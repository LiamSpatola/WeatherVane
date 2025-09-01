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
            "current": ",".join(current_params) if current_params else None,
            "daily": ",".join(daily_params) if daily_params else None,
            "hourly": ",".join(hourly_params) if hourly_params else None
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
        hourly_data = self._get_open_meteo_json(hourly_params=["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "uv_index"])
        daily_data = self._get_open_meteo_json(daily_params=["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean", "relative_humidity_2m_max", "relative_humidity_2m_min", "relative_humidity_2m_mean", "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min", "precipitation_probability_max", "precipitation_probability_min", "precipitation_probability_mean", "precipitation_hours", "precipitation_sum", "snowfall_sum", "showers_sum", "rain_sum", "pressure_msl_mean", "pressure_msl_max", "pressure_msl_min", "surface_pressure_mean", "surface_pressure_max", "surface_pressure_min", "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min", "visibility_min", "visibility_max", "visibility_mean", "wind_speed_10m_min", "wind_gusts_10m_min", "wind_speed_10m_mean", "wind_gusts_10m_mean", "wind_speed_10m_max", "wind_gusts_10m_max", "winddirection_10m_dominant", "uv_index_max", "uv_index_clear_sky_max"])

        daily_forecasts = []
        # Processing the daily data
        for idx, day in enumerate(daily_data["daily"]["time"]):
            forecast = {
                "date": day,
                "temperature": {
                    "temp_min": daily_data["daily"]["temperature_2m_min"][idx],
                    "temp_mean": daily_data["daily"]["temperature_2m_mean"][idx],
                    "temp_max": daily_data["daily"]["temperature_2m_max"][idx],
                    "apparent_min": daily_data["daily"]["apparent_temperature_min"][idx],
                    "apparent_mean": daily_data["daily"]["apparent_temperature_mean"][idx],
                    "apparent_max": daily_data["daily"]["apparent_temperature_max"][idx]
                },
                "humidity": {
                    "relative_min": daily_data["daily"]["relative_humidity_2m_min"][idx],
                    "relative_mean": daily_data["daily"]["relative_humidity_2m_mean"][idx],
                    "relative_max": daily_data["daily"]["relative_humidity_2m_max"][idx],
                    "dewpoint_min": daily_data["daily"]["dew_point_2m_min"][idx],
                    "dewpoint_mean": daily_data["daily"]["dew_point_2m_mean"][idx],
                    "dewpoint_max": daily_data["daily"]["dew_point_2m_max"][idx]
                },
                "precipitation": {
                    "probability_min": daily_data["daily"]["precipitation_probability_min"][idx],
                    "probability_mean": daily_data["daily"]["precipitation_probability_mean"][idx],
                    "probability_max": daily_data["daily"]["precipitation_probability_max"][idx],
                    "total_hours": daily_data["daily"]["precipitation_hours"][idx],
                    "total_sum": daily_data["daily"]["precipitation_sum"][idx],
                    "rain_sum": daily_data["daily"]["rain_sum"][idx],
                    "showers_sum": daily_data["daily"]["showers_sum"][idx],
                    "snowfall_sum": daily_data["daily"]["snowfall_sum"][idx]
                },
                "pressure": {
                    "sea_level_min": daily_data["daily"]["pressure_msl_min"][idx],
                    "sea_level_mean": daily_data["daily"]["pressure_msl_mean"][idx],
                    "sea_level_max": daily_data["daily"]["pressure_msl_max"][idx],
                    "surface_min": daily_data["daily"]["surface_pressure_min"][idx],
                    "surface_mean": daily_data["daily"]["surface_pressure_mean"][idx],
                    "surface_max": daily_data["daily"]["surface_pressure_max"][idx]
                },
                "cloud_cover": {
                    "min": daily_data["daily"]["cloud_cover_min"][idx],
                    "mean": daily_data["daily"]["cloud_cover_mean"][idx],
                    "max": daily_data["daily"]["cloud_cover_max"][idx]
                },
                "visibility": {
                    "min": round(daily_data["daily"]["visibility_min"][idx] / 1000, 2),
                    "mean": round(daily_data["daily"]["visibility_mean"][idx] / 1000, 2),
                    "max": round(daily_data["daily"]["visibility_max"][idx] / 1000, 2)
                },
                "wind": {
                    "min_speed": daily_data["daily"]["wind_speed_10m_min"][idx],
                    "min_gusts": daily_data["daily"]["wind_gusts_10m_min"][idx],
                    "mean_speed": daily_data["daily"]["wind_speed_10m_mean"][idx],
                    "mean_gusts": daily_data["daily"]["wind_gusts_10m_mean"][idx],
                    "max_speed": daily_data["daily"]["wind_speed_10m_max"][idx],
                    "max_gusts": daily_data["daily"]["wind_gusts_10m_max"][idx],
                    "direction": daily_data["daily"]["winddirection_10m_dominant"][idx]
                },
                "uv_index": {
                    "index": daily_data["daily"]["uv_index_max"][idx],
                    "clear_sky_index": daily_data["daily"]["uv_index_clear_sky_max"][idx]
                }
            }

            daily_forecasts.append(forecast)

            # Processing the hourly data
            hourly_forecasts = []
            for idx, hour in enumerate(hourly_data["hourly"]["time"]):
                forecast = {
                    "datetime": {
                        "date": hourly_data["hourly"]["time"][idx].split("T")[0],
                        "time": hourly_data["hourly"]["time"][idx].split("T")[1]
                    },
                    "temperature": {
                        "air_temp": hourly_data["hourly"]["temperature_2m"][idx],
                        "apparent_temp": hourly_data["hourly"]["apparent_temperature"][idx]
                    },
                    "humidity": {
                        "relative": hourly_data["hourly"]["relative_humidity_2m"][idx],
                        "dewpoint": hourly_data["hourly"]["dew_point_2m"][idx]
                    },
                    "precipitation": {
                        "probability": hourly_data["hourly"]["precipitation_probability"][idx],
                        "amount": hourly_data["hourly"]["precipitation"][idx],
                        "rain": hourly_data["hourly"]["rain"][idx],
                        "showers": hourly_data["hourly"]["showers"][idx],
                        "snowfall": hourly_data["hourly"]["snowfall"][idx]
                    },
                    "pressure": {
                        "sea_level": hourly_data["hourly"]["pressure_msl"][idx],
                        "surface": hourly_data["hourly"]["surface_pressure"][idx]
                    },
                    "cloud_cover": {
                        "total": hourly_data["hourly"]["cloud_cover"][idx],
                        "low": hourly_data["hourly"]["cloud_cover_low"][idx],
                        "mid": hourly_data["hourly"]["cloud_cover_mid"][idx],
                        "high": hourly_data["hourly"]["cloud_cover_high"][idx]
                    },
                    "visibility": round(hourly_data["hourly"]["visibility"][idx] / 1000, 2),
                    "wind": {
                        "speed": hourly_data["hourly"]["wind_speed_10m"][idx],
                        "gusts": hourly_data["hourly"]["wind_gusts_10m"][idx],
                        "direction": hourly_data["hourly"]["wind_direction_10m"][idx]
                    },
                    "uv_index": hourly_data["hourly"]["uv_index"][idx]
                }

                hourly_forecasts.append(forecast)
            
            return (daily_forecasts, hourly_forecasts)


if __name__ == "__main__":
    w = Weather()
    w.city, w.coords, w.timezone = w.get_location_by_user_ip()
    print(w.get_current_weather())