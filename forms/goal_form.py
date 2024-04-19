from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import SubmitField, EmailField, StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

now = datetime.now()

class GoalForm(FlaskForm):
    title = StringField('Цель', validators=[DataRequired()])
    description = StringField('Описание', default="Отстутствует")
    priority = IntegerField('Приоритет', default=0)
    finish_date = StringField("Дата ожидаемого выполнения", default=f"{now.day}.{now.month}.{now.year}")
    submit = SubmitField('Подтвердить')