import requests


class Weather:
    def __init__(self, location=None):
        self.base_url = "https://wttr.in"
        self.location = location

    def get_location_by_user_ip(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            response.raise_for_status()
            data = response.json()
            city = data["city"]

            return city if city else None
        except Exception:
            return None
        
    def _get_weather_json(self):
        try:
            url = f"{self.base_url}/{self.location}?format=j1"
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
        data = self._get_weather_json()

        # Processing the astronomy data
        weather_data = data["weather"]

        full_astronomy_data = []

        for day in weather_data:
            astronomy_data = day["astronomy"][0]
            astronomy = {
                "date": day["date"],
                "sun": {
                    "sunrise": astronomy_data["sunrise"],
                    "sunset": astronomy_data["sunset"],
                },
                "moon": {
                    "moonrise": astronomy_data["moonrise"],
                    "moonset": astronomy_data["moonset"],
                    "moon_phase": astronomy_data["moon_phase"],
                    "moon_illumination": astronomy_data["moon_illumination"],
                }
            }

            full_astronomy_data.append(astronomy)

        return full_astronomy_data
    
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
    w.location = w.get_location_by_user_ip()
    print(w.get_forecast())