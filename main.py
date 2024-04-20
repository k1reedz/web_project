from flask import Flask, render_template, redirect, make_response, jsonify, request, url_for, flash
from data import db_session  # Импорт модуля для работы с базой данных
from data.users import User  # Импорт модели пользователя
from sqlalchemy import orm, desc  # Импорт функций для работы с базой данных
from datetime import datetime  # Импорт модуля для работы с датами и временем
from data.health import Health  # Импорт модели здоровья
import requests  # Импорт модуля для отправки HTTP-запросов
from data import goals_api  # Импорт API для работы с целями
from data import tasks_api  # Импорт API для работы с задачами
from flask_login import LoginManager, login_user, login_required, logout_user, current_user  # Импорт модуля для аутентификации пользователей
from forms.user_form import RegisterForm, LoginForm  # Импорт форм для регистрации и входа
from forms.goal_form import GoalForm  # Импорт формы для целей
from forms.task_form import TaskForm  # Импорт формы для задач
import os  # Импорт модуля для работы с операционной системой
import time  # Импорт модуля для работы со временем
from flask_sqlalchemy import SQLAlchemy  # Импорт модуля для работы с базой данных SQLAlchemy
from flask_migrate import Migrate  # Импорт модуля для миграции базы данных
import numpy as np  # Импорт модуля для работы с массивами
import matplotlib  # Импорт модуля для построения графиков
import matplotlib.pyplot as plt  # Импорт функций для построения графиков
import secrets  # Импорт модуля для генерации безопасных случайных чисел
from PIL import Image  # Импорт модуля для работы с изображениями

matplotlib.use('Agg')  # Используем Agg для работы без GUI

app = Flask(__name__)  # Создание экземпляра приложения Flask
address = "http://127.0.0.1:5000"  # Адрес API
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # Установка секретного ключа для безопасности приложения
app.register_blueprint(goals_api.blueprint)  # Регистрация Blueprint для работы с целями
app.register_blueprint(tasks_api.blueprint)  # Регистрация Blueprint для работы с задачами
login_manager = LoginManager()  # Создание объекта для управления аутентификацией пользователей
login_manager.init_app(app)  # Инициализация аутентификации в приложении
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Установка URI для базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений базы данных
db = SQLAlchemy(app)  # Создание объекта для работы с базой данных SQLAlchemy
migrate = Migrate(app, db)  # Создание объекта для миграции базы данных
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для загрузки изображений профиля

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# Регистрация нового пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/profile")
    form = RegisterForm()
    if form.validate_on_submit():
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        # Создание нового пользователя и сохранение его в базе данных
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким email уже существует")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            stats={"gender": "", "height": 0, "profile_image": ".jpg", "age": "", "about": ""},
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

# Вход пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/profile")
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Проверка соответствия email и пароля
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

# Выход пользователя
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# Загрузка пользователя при аутентификации
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()

# Обработчик ошибки 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Обработчик ошибки 400
@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

# Отображение списка целей пользователя
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

# Добавление новой цели пользователя
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
        requests.post(f"{address}/api/add_goal/", json=jsonify(data).json)
        return redirect('/goals')
    return render_template("goal_form.html", form=form)

# Удаление цели пользователя
@app.route("/delete_goal/<int:goal_id>", methods=["DELETE", "POST", "GET"])
def delete_goal(goal_id):
    requests.delete(f"{address}/api/goal/{str(goal_id)}")
    return redirect('/goals')

# Отображение выполненных целей пользователя
@app.route("/done_goals", methods=["GET"])
def render_done_goals():
    if not current_user.is_authenticated:
        return redirect("/login")
    goals_response = requests.get(f"{address}/api/done_goals/{str(current_user.id)}")
    if goals_response.status_code == 200:
        goals_data = goals_response.json()
        goals = goals_data["goals"]
        # Обновляем формат даты выполнения в каждой цели
        for goal in goals:
            # Преобразуем строку времени выполнения в объект datetime
            finish_date = datetime.strptime(goal["finish_date"], "%Y-%m-%d %H:%M:%S")
            # Форматируем дату и время с учетом формата, используемого в вашем приложении
            goal["finish_date"] = finish_date.strftime("%d.%m.%Y %H:%M:%S")
    else:
        goals = []
    return render_template("done_goals.html", goals=goals)

