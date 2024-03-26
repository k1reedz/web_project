import flask
from flask import jsonify, make_response, request
from . import db_session
from datetime import datetime
from .goals import Goal


blueprint = flask.Blueprint(
    'goals_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/goals', methods=['GET'])
def get_goals():
    db_sess = db_session.create_session()
    goals = db_sess.query(Goal).all()
    return jsonify(
        {
            'goals': [item.to_dict() for item in goals]
        }
    )


@blueprint.route("/api/goals/<int:user_id>", methods=['GET'])
def get_goals_by_id(user_id):
    db_sess = db_session.create_session()
    goals = db_sess.query(Goal).filter(Goal.user_id == user_id).fetchall()
    if not goals:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'goals': [item.to_dict() for item in goals]
        }
    )


@blueprint.route("/api/goal/<int:goal_id>", methods=["GET"])
def get_goal(goal_id):
    db_sess = db_session.create_session()
    goal = db_sess.query(Goal).filter().first()
    if not goal:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            "goal": goal.to_dict()
        }
    )


@blueprint.route("/api/goals/", methods=["POST"])
def add_goal():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    if not all(item in request.json for item in ["title", "user_id", "priority", "description", "finish_date"]):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    try:
        data = datetime.strptime(request.json["finish_date"], "%Y.%m.%d")
    except ValueError:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    goal = Goal(
        title=request.json["title"],
        user_id=request.json["user_id"],
        priority=request.json["priority"],
        description=request.json["description"],
        finish_date=data
    )
    db_sess.add(goal)
    db_sess.commit()
    return jsonify({"id": goal.id})


@blueprint.route("/api/goal/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    db_sess = db_session.create_session()
    goal = db_sess.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        return make_response(jsonify({"error": "Not found"}), 404)
    db_sess.delete(goal)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/goal/<int:goal_id>", methods=["POST"])
def edit_goal(goal_id):
    db_sess = db_session.create_session()
    goal = db_sess.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        return make_response(jsonify({"error": "Not found"}), 404)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    data = None
    if "finish_date" in request.json:
        try:
            data = datetime.strptime(request.json["finish_date"], "%Y.%m.%d")
        except ValueError:
            return make_response(jsonify({'error': 'Bad request'}), 400)

    goal.title = request.json["title"] if "title" in request.json else goal.title
    goal.user_id = request.json["user_id"] if "user_id" in request.json else goal.user_id
    goal.priority = request.json["priority"] if "priority" in request.json else goal.priority
    goal.description = request.json["description"] if "description" in request.json else goal.description
    goal.finish_date = data if data is not None else goal.finish_date
