import os
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем Agg для работы без GUI
import matplotlib.pyplot as plt
import secrets
from PIL import Image
from werkzeug.utils import secure_filename

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Конфигурируем базу данных SQLite для приложения здоровья
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Конфигурируем базу данных SQLite для приложения профиля
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для защиты приложения
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для загрузки изображений профиля


# Определяем модель данных для таблицы в базе данных здоровья
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    water = db.Column(db.Float)
    activity = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    mental = db.Column(db.Integer)
    steps = db.Column(db.Integer)


# Определяем модель данных для таблицы в базе данных профиля
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Integer)
    about_me = db.Column(db.Text)
    profile_image = db.Column(db.String(100), nullable=False, default='default.jpg')


# Создаем таблицы в базах данных, если они не существуют
with app.app_context():
    db.create_all()


# Функция для получения данных из базы данных здоровья
def get_data_from_db():
    weight_data = np.array([d.weight for d in HealthData.query.all() if d.weight is not None])
    water_data = np.array([d.water for d in HealthData.query.all() if d.water is not None])
    activity_data = np.array([d.activity for d in HealthData.query.all() if d.activity is not None])
    heart_rate_data = np.array([d.heart_rate for d in HealthData.query.all() if d.heart_rate is not None])
    mental_data = np.array([d.mental for d in HealthData.query.all() if d.mental is not None])
    steps_data = np.array([d.steps for d in HealthData.query.all() if d.steps is not None])
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Показывает профиль пользователя
    user = User.query.first()
    if user is None:
        # Если пользователь не найден, создаем нового пользователя
        user = User(username='Default User', email='default@example.com')
        db.session.add(user)
        db.session.commit()
    if request.method == 'POST':
        # Обработка запроса на обновление профиля
        user.username = request.form['username']
        user.email = request.form['email']
        user.age = request.form['age']
        user.gender = request.form['gender']
        user.height = request.form['height']
        user.about_me = request.form['about_me']

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename != '':
                # Удаляем предыдущее изображение, если оно не является изображением по умолчанию
                if user.profile_image != 'default.jpg':
                    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image)):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image))
                # Сохраняем новое изображение профиля
                user.profile_image = save_picture(file)

        db.session.commit()  # Сохраняем изменения в базе данных
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    # Обновляет профиль пользователя
    user_id = request.form['user_id']
    username = request.form['username']
    email = request.form['email']
    age = request.form['age']
    gender = request.form.get('gender', '')
    height = request.form.get('height', '')
    about_me = request.form.get('about_me', '')
    profile_image = request.files['profile_image'] if 'profile_image' in request.files else None

    # Находим пользователя по ID
    user = User.query.get(user_id)
    if user:
        # Удаляем предыдущее изображение, если оно существует и не является изображением по умолчанию
        if user.profile_image != 'default.jpg':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image))

        # Сохраняем предыдущее имя файла изображения профиля
        previous_profile_image = user.profile_image

        # Обновляем данные пользователя
        user.username = username
        user.email = email
        user.age = age
        user.gender = gender
        user.height = height
        user.about_me = about_me

        # Проверяем, загружено ли новое изображение профиля
        if profile_image:
            # Сохраняем новое изображение профиля
            filename = save_picture(profile_image)
            user.profile_image = filename

        # Сохраняем обновленные данные пользователя в базе данных
        db.session.commit()

    return redirect(url_for('profile'))


# Определяем маршрут для отображения главной страницы
@app.route('/health')
def index():
    return render_template('index.html')


# Определяем маршрут для обработки отправленной формы
@app.route('/submit', methods=['POST'])
def submit():
    # Получение данных из формы
    weight = request.form.get('weight', type=float)
    water = request.form.get('water', type=float)
    activity = request.form.get('activity', type=int)
    heart_rate = request.form.get('heart_rate', type=int)
    mental = request.form.get('mental', type=int)
    steps = request.form.get('steps', type=int)

    # Создание нового объекта данных и добавление его в базу данных
    new_data = HealthData(weight=weight, water=water, activity=activity,
                          heart_rate=heart_rate, mental=mental, steps=steps)
    db.session.add(new_data)
    db.session.commit()

    # Повторное получение данных и генерация графиков
    weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data = get_data_from_db()
    plot_file = generate_plots(weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data)

    return render_template('index.html', image_file=plot_file)


@app.route('/advice')
def advice():
    health_data = HealthData.query.first()  # Получаем первую запись из базы данных
    advice = generate_advice(health_data)  # Генерируем советы на основе данных
    return render_template('advices.html', advice=advice)


def generate_advice(health_data):
    advice = []
    if health_data.steps < 500:
        advice.append("Увеличьте количество шагов в течение дня.")
    if health_data.weight < 60 or health_data.weight > 130:  # Пример значения, которое считается низким
        advice.append("Обратите внимание на свой вес и питание.")
    if health_data.mental >= 8:  # Пример значения, которое считается высоким уровнем стресса
        advice.append("Постарайтесь уменьшить уровень стресса, возможно, стоит обратиться к специалисту.")
    if health_data.water < 2:  # Пример значения, которое считается низким количеством выпитой воды
        advice.append("Не забывайте употреблять достаточное количество воды в течение дня.")
    return advice


if __name__ == '__main__':
    app.run(debug=True)