# Пометка цели как выполненной
@app.route("/finish_goal/<int:goal_id>", methods=["PUT", "GET"])
def done_goal(goal_id):
    requests.put(f"{address}/api/goal/{str(goal_id)}", json=jsonify({"accomplished": True, "finish_date":
                                                                          datetime.now().date().strftime("%d.%m.%Y")}).json)
    return redirect("/done_goals")

# Отображение расписания пользователя
@app.route("/schedule", methods=["GET", "POST"])
def render_schedule():
    if not current_user.is_authenticated:
        return redirect("/login")
    tasks = requests.get(f"{address}/api/tasks_weekday/{str(current_user.id)}")
    if tasks.status_code != 200:
        tasks = dict()
    else:
        tasks = tasks.json()
    form = TaskForm()
    if form.validate_on_submit():
        data = {
            "task_name": form.name.data,
            "weekday": form.weekday.data,
            "start": form.start_time.data,
            "end": form.end_time.data,
            "user_id": current_user.id,
        }
        response = requests.post(f"{address}/api/task", json=jsonify(data).json)
        if response.status_code != 200:
            error_type = response.json()["error"]
            if error_type == "Time format error":
                message = "Неправильный формат времени"
            elif error_type == "Time span is busy":
                message = "Промежуток времени уже занят"
            else:
                message = "Ошибка"
        else:
            message = "Событие успешно добавлено"
    else:
        message = ""
    return render_template("schedule.html", form=form, tasks=tasks, message=message)

# Удаление задачи пользователя
@app.route("/delete_task/<int:task_id>", methods=["DELETE", "GET"])
def delete_task(task_id):
    requests.delete(f"{address}/api/task/{str(task_id)}")
    return redirect('/schedule')

# Создание таблиц в базах данных, если они не существуют
with app.app_context():
    db.create_all()

# Функция для получения данных из базы данных здоровья
def get_data_from_db():
    db_sess = db_session.create_session()
    data = db_sess.query(Health).filter(Health.user_id == current_user.id).all()
    weight_data = np.array([d.weight for d in data if d.weight is not None])
    water_data = np.array([d.water for d in data if d.water is not None])
    activity_data = np.array([d.activity for d in data if d.activity is not None])
    heart_rate_data = np.array([d.heart_rate for d in data if d.heart_rate is not None])
    mental_data = np.array([d.mental for d in data if d.mental is not None])
    steps_data = np.array([d.steps for d in data if d.steps is not None])
    db_sess.close()
    return weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data

# Функция для сохранения изображения профиля
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)
    i = Image.open(form_picture)
    min_dimension = min(i.width, i.height)
    crop_area = (
        (i.width - min_dimension) // 2,
        (i.height - min_dimension) // 2,
        (i.width + min_dimension) // 2,
        (i.height + min_dimension) // 2
    )
    i = i.crop(crop_area)
    output_size = (200, 200)
    i = i.resize(output_size, Image.LANCZOS)
    i.save(picture_path)
    return picture_fn

