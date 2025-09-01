# WeatherVane
A simple flask web app to get weather data

## Installation
1. Clone the repository
```bash
git clone https://github.com/LiamSpatola/WeatherVane.git
```

2. Navigate to the repository directory
```bash
cd WeatherVane
```

3. Install poetry
```bash
pip install poetry
```

4. Install dependencies
```bash
poetry install
```

5. Run app.py
```bash
poetry run python app.py
```

## APIs Used
- [Open-Meteo](https://open-meteo.com) - Used for extracting current conditions, and forecast data.
- [Sunrise-Sunset](https://sunrise-sunset.org) - Used for extracting sunrise/sunset times, and twilight data.
- [wttr.in](https://wttr.in) - Used for extracting moon data.
- [IPinfo](https://ipinfo.io/) - Used for finding user location based off IP address.
- [OpenStreetMap](https://openstreetmap.org) - Used for finding coordinates based off place names.

Many thanks to these API providers for making their API free and not requiring API keys. This project would not be possible without them.