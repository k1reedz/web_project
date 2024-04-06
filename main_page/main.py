from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from data import db_session
from data.users import User
from data.goals import Goal
from datetime import datetime
import requests
from data import goals_api
from data import tasks_api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user_form import RegisterForm, LoginForm
from forms.goal_form import GoalForm


app = Flask(__name__)
address = "http://127.0.0.1:5000"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(goals_api.blueprint)
app.register_blueprint(tasks_api.blueprint)
login_manager = LoginManager()
login_manager.init_app(app)


# Главная страница
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким email уже существует")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/goals")
def render_goals():
    if not current_user.is_authenticated:
        return redirect("/login")
    goals = requests.get(f"{address}/api/goals/{str(current_user.id)}")
    if goals.status_code == 200:
        goals = goals.json()["goals"]
    else:
        goals = []
    return render_template("goals.html", goals=goals)


@app.route("/add_goal", methods=["POST", "GET"])
def add_goal():
    if not current_user.is_authenticated:
        return redirect("/login")
    form = GoalForm()
    if form.validate_on_submit():
        data = {
            "title": form.title.data,
            "description": form.description.data,
            "priority": form.priority.data,
            "finish_date": form.finish_date.data,
            "user_id": current_user.id,
            "accomplished": False
        }
        print(requests.post(f"{address}/api/add_goal/", json=jsonify(data).json))
        return redirect('/goals')
    return render_template("goal_form.html", form=form)


@app.route("/delete_goal/<int:goal_id>", methods=["DELETE", "POST", "GET"])
def delete_goal(goal_id):
    requests.delete(f"{address}/api/goal/{str(goal_id)}")
    return redirect('/goals')


@app.route("/done_goals", methods=["GET"])
def render_done_goals():
    if not current_user.is_authenticated:
        return redirect("/login")
    goals = requests.get(f"{address}/api/done_goals/{str(current_user.id)}")
    if goals.status_code == 200:
        goals = goals.json()["goals"]
    else:
        goals = []
    return render_template("done_goals.html", goals=goals)


@app.route("/finish_goal/<int:goal_id>", methods=["PUT", "GET"])
def done_goal(goal_id):
    print(requests.put(f"{address}/api/goal/{str(goal_id)}", json=jsonify({"accomplished": True, "finish_date":
                                                                          datetime.now().date().strftime("%d.%m.%Y")}).json))
    return redirect("/done_goals")


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
