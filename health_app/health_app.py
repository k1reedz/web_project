# Импортируем необходимые модули
import os
import time
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем Agg для работы без GUI
import matplotlib.pyplot as plt

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Конфигурируем базу данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Определяем модель данных для таблицы в базе данных
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    water = db.Column(db.Float)
    activity = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    mental = db.Column(db.Integer)
    steps = db.Column(db.Integer)


# Создаем таблицу в базе данных, если она не существует
with app.app_context():
    db.create_all()


# Функция для получения данных из базы данных
def get_data_from_db():
    weight_data = np.array([d.weight for d in HealthData.query.all() if d.weight is not None])
    water_data = np.array([d.water for d in HealthData.query.all() if d.water is not None])
    activity_data = np.array([d.activity for d in HealthData.query.all() if d.activity is not None])
    heart_rate_data = np.array([d.heart_rate for d in HealthData.query.all() if d.heart_rate is not None])
    mental_data = np.array([d.mental for d in HealthData.query.all() if d.mental is not None])
    steps_data = np.array([d.steps for d in HealthData.query.all() if d.steps is not None])

    return weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data


# Функция для генерации графиков
def generate_plots(weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data):
    plt.figure(figsize=(18, 10))  # Устанавливаем размер области построения

    # Заголовки для графиков
    titles = ['Вес (кг)', 'Потребление воды (л)', 'Активность', 'Сердцебиение', 'Уровень стресса', 'Пройденные шаги']
    data_arrays = [weight_data, water_data, activity_data, heart_rate_data, mental_data, steps_data]

    # Цвета линий и маркеров для разных графиков
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    for i, data in enumerate(data_arrays):
        plt.subplot(2, 3, i + 1)  # Создаем подграфик
        plt.plot(range(1, len(data) + 1), data, marker='o',
                 color=colors[i])  # Строим график с заданным цветом и отсчётом с 1
        plt.title(titles[i], fontsize=16, color='black')  # Устанавливаем заголовок с нужными параметрами
        plt.xlabel('Измерение', fontsize=12, color='black')  # Устанавливаем подпись по x
        plt.ylabel(titles[i], fontsize=12, color='black')  # Устанавливаем подпись по y
        plt.xticks(color='black')  # Устанавливаем цвет делений по x
        plt.yticks(color='black')  # Устанавливаем цвет делений по y

    plt.tight_layout()  # Автоматически подгоняем размеры подложек
    timestamp = int(time.time())  # Получаем текущий timestamp
    plot_file = f'static/plots_{timestamp}.png'  # Формируем уникальное имя файла

    # Удаляем предыдущие графики
    for filename in os.listdir('./static/'):
        if filename.startswith('plots_'):
            os.remove(os.path.join('./static/', filename))

    plt.savefig(plot_file)  # Сохраняем текущий график
    plt.close()  # Закрываем текущее изображение

    return plot_file


# Определяем маршрут для отображения главной страницы
@app.route('/')
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


# Запускаем приложение Flask при выполнении скрипта
if __name__ == '__main__':
    app.run(debug=True)