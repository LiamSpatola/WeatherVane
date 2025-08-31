from flask import Flask, render_template

from utils.weather import Weather


app = Flask(__name__)

global w
w = Weather()
w.city, w.coords, w.timezone = w.get_location_by_name("north ryde")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/current")
def current():
    current = w.get_current_weather()
    return render_template("current.html", w=w, current=current)


@app.route("/forecast")
def forecast():
    return render_template("forecast.html", w=w)


@app.route("/astronomy")
def astronomy():
    astronomy = w.get_astronomy_data()
    return render_template("astronomy.html", w=w, astronomy=astronomy)

if __name__ == "__main__":
    app.run(debug=True)
