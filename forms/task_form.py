from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    name = StringField('Событие', validators=[DataRequired()])
    weekday = SelectField('День недели', choices=[("Понедельник", "Понедельник"), ("Вторник", "Вторник"),
                                                  ("Среда", "Среда"), ("Четверг", "Четверг"), ("Пятница", "Пятница")
                                                  , ("Суббота", "Суббота"), ("Воскресенье", "Воскресенье")], validators=[DataRequired()])
    start_time = StringField("Время начала", default="00:00", validators=[DataRequired()])
    end_time = StringField("Время окончания", default="23:59", validators=[DataRequired()])
    submit = SubmitField('Добавить')