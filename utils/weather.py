import requests
from tzfpy import get_tz


class Weather:
    def __init__(self, city=None, coords=None, timezone=None):
        self.city = city
        self.coords = coords
        self.timezone = timezone

    def get_location_by_user_ip(self):
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
        
    def get_location_by_name(self, place_name):
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
        
    def _get_wttr_in_json(self):
        url = f"https://wttr.in/{self.city}?format=j1"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
        
    def _get_astronomy_json(self):
        url = f"https://api.sunrise-sunset.org/json?lat={self.coords["lat"]}&lng={self.coords["lng"]}&tzid={self.timezone}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
        
    def _get_open_meteo_json(self, current_params=None, daily_params=None, hourly_params=None):
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.coords["lat"],
            "longitude": self.coords["lng"],
            "timezone": self.timezone,
            "current": ",".join(current_params),
            "daily": daily_params,
            "hourly": hourly_params
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_current_weather(self):
        data = self._get_open_meteo_json(["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "uv_index"])

        current_data = data["current"]

        current = {
            "datetime": {
                "date": current_data["time"].split("T")[0],
                "time": current_data["time"].split("T")[1]
            },
            "temperature": {
                "air_temp": current_data["temperature_2m"],
                "apparent_temp": current_data["apparent_temperature"]
            },
            "humidity": {
                "relative": current_data["relative_humidity_2m"],
                "dewpoint": current_data["dew_point_2m"]
            },
            "precipitation": {
                "probability": current_data["precipitation_probability"],
                "amount": current_data["precipitation"],
                "rain": current_data["rain"],
                "showers": current_data["showers"],
                "snowfall": current_data["snowfall"]
            },
            "pressure": {
                "sea_level": current_data["pressure_msl"],
                "surface": current_data["surface_pressure"]
            },
            "cloud_cover": {
                "total": current_data["cloud_cover"],
                "low": current_data["cloud_cover_low"],
                "mid": current_data["cloud_cover_mid"],
                "high": current_data["cloud_cover_high"]
            },
            "visibility": round(current_data["visibility"] / 1000, 2),
            "wind": {
                "speed": current_data["wind_speed_10m"],
                "gusts": current_data["wind_gusts_10m"],
                "direction": current_data["wind_direction_10m"]
            },
            "uv_index": current_data["uv_index"]
        }

        return current
    
    def get_astronomy_data(self):
        astronomy_data = self._get_astronomy_json()["results"]
        weather_data = self._get_wttr_in_json()["weather"][0]["astronomy"][0]

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
        pass

if __name__ == "__main__":
    w = Weather()
    w.city, w.coords, w.timezone = w.get_location_by_name("sydney")
    print(w.get_current_weather())