import requests
import os

def get_weather_tool():
    def weather_lookup(location, date=None):
        # Free API: https://open-meteo.com/
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 35.6762,  # default Tokyo for demo
            "longitude": 139.6503,
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "Asia/Tokyo"
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data

    return weather_lookup
