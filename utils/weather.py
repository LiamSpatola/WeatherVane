import requests
from tzfpy import get_tz


class Weather:
    def __init__(self, city=None, coords=None, timezone=None):
        self.base_url = "https://wttr.in"
        self.city = city
        self.coords = coords
        self.timezone = timezone

    def get_location_by_user_ip(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            response.raise_for_status()
            data = response.json()

            city = data["city"]
            
            unformatted_coords = data["loc"].split(",")
            coords = {
                "lat": unformatted_coords[0],
                "lng": unformatted_coords[1]
            }
            
            timezone = data["timezone"]

            return (city, coords, timezone)
        except Exception:
            return None
        
    def get_location_by_name(self, place_name):
        try:
            headers = {"User-Agent": "WeatherVane/1.0"}
            response = requests.get(f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json", headers=headers)
            response.raise_for_status()
            data = response.json()[0]

            city = data["name"]

            coords = {
                "lat": data["lat"],
                "lng": data["lon"]
            }

            timezone = get_tz(float(data["lon"]), float(data["lat"]))

            return (city, coords, timezone)
        except Exception:
            return None
        
    def _get_weather_json(self):
        try:
            url = f"{self.base_url}/{self.city}?format=j1"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        
    def _get_astronomy_json(self):
        try:
            url = f"https://api.sunrise-sunset.org/json?lat={self.coords["lat"]}&lng={self.coords["lng"]}&tzid={self.timezone}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        
    def get_current_weather(self):
        data = self._get_weather_json()
        
        # Processing the current data
        current_data = data["current_condition"][0]
        current_weather = {
            "datetime": current_data["localObsDateTime"],
            "temperature": {
                "current": current_data["temp_C"],
                "feels_like": current_data["FeelsLikeC"]
            },
            "wind": {
                "speed": current_data["windspeedKmph"],
                "direction_deg": current_data["winddirDegree"],
                "direction_text": current_data["winddir16Point"],
            },
            "humidity": current_data["humidity"],
            "cloud_cover": current_data["cloudcover"],
            "precipitation": current_data["precipMM"],
            "pressure": current_data["pressure"],
            "uv_index": current_data["uvIndex"],
            "visibility": current_data["visibility"],
            "description": current_data["weatherDesc"][0]["value"],
        }

        return current_weather
    
    def get_astronomy_data(self):
        astronomy_data = self._get_astronomy_json()["results"]
        weather_data = self._get_weather_json()["weather"][0]["astronomy"][0]

        # Processing the data
        astronomy = {
            "sun": {
                "sunrise": astronomy_data["sunrise"],
                "sunset": astronomy_data["sunset"],
                "solar_noon": astronomy_data["solar_noon"],
                "day_length": astronomy_data["day_length"],
                "civil_twilight": {
                    "begin": astronomy_data["civil_twilight_begin"],
                    "end": astronomy_data["civil_twilight_end"],
                },
                "nautical_twilight": {
                    "begin": astronomy_data["nautical_twilight_begin"],
                    "end": astronomy_data["nautical_twilight_end"],
                },
                "astronomical_twilight": {
                    "begin": astronomy_data["astronomical_twilight_begin"],
                    "end": astronomy_data["astronomical_twilight_end"],
                }
            },
            "moon": {
                "moonrise": weather_data["moonrise"],
                "moonset": weather_data["moonset"],
                "moon_phase": weather_data["moon_phase"],
                "moon_illumination": weather_data["moon_illumination"],
            }
        }

        return astronomy
    
    def get_forecast(self):
        data = self._get_weather_json()

        # Processing the forecast
        forecast_data = data["weather"]

        full_daily_data = []
        full_hourly_data = []

        for day in forecast_data:
            # Getting the data for the day
            daily_data = {
                "date": day["date"],
                "temperature": {
                    "minimum": day["mintempC"],
                    "mean": day["avgtempC"],
                    "maximum": day["maxtempC"],
                },
                "sun_hours": day["sunHour"],
                "uvIndex": day["uvIndex"]
            }

            full_daily_data.append(daily_data)

            # Getting the data for each hour
            hourly_data = {"date": day["date"]}
            
            for hour in day["hourly"]:
                hourly_data[hour["time"].zfill(4)] = {
                    "temperature": {
                        "temp": hour["tempC"],
                        "feels_like": hour["FeelsLikeC"],
                        "dew_point": hour["DewPointC"],
                        "heat_index": hour["HeatIndexC"],
                        "wind_chill": hour["WindChillC"],
                    },
                    "wind": {
                        "speed": hour["windspeedKmph"],
                        "gust": hour["WindGustKmph"],
                        "direction_deg": hour["winddirDegree"],
                        "direction_text": hour["winddir16Point"],
                    },
                    "humidity": hour["humidity"],
                    "cloud_cover": hour["cloudcover"],
                    "pressure": hour["pressure"],
                    "precipitation": hour["precipMM"],
                    "visibility": hour["visibility"],
                    "uv_index": hour["uvIndex"],
                    "description": hour["weatherDesc"][0]["value"],
                    "radiation": {
                        "shortwave": hour["shortRad"],
                        "diffuse": hour["diffRad"],
                    },
                    "chance": {
                        "fog": hour["chanceoffog"],
                        "frost": hour["chanceoffrost"],
                        "high_temp": hour["chanceofhightemp"],
                        "overcast": hour["chanceofovercast"],
                        "rain": hour["chanceofrain"],
                        "remain_dry": hour["chanceofremdry"],
                        "snow": hour["chanceofsnow"],
                        "sunshine": hour["chanceofsunshine"],
                        "thunder": hour["chanceofthunder"],
                        "windy": hour["chanceofwindy"],
                    }
                }

            full_hourly_data.append(hourly_data)
    
        return (full_daily_data, full_hourly_data)

if __name__ == "__main__":
    w = Weather()
    w.city, w.coords, w.timezone = w.get_location_by_name("sydney")
    print(w.get_astronomy_data())