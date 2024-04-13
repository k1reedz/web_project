import sqlite3

from flask import Flask, render_template, request, redirect, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from data.activity import Activity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
engine = create_engine("sqlite:///db/activity.db")
weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')
week = []
current_day = date.today()
timedelta_value = 0


def main():
    app.run()


@app.route("/activities", methods=['POST', 'GET'])
def activities():
    global week
    global current_day
    current_day = date.today() + timedelta(days=timedelta_value)
    today_weekday = current_day.weekday()  # промежуток дней между понедельником и текущим днем
    week = []   # даты всех дней на текущей неделе
    for i in range(7):
        week.append(current_day + timedelta(days=i - today_weekday))
    session = Session(bind=engine)
    week_activities = []
    for j in range(7):
        week_activities.append(session.query(Activity).filter(Activity.date.like(f'{week[j]}%')).order_by(
            Activity.start, Activity.end).all())
    session.close()
    return render_template('activities.html', weekdays=weekdays, week=week, week_activities=week_activities)


@app.route("/adding_a_training/<date>", methods=['POST', 'GET'])
def adding_a_training(date):
    global week
    if request.method == "POST":
        title = request.form['title']
        type = request.form['type']
        start = request.form['start']
        end = request.form['end']
        if bool(title) and bool(start) and bool(end):
            try:
                print(date)
                date = datetime.strptime(date, "%Y-%m-%d")
                print(date)
                session = Session(bind=engine)
                training = Activity(title=title,
                                    type=type,
                                    start=start,
                                    end=end,
                                    date=date)
                session.add(training)
                session.commit()
                return redirect("/activities")
            except:
                abort(404)
        else:
            return render_template("adding_a_training.html", inf='Заполните все поля', page_title='Добавить ',
                                   title_text=title, start_text=start, end_text=end,
                                   type_text=type)
    return render_template('adding_a_training.html', weekdays=weekdays, page_title='Добавить ')


@app.route('/activities_change/<int:id>', methods=['POST', 'GET'])
def activities_change(id):
    if request.method == "POST":
        title = request.form['title']
        type = request.form['type']
        start = request.form['start']
        end = request.form['end']

        if bool(title) and bool(start) and bool(end):
            try:
                session = Session(bind=engine)
                training = session.query(Activity).get(id)
                training.title = title
                training.type = type
                training.start = start
                training.end = end
                session.add(training)
                session.commit()
                return redirect("/activities")
            except:
                abort(404)
        else:
            return render_template("adding_a_training.html", inf='Заполните все поля',
                                   page_title='Изменить ', title_text=title, start_text=start, end_text=end,
                                   type_text=type)
    else:
        return render_template('adding_a_training.html', weekdays=weekdays, page_title='Изменить ')


@app.route('/activities_delete/<int:id>', methods=['GET', 'POST'])
def activities_delete(id):
    session = Session(bind=engine)
    training = session.query(Activity).get(id)
    if training:
        session.delete(training)
        session.commit()
    else:
        abort(404)
    return redirect('/activities')


@app.route('/activities_previous')
def previous():
    global timedelta_value
    timedelta_value -= 7
    return redirect('/activities')


@app.route('/activities_next')
def next():
    global timedelta_value
    timedelta_value += 7
    return redirect('/activities')


if __name__ == '__main__':
    main()
