from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float)
    water = db.Column(db.Float)
    activity = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    mental = db.Column(db.Integer)
    steps = db.Column(db.Integer)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    weight = request.form.get('weight')
    activity = request.form.get('activity')
    heart_rate = request.form.get('heart-rate')
    mental = request.form.get('mental', 0)
    steps = request.form.get('steps', 0)
    water = request.form.get('water')

    new_data = HealthData(weight=weight, mental=mental, activity=activity,
                          heart_rate=heart_rate, steps=steps, water=water)
    db.session.add(new_data)
    db.session.commit()

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)