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
        
    def _get_open_meteo_json(self, current_params=None, daily_params=None, hourly_params=None, date=None):
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.coords["lat"],
            "longitude": self.coords["lng"],
            "timezone": self.timezone,
            "current": ",".join(current_params) if current_params else None,
            "daily": ",".join(daily_params) if daily_params else None,
            "hourly": ",".join(hourly_params) if hourly_params else None,
            "start_date": date,
            "end_date": date
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def get_current_weather(self):
        data = self._get_open_meteo_json(current_params=["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "uv_index"])

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
        data = self._get_open_meteo_json(daily_params=["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean", "relative_humidity_2m_max", "relative_humidity_2m_min", "relative_humidity_2m_mean", "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min", "precipitation_probability_max", "precipitation_probability_min", "precipitation_probability_mean", "precipitation_hours", "precipitation_sum", "snowfall_sum", "showers_sum", "rain_sum", "pressure_msl_mean", "pressure_msl_max", "pressure_msl_min", "surface_pressure_mean", "surface_pressure_max", "surface_pressure_min", "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min", "visibility_min", "visibility_max", "visibility_mean", "wind_speed_10m_min", "wind_gusts_10m_min", "wind_speed_10m_mean", "wind_gusts_10m_mean", "wind_speed_10m_max", "wind_gusts_10m_max", "winddirection_10m_dominant", "uv_index_max", "uv_index_clear_sky_max"])

        forecasts = []
        # Processing the daily data
        for idx, day in enumerate(data["daily"]["time"]):
            forecast = {
                "date": day,
                "temperature": {
                    "temp_min": data["daily"]["temperature_2m_min"][idx],
                    "temp_mean": data["daily"]["temperature_2m_mean"][idx],
                    "temp_max": data["daily"]["temperature_2m_max"][idx],
                    "apparent_min": data["daily"]["apparent_temperature_min"][idx],
                    "apparent_mean": data["daily"]["apparent_temperature_mean"][idx],
                    "apparent_max": data["daily"]["apparent_temperature_max"][idx]
                },
                "humidity": {
                    "relative_min": data["daily"]["relative_humidity_2m_min"][idx],
                    "relative_mean": data["daily"]["relative_humidity_2m_mean"][idx],
                    "relative_max": data["daily"]["relative_humidity_2m_max"][idx],
                    "dewpoint_min": data["daily"]["dew_point_2m_min"][idx],
                    "dewpoint_mean": data["daily"]["dew_point_2m_mean"][idx],
                    "dewpoint_max": data["daily"]["dew_point_2m_max"][idx]
                },
                "precipitation": {
                    "probability_min": data["daily"]["precipitation_probability_min"][idx],
                    "probability_mean": data["daily"]["precipitation_probability_mean"][idx],
                    "probability_max": data["daily"]["precipitation_probability_max"][idx],
                    "total_hours": data["daily"]["precipitation_hours"][idx],
                    "total_sum": data["daily"]["precipitation_sum"][idx],
                    "rain_sum": data["daily"]["rain_sum"][idx],
                    "showers_sum": data["daily"]["showers_sum"][idx],
                    "snowfall_sum": data["daily"]["snowfall_sum"][idx]
                },
                "pressure": {
                    "sea_level_min": data["daily"]["pressure_msl_min"][idx],
                    "sea_level_mean": data["daily"]["pressure_msl_mean"][idx],
                    "sea_level_max": data["daily"]["pressure_msl_max"][idx],
                    "surface_min": data["daily"]["surface_pressure_min"][idx],
                    "surface_mean": data["daily"]["surface_pressure_mean"][idx],
                    "surface_max": data["daily"]["surface_pressure_max"][idx]
                },
                "cloud_cover": {
                    "min": data["daily"]["cloud_cover_min"][idx],
                    "mean": data["daily"]["cloud_cover_mean"][idx],
                    "max": data["daily"]["cloud_cover_max"][idx]
                },
                "visibility": {
                    "min": round(data["daily"]["visibility_min"][idx] / 1000, 2),
                    "mean": round(data["daily"]["visibility_mean"][idx] / 1000, 2),
                    "max": round(data["daily"]["visibility_max"][idx] / 1000, 2)
                },
                "wind": {
                    "min_speed": data["daily"]["wind_speed_10m_min"][idx],
                    "min_gusts": data["daily"]["wind_gusts_10m_min"][idx],
                    "mean_speed": data["daily"]["wind_speed_10m_mean"][idx],
                    "mean_gusts": data["daily"]["wind_gusts_10m_mean"][idx],
                    "max_speed": data["daily"]["wind_speed_10m_max"][idx],
                    "max_gusts": data["daily"]["wind_gusts_10m_max"][idx],
                    "direction": data["daily"]["winddirection_10m_dominant"][idx]
                },
                "uv_index": {
                    "index": data["daily"]["uv_index_max"][idx],
                    "clear_sky_index": data["daily"]["uv_index_clear_sky_max"][idx]
                }
            }

            forecasts.append(forecast)
            
        return forecasts
    
    def get_hourly_forecast(self, date):
        data = self._get_open_meteo_json(hourly_params=["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "uv_index"], date=date)

        forecasts = []
        for idx, hour in enumerate(data["hourly"]["time"]):
            forecast = {
                "time": hour.split("T")[1],
                "temperature": {
                    "air_temp": data["hourly"]["temperature_2m"][idx],
                    "apparent_temp": data["hourly"]["apparent_temperature"][idx]
                },
                "humidity": {
                    "relative": data["hourly"]["relative_humidity_2m"][idx],
                    "dewpoint": data["hourly"]["dew_point_2m"][idx]
                },
                "precipitation": {
                    "probability": data["hourly"]["precipitation_probability"][idx],
                    "amount": data["hourly"]["precipitation"][idx],
                    "rain": data["hourly"]["rain"][idx],
                    "showers": data["hourly"]["showers"][idx],
                    "snowfall": data["hourly"]["snowfall"][idx]
                },
                "pressure": {
                    "sea_level": data["hourly"]["pressure_msl"][idx],
                    "surface": data["hourly"]["surface_pressure"][idx]
                },
                "cloud_cover": {
                    "total": data["hourly"]["cloud_cover"][idx],
                    "low": data["hourly"]["cloud_cover_low"][idx],
                    "mid": data["hourly"]["cloud_cover_mid"][idx],
                    "high": data["hourly"]["cloud_cover_high"][idx]
                },
                "visibility": round(data["hourly"]["visibility"][idx] / 1000, 2),
                "wind": {
                    "speed": data["hourly"]["wind_speed_10m"][idx],
                    "gusts": data["hourly"]["wind_gusts_10m"][idx],
                    "direction": data["hourly"]["wind_direction_10m"][idx]
                },
                "uv_index": data["hourly"]["uv_index"][idx]
            }

            forecasts.append(forecast)

        return forecasts


if __name__ == "__main__":
    w = Weather()
    w.city, w.coords, w.timezone = w.get_location_by_user_ip()
    print(w.get_current_weather())