import flask
from flask import jsonify, make_response, request
from . import db_session
from datetime import datetime
from .tasks import Task


blueprint = flask.Blueprint(
    'tasks_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/tasks', methods=['GET'])
def get_tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Task).all()
    if not tasks:
        return make_response(jsonify({"error": "Not found"}), 404)
    return jsonify(
        {
            'tasks': [item.to_dict() for item in tasks]
        }
    )


@blueprint.route("/api/tasks/<int:user_id>", methods=['GET'])
def get_tasks_by_id(user_id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Task).filter(Task.user_id == user_id).all()
    if not tasks:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'tasks': [item.to_dict() for item in tasks]
        }
    )


@blueprint.route("/api/task/<int:task_id>", methods=["GET"])
def get_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()
    if not task:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            "tasks": [task.to_dict(), ]
        }
    )


@blueprint.route("/api/tasks_weekday/<int:user_id>", methods=["GET"])
def get_weekday_tasks(user_id):
    tasks = get_tasks_by_id(user_id)
    if tasks.status_code == 404:
        return make_response(jsonify({'error': 'Not found'}), 404)
    result = {}
    for task in tasks["tasks"]:
        result[task["weekday"]] = result.get(task["weekday"], []) + [task]
    return result


@blueprint.route("/api/task", methods=["GET", "POST"])
def add_task():
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    if not all(item in request.json for item in ["task_name", "user_id", "start", "end",
                                                 "weekday"]):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    other_tasks = get_tasks_by_id(request.json["user_id"])
    if other_tasks.status_code != 404:
        try:
            start1, end1 = datetime.strptime(request.json["start"], "%H:%M"), \
                                   datetime.strptime(request.json["end"], "%H:%M")
        except ValueError:
            return make_response(jsonify({"error": "Time format error"}), 400)
        for task in other_tasks:
            start2, end2 = task["start"], task["end"]
            if start2 <= start1 < end2 or start2 < end1 <= end2:
                return make_response(jsonify({"error": "Time span is busy"}), 400)

    db_sess = db_session.create_session()
    task = Task(
        task_name=request.json["task_name"],
        user_id=request.json["user_id"],
        start=request.json["start"].time(),
        end=request.json["end"].time(),
        weekday=request.json["weekday"]
    )
    db_sess.add(task)
    db_sess.commit()
    return jsonify({"id": task.id})


@blueprint.route("/api/goal/<int:task_id>", methods=["DELETE"])
def delete_goal(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()
    if not task:
        return make_response(jsonify({"error": "Not found"}), 404)
    db_sess.delete(task)
    db_sess.commit()
    return jsonify({'success': 'OK'})