# Функция для генерации графиков
def generate_plots(weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data):
    plt.figure(figsize=(18, 10))
    titles = ['Вес (кг)', 'Потребление воды (л)', 'Активность', 'Сердцебиение', 'Уровень стресса', 'Пройденные шаги']
    data_arrays = [weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for i, data in enumerate(data_arrays):
        plt.subplot(2, 3, i + 1)
        plt.plot(range(1, len(data) + 1), data, marker='o', color=colors[i])
        plt.title(titles[i], fontsize=16, color='black')
        plt.xlabel('Измерение', fontsize=12, color='black')
        plt.ylabel(titles[i], fontsize=12, color='black')
        plt.xticks(color='black')
        plt.yticks(color='black')
    plt.tight_layout()
    timestamp = int(time.time())
    plot_file = f'static/plots_{timestamp}.png'
    for filename in os.listdir('./static/'):
        if filename.startswith('plots_'):
            os.remove(os.path.join('./static/', filename))
    plt.savefig(plot_file)
    plt.close()
    return plot_file

# Отображение профиля пользователя
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect("/")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if request.method == 'POST':
        try:
            # Обновление профиля пользователя
            user.name = request.form['username']
            user.email = request.form['email']
            user.stats["age"] = request.form['age']
            user.stats["gender"] = request.form['gender']
            user.stats["height"] = request.form['height']
            user.stats["about"] = request.form['about_me']
            if 'profile_image' in request.files:
                # Обновление изображения профиля, если оно загружено
                file = request.files['profile_image']
                if file.filename != '':
                    user.stats["profile_image"] = save_picture(file)
            orm.attributes.flag_modified(user, 'stats')
            db_sess.commit()
            login_user(user)
            return redirect(url_for('profile'))
        except Exception as e:
            # Обработка исключений, таких как ошибки валидации или ошибки базы данных
            db_sess.rollback()
            flash("An error occurred while updating the profile.", "error")
    db_sess.close()
    return render_template('profile.html', user=user)

# Обновление профиля пользователя
@app.route('/update_profile', methods=['POST', 'GET'])
def update_profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        age = request.form['age']
        gender = request.form.get('gender', '')
        height = request.form.get('height', '')
        about_me = request.form.get('about_me', '')
        profile_image = request.files['profile_image'] if 'profile_image' in request.files else None
        user = User.query.get(current_user.id)
        if user:
            if user.profile_image != 'default.jpg':
                os.remove(os.path.join(app.root_path, 'static/uploads', user.profile_image))
            user.name = username
            user.email = email
            user.stats["age"] = age
            user.stats["gender"] = gender
            user.stats["height"] = height
            user.stats["about"] = about_me
            if profile_image:
                filename = save_picture(profile_image)
                user.stats["profile_image"] = filename
            db.session.commit()
            return redirect(url_for('profile'))
    return render_template('update_profile.html')

# Отображение страницы здоровья
@app.route('/health')
def health():
    return render_template('health.html')

# Обработка данных, отправленных формой
@app.route('/submit', methods=['POST'])
def submit():
    db_sess = db_session.create_session()
    weight = request.form.get('weight', type=float)
    water = request.form.get('water', type=float)
    activity = request.form.get('activity', type=int)
    heart_rate = request.form.get('heart_rate', type=int)
    mental = request.form.get('mental', type=int)
    steps = request.form.get('steps', type=int)
    new_data = Health(weight=weight, water=water, activity=activity,
                          heart_rate=heart_rate, mental=mental, steps=steps, user_id=current_user.id)
    db_sess.add(new_data)
    db_sess.commit()
    db_sess.close()
    weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data = get_data_from_db()
    plot_file = generate_plots(weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data)
    return render_template('health.html', image_file=plot_file)

# Получение последних данных о здоровье пользователя
def get_latest_health_data(user_id):
    db_sess = db_session.create_session()
    latest_health_data = db_sess.query(Health).filter(Health.user_id == user_id).order_by(desc(Health.id)).all()
    latest_date = latest_health_data[0]
    db_sess.close()
    return latest_health_data

# Отображение советов по здоровью
@app.route("/advice")
def advice():
    latest_health_data = get_latest_health_data(current_user.id)
    if latest_health_data:
        latest_health_entry = latest_health_data[0]
        advices = generate_advice(latest_health_entry)
    else:
        advices = []
    return render_template('advices.html', advices=advices)

# Генерация советов по здоровью на основе последних данных о здоровье
def generate_advice(latest_health_entry):
    advices = []
    if latest_health_entry.weight:
        weight = latest_health_entry.weight
        if weight < 50:
            advices.append("Ваш вес ниже нормы. Рекомендуется обратиться к врачу.")
        elif weight > 100:
            advices.append("Ваш вес выше нормы. Рекомендуется обратить внимание на режим питания.")
    if latest_health_entry.heart_rate:
        heart_rate = latest_health_entry.heart_rate
        if heart_rate > 100:
            advices.append("Ваш пульс выше нормы. Рекомендуется уменьшить физическую активность.")
    if latest_health_entry.mental:
        mental = latest_health_entry.mental
        if mental > 7:
            advices.append("Уровень стресса выше нормы. Рекомендуется принять меры по его снижению.")
    return advices

# Запуск приложения
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
