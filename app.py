from flask import Flask, render_template

from utils.weather import Weather


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/current")
def current():
    return render_template("current.html")


@app.route("/forecast")
def forecast():
    return render_template("forecast.html")


@app.route("/astronomy")
def astronomy():
    return render_template("astronomy.html")

if __name__ == "__main__":
    app.run(debug=True)
