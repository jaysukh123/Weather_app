import requests
from django.shortcuts import render

# Weather code to OpenWeather icons mapping
WEATHER_ICONS = {
    0: "https://openweathermap.org/img/wn/01d@2x.png",  # Clear sky
    1: "https://openweathermap.org/img/wn/02d@2x.png",  # Partly cloudy
    2: "https://openweathermap.org/img/wn/03d@2x.png",  # Cloudy
    3: "https://openweathermap.org/img/wn/04d@2x.png",  # Overcast
    45: "https://openweathermap.org/img/wn/50d@2x.png",  # Fog
    48: "https://openweathermap.org/img/wn/50d@2x.png",
    51: "https://openweathermap.org/img/wn/09d@2x.png",  # Drizzle
    61: "https://openweathermap.org/img/wn/10d@2x.png",  # Rain
    66: "https://openweathermap.org/img/wn/13d@2x.png",  # Freezing rain
    71: "https://openweathermap.org/img/wn/13d@2x.png",  # Snow
    80: "https://openweathermap.org/img/wn/09d@2x.png",  # Showers
    95: "https://openweathermap.org/img/wn/11d@2x.png",  # Thunderstorm
}

def get_weather(request):
    city = request.GET.get('city', 'London')  # Default: London
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

    # Get latitude & longitude
    geo_response = requests.get(geo_url).json()
    if "results" not in geo_response:
        return render(request, "weather.html", {"error": "City not found. Try again."})

    latitude = geo_response["results"][0]["latitude"]
    longitude = geo_response["results"][0]["longitude"]

    # Fetch weather data with hourly forecast
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,windspeed_10m&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max,weathercode&timezone=auto"
    weather_response = requests.get(weather_url).json()

    if "current_weather" not in weather_response:
        return render(request, "weather.html", {"error": "Weather data not available."})

    # Get weather code and icon
    weather_code = weather_response["current_weather"]["weathercode"]
    weather_icon = WEATHER_ICONS.get(weather_code, "https://openweathermap.org/img/wn/01d@2x.png")  # Default sun icon

    # Extract hourly forecast (next 6 hours)
    hourly_data = [
        {
            "time": weather_response["hourly"]["time"][i][-5:],  # Get hour (HH:MM)
            "temp": weather_response["hourly"]["temperature_2m"][i],
            "wind": weather_response["hourly"]["windspeed_10m"][i],
        }
        for i in range(24)  # Next 6 hours
    ]

    # Extract daily forecast (7 days)
    weather_data = {
        "city": city,
        "temperature": weather_response["current_weather"]["temperature"],
        "windspeed": weather_response["current_weather"]["windspeed"],
        "weather_icon": weather_icon,
        "forecast": [
            {
                "date": weather_response["daily"]["time"][i],
                "temp_max": weather_response["daily"]["temperature_2m_max"][i],
                "temp_min": weather_response["daily"]["temperature_2m_min"][i],
                "wind_max": weather_response["daily"]["windspeed_10m_max"][i],
                "icon": WEATHER_ICONS.get(weather_response["daily"]["weathercode"][i], "https://openweathermap.org/img/wn/01d@2x.png"),
            }
            for i in range(7)
        ],
        "hourly": hourly_data,  # Add hourly forecast
        "latitude": latitude,
        "longitude": longitude,
    }

    

    return render(request, "weather.html", {"weather": weather_data})
