from flask import Flask, render_template, redirect
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/base")
def base():
    return render_template("base.html")


def main():
    app.run()


if __name__ == '__main__':
    main()
