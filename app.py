from flask import Flask, render_template, request, redirect, url_for

from utils.weather import Weather


app = Flask(__name__)

global w
w = Weather()
w.city, w.coords, w.timezone = w.get_location_by_user_ip()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/current")
def current():
    current = w.get_current_weather()
    return render_template("current.html", w=w, current=current)


@app.route("/forecast")
def forecast():
    daily = w.get_forecast()
    return render_template("forecast.html", w=w, daily=daily)


@app.route("/hourly_forecast")
def hourly_forecast():
    date = request.args.get("date")
    if not date:
        return redirect(url_for("index"))
    
    hourly = w.get_hourly_forecast(date)
    return render_template("hourly_forecast.html", w=w, hourly=hourly, date=date)


@app.route("/astronomy")
def astronomy():
    astronomy = w.get_astronomy_data()
    return render_template("astronomy.html", w=w, astronomy=astronomy)

if __name__ == "__main__":
    app.run(debug=True)
