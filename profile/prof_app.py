from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)


from models.models import User


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form['username']
        email = request.form['email']
        age = request.form['age']
        profile_image = 'default.jpg'

        # Проверяем, загружено ли изображение
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_image = filename

        # Создаем нового пользователя
        new_user = User(username=username, email=email, age=age, profile_image=profile_image)

        # Добавляем пользователя в базу данных
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)