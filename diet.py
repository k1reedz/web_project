import sqlite3

from flask import Flask, render_template, request, redirect, abort
from data.ration import Ration
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
engine = create_engine("sqlite:///db/ration.db")
con = sqlite3.connect('db/products.db')
cur = con.cursor()
all_products = cur.execute('''SELECT name FROM products''').fetchall()
products_list = []
for i in all_products:
    products_list.append(i[0])
con.close()


def get_kpfc(product):
    con = sqlite3.connect('db/products.db')
    cur = con.cursor()
    get_kpfc = cur.execute('''SELECT kcal, proteins, fats, carbohydrates FROM products
    WHERE name = ?''', (product,)).fetchone()
    con.close()
    return get_kpfc[0], get_kpfc[1], get_kpfc[2], get_kpfc[3]


def main():
    app.run()


@app.route("/diet", methods=['POST', 'GET'])
def diet():
    if request.method == 'POST':
        current_date = request.form['input_date']
    else:
        current_date = date.today()
    session = Session(bind=engine)
    products = session.query(Ration).filter(Ration.created_date.like(f'{current_date}%')).all()
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
            return render_template("adding_a_product.html", products_list=products_list,
                                   inf='Продукт не найден', title_text=title, weight_text=weight)
        if bool(title) and bool(weight):
            try:
                session = Session(bind=engine)
                kcal, proteins, fats, carbohydrates = get_kpfc(title)
                if session.query(Ration).filter(Ration.title == title).count() == 0:
                    product = Ration(title=title, weight=weight,
                                     total_kcal=str(float(kcal) * float(weight) / 100),
                                     total_proteins=str(float(proteins) * float(weight) / 100),
                                     total_fats=str(float(fats) * float(weight) / 100),
                                     total_carbohydrates=str(float(carbohydrates) * float(weight) / 100))
                    session.add(product)
                    session.commit()
                else:
                    product = session.query(Ration).filter(Ration.title == title).first()
                    product.weight = str(product.weight + float(weight))
                    product.total_kcal = str(float(product.total_kcal) + float(kcal) * float(weight) / 100)
                    product.total_proteins = str(float(product.total_proteins) + float(proteins) * float(weight) / 100)
                    product.total_fats = str(float(product.total_fats) + float(fats) * float(weight) / 100)
                    product.total_carbohydrates = str(float(product.total_carbohydrates) + float(carbohydrates) * \
                                                  float(weight) / 100)
                    session.add(product)
                    session.commit()
                return redirect("/diet")
            except:
                abort(404)
        else:
            return render_template("adding_a_product.html", products_list=products_list,
                                   inf='Заполните все поля', title_text=title, weight_text=weight)
    else:
        return render_template("adding_a_product.html", products_list=products_list)


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
                session = Session(bind=engine)
                product = session.query(Ration).get(id)
                kcal, proteins, fats, carbohydrates = get_kpfc(title)
                product.title = title
                product.weight = weight
                product.total_kcal = str(float(product.total_kcal) + float(kcal) * float(weight) / 100)
                product.total_proteins = str(float(product.total_proteins) + float(proteins) * float(weight) / 100)
                product.total_fats = str(float(product.total_fats) + float(fats) * float(weight) / 100)
                product.total_carbohydrates = str(float(product.total_carbohydrates) + float(carbohydrates) *
                                                  float(weight) / 100)
                session.add(product)
                session.commit()
                return redirect("/diet")
            except:
                abort(404)
        else:
            return render_template("diet_change.html", products_list=products_list, inf='Заполните все поля',
                                   title_text=title, weight_text=weight)
    else:
        return render_template("diet_change.html", products_list=products_list)


@app.route('/diet_delete/<int:id>', methods=['GET', 'POST'])
def diet_delete(id):
    session = Session(bind=engine)
    product = session.query(Ration).get(id)
    if product:
        session.delete(product)
        session.commit()
    else:
        abort(404)
    return redirect('/diet')


if __name__ == '__main__':
    main()
