import sqlite3

from flask import Flask, render_template, request, redirect, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from data.activity import Activity
from data.ration import Ration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
engine = create_engine("sqlite:///db/activity.db")
weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')
week = []
current_day = date.today()
timedelta_value = 0
current_user_id = 1
engine2 = create_engine("sqlite:///db/ration.db")
con = sqlite3.connect('db/products.db')
cur = con.cursor()
all_products = cur.execute('''SELECT name FROM products''').fetchall()
products_list = []
for i in all_products:
    products_list.append(i[0])
con.close()


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
        week_activities.append(session.query(Activity).filter(Activity.date.like(f'{week[j]}%'),
                                                              Activity.user_id == current_user_id).order_by(
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
        if bool(title) and datetime.strptime(start, "%H:%M") < datetime.strptime(end, "%H:%M"):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
                session = Session(bind=engine)
                training = Activity(title=title,
                                    type=type,
                                    start=start,
                                    end=end,
                                    date=date,
                                    user_id=current_user_id)
                session.add(training)
                session.commit()
                return redirect("/activities")
            except:
                abort(404)
        else:
            return render_template("adding_a_training.html", inf='Ошибка', page_title='Добавить ',
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

        if bool(title) and datetime.strptime(start, "%H:%M") < datetime.strptime(end, "%H:%M"):
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
            return render_template("adding_a_training.html", inf='Ошибка',
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


def get_kpfc(product):
    con = sqlite3.connect('db/products.db')
    cur = con.cursor()
    get_kpfc = cur.execute('''SELECT kcal, proteins, fats, carbohydrates FROM products
    WHERE name = ?''', (product,)).fetchone()
    con.close()
    return get_kpfc[0], get_kpfc[1], get_kpfc[2], get_kpfc[3]


@app.route("/diet", methods=['POST', 'GET'])
def diet():
    if request.method == 'POST':
        current_date = request.form['input_date']
    else:
        current_date = date.today()
    session = Session(bind=engine2)
    products = session.query(Ration).filter(Ration.created_date.like(f'{current_date}%'),
                                            Ration.user_id == current_user_id).all()
    sum_kcal, sum_proteins, sum_fats, sum_carbohydrates = float(), float(), float(), float()
    for item in products:
        sum_kcal += float(item.total_kcal)
        sum_proteins += float(item.total_proteins)
        sum_fats += float(item.total_fats)
        sum_carbohydrates += float(item.total_carbohydrates)
    session.close()
    return render_template("diet.html", products=products, today=date.today(), current_date=current_date,
                           sum_kcal=sum_kcal, sum_proteins=sum_proteins, sum_fats=sum_fats,
                           sum_carbohydrates=sum_carbohydrates)


@app.route("/diet/adding_a_product", methods=["POST", "GET"])
def adding_a_product():
    if request.method == "POST":
        title = request.form['title']
        weight = request.form['weight']

        if title not in products_list:
            return render_template("diet_change.html", products_list=products_list,
                                   inf='Продукт не найден', title_text='Добавить', weight_text=weight)
        if bool(title) and bool(weight):
            try:
                session = Session(bind=engine2)
                kcal, proteins, fats, carbohydrates = get_kpfc(title)
                if session.query(Ration).filter(Ration.title == title,
                                                Ration.created_date == date.today()).count() == 0:
                    product = Ration(title=title, weight=round(float(weight), 1),
                                     total_kcal=str(round(float(kcal) * float(weight) / 100, 1)),
                                     total_proteins=str(round(float(proteins) * float(weight) / 100, 1)),
                                     total_fats=str(round(float(fats) * float(weight) / 100, 1)),
                                     total_carbohydrates=str(round(float(carbohydrates) * float(weight) / 100, 1)),
                                     created_date=date.today(),
                                     user_id=current_user_id)
                    session.add(product)
                    session.commit()
                else:
                    product = session.query(Ration).filter(Ration.title == title,
                                                           Ration.created_date == date.today()).first()
                    product.weight = str(round(product.weight + float(weight), 1))
                    product.total_kcal = str(round(float(product.total_kcal) + float(kcal) * float(weight) / 100, 1))
                    product.total_proteins = str(round(float(product.total_proteins) + float(proteins) * float(weight)
                                                       / 100, 1))
                    product.total_fats = str(round(float(product.total_fats) + float(fats) * float(weight) / 100, 1))
                    product.total_carbohydrates = str(round(float(product.total_carbohydrates) +
                                                            float(carbohydrates) * float(weight) / 100, 1))
                    session.add(product)
                    session.commit()
                return redirect("/diet")
            except:
                abort(404)
        else:
            return render_template("diet_change.html", products_list=products_list,
                                   inf='Заполните все поля', title_text='Добавить', weight_text=weight)
    else:
        return render_template("diet_change.html", products_list=products_list, title_text='Добавить')


@app.route('/diet_change/<int:id>', methods=['GET', 'POST'])
def diet_change(id):
    if request.method == "POST":
        title = request.form['title']
        weight = request.form['weight']

        if bool(title) and bool(weight):
            if title not in products_list:
                return render_template("diet_change.html", products_list=products_list,
                                       inf='Продукт не найден', title_text=title, weight_text=weight)
            try:
                session = Session(bind=engine2)
                product = session.query(Ration).get(id)
                kcal, proteins, fats, carbohydrates = get_kpfc(title)
                product.title = title
                product.weight = weight
                product.total_kcal = str(round(float(product.total_kcal) + float(kcal) * float(weight) / 100))
                product.total_proteins = str(round(float(product.total_proteins) + float(proteins) * float(weight)
                                                   / 100))
                product.total_fats = str(round(float(product.total_fats) + float(fats) * float(weight) / 100))
                product.total_carbohydrates = str(round(float(product.total_carbohydrates) + float(carbohydrates) *
                                                  float(weight) / 100))
                session.add(product)
                session.commit()
                return redirect("/diet")
            except:
                abort(404)
        else:
            return render_template("diet_change.html", products_list=products_list, inf='Заполните все поля',
                                   title_text='Изменить', weight_text=weight)
    else:
        return render_template("diet_change.html", products_list=products_list, title_text='Изменить')


@app.route('/diet_delete/<int:id>', methods=['GET', 'POST'])
def diet_delete(id):
    session = Session(bind=engine2)
    product = session.query(Ration).get(id)
    if product:
        session.delete(product)
        session.commit()
    else:
        abort(404)
    return redirect('/diet')


if __name__ == '__main__':
    main()
