from flask import Flask, render_template, request, redirect, url_for
from zoneinfo import available_timezones

from utils.weather import Weather


app = Flask(__name__)

w = Weather()
w.city, w.coords, w.timezone = w.get_location_by_user_ip()

timezones = sorted(available_timezones(), key=lambda tz: (tz.split("/")[0], tz.split("/")[1] if "/" in tz else ""))

@app.route("/", methods=["GET", "POST"])
def index():
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

        # 
        
        # Redirecting the user to the current weather page
        return redirect(url_for("current"))

    return render_template("index.html", w=w, timezones=timezones)


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
