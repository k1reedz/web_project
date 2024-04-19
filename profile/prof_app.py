import secrets
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from PIL import Image


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Конфигурация базы данных
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для защиты приложения
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для загрузки изображений профиля

db = SQLAlchemy(app)  # Инициализация базы данных


class User(db.Model):
    # Модель данных пользователя
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height = db.Column(db.Integer)  # Поле роста пользователя
    about_me = db.Column(db.Text)  # Поле "О себе"
    profile_image = db.Column(db.String(100), nullable=False, default='default.jpg')  # Путь к изображению профиля


def save_picture(form_picture):
    # Функция сохранения изображения профиля
    random_hex = secrets.token_hex(8)  # Генерация случайного имени файла
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)

    # Открытие изображения с использованием PIL
    i = Image.open(form_picture)
    # Вырезаем изображение в квадрат
    min_dimension = min(i.width, i.height)
    crop_area = (
        (i.width - min_dimension) // 2,
        (i.height - min_dimension) // 2,
        (i.width + min_dimension) // 2,
        (i.height + min_dimension) // 2
    )
    i = i.crop(crop_area)
    # Изменение размера до 200x200
    output_size = (200, 200)
    i = i.resize(output_size, Image.LANCZOS)  # Используем метод интерполяции LANCZOS для сохранения качества
    # Сохраняем изображение
    i.save(picture_path)

    return picture_fn


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


if __name__ == '__main__':
    app.run(debug=True)