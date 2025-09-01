from flask import Flask, render_template, request, redirect, url_for, session
from zoneinfo import available_timezones
import os

from utils.weather import Weather


app = Flask(__name__)

app.secret_key = os.urandom(32)


def create_weather_object_if_not_in_session():
    try:
        if not session["weather"]:
            w = Weather()
            session["weather"] = {
                "city": w.city,
                "coords": w.coords,
                "timezone": w.timezone
            }
    except KeyError:
        w = Weather()
        session["weather"] = {
            "city": w.city,
            "coords": w.coords,
            "timezone": w.timezone
        }


timezones = sorted(available_timezones(), key=lambda tz: (tz.split("/")[0], tz.split("/")[1] if "/" in tz else ""))

@app.route("/", methods=["GET", "POST"])
def index():
    create_weather_object_if_not_in_session()
    w = Weather(session["weather"]["city"], session["weather"]["coords"], session["weather"]["timezone"])

    if request.method == "POST": # Checking if the user is updating their location
        # Getting the form data
        use_my_location = request.form.get("use_location")
        place_name = request.form.get("place_name")
        tz = request.form.get("timezone")

        # Updating the location
        if use_my_location:
            w.city, w.coords, w.timezone = w.get_location_by_user_ip()
        else:
            if not place_name:
                # Fallback to user location if no place entered
                w.city, w.coords, w.timezone = w.get_location_by_user_ip()
            else:
                w.city, w.coords, w.timezone = w.get_location_by_name(place_name)
        
        # Overriding the timezone if the user selected a custom timezone
        if tz and tz != "auto":
            w.timezone = tz

        # Saving the weather object
        session["weather"] = {
                "city": w.city,
                "coords": w.coords,
                "timezone": w.timezone
        }

    return render_template("index.html", w=w, timezones=timezones)


@app.route("/current")
def current():
    create_weather_object_if_not_in_session()
    w = Weather(session["weather"]["city"], session["weather"]["coords"], session["weather"]["timezone"])

    current = w.get_current_weather()
    return render_template("current.html", w=w, current=current)


@app.route("/forecast")
def forecast():
    create_weather_object_if_not_in_session()
    w = Weather(session["weather"]["city"], session["weather"]["coords"], session["weather"]["timezone"])

    daily = w.get_forecast()
    return render_template("forecast.html", w=w, daily=daily)


@app.route("/hourly-forecast")
def hourly_forecast():
    create_weather_object_if_not_in_session()
    w = Weather(session["weather"]["city"], session["weather"]["coords"], session["weather"]["timezone"])

    date = request.args.get("date")
    if not date:
        return redirect(url_for("index"))
    
    hourly = w.get_hourly_forecast(date)
    return render_template("hourly_forecast.html", w=w, hourly=hourly, date=date)


@app.route("/astronomy")
def astronomy():
    create_weather_object_if_not_in_session()
    w = Weather(session["weather"]["city"], session["weather"]["coords"], session["weather"]["timezone"])

    astronomy = w.get_astronomy_data()
    return render_template("astronomy.html", w=w, astronomy=astronomy)


@app.route("/reset-session", methods=["GET", "POST"])
def reset_session():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
