import requests


def get_weather_data(api_key, city_name=None, lat=None, lon=None):
    """Fetches weather + AQI and applies professional error handling."""
    base_url = "https://api.openweathermap.org/data/2.5"
    query = f"lat={lat}&lon={lon}" if lat else f"q={city_name}"

    try:
        # 1. Fetch Current Weather
        curr_res = requests.get(f"{base_url}/weather?{query}&appid={api_key}&units=metric", timeout=5)
        curr_res.raise_for_status()
        curr_data = curr_res.json()

        # Dynamic Background Logic
        api_icon = curr_data["weather"][0]["icon"]
        background_classes = {
            '01d': 'clear-day', '01n': 'clear-night',
            '02d': 'clouds-day', '02n': 'clouds-night',
        }
        weather_type = background_classes.get(api_icon, curr_data["weather"][0]["main"].lower())

        # 2. Fetch 5-Day Forecast
        fore_res = requests.get(f"{base_url}/forecast?{query}&appid={api_key}&units=metric", timeout=5)
        fore_res.raise_for_status()
        fore_data = fore_res.json()

        daily_forecast = []
        for i in range(0, len(fore_data['list']), 8):
            day = fore_data['list'][i]
            daily_forecast.append({
                "date": day['dt_txt'].split(" ")[0][5:],
                "temp": round(day['main']['temp']),
                "icon": day['weather'][0]['icon']
            })

        # Fetch Air Quality Index (AQI)
        # We use the exact coordinates returned from the first API call
        city_lat = curr_data['coord']['lat']
        city_lon = curr_data['coord']['lon']

        aqi_res = requests.get(f"{base_url}/air_pollution?lat={city_lat}&lon={city_lon}&appid={api_key}", timeout=5)
        aqi_res.raise_for_status()
        aqi_data = aqi_res.json()

        aqi_val = aqi_data['list'][0]['main']['aqi']
        aqi_mapping = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        return {
            "success": True,
            "city": curr_data["name"],
            "temp": round(curr_data["main"]["temp"]),
            "weather": curr_data["weather"][0]["description"].title(),
            "weather_type": weather_type,
            "icon": api_icon,
            "humidity": curr_data["main"]["humidity"],
            "wind": curr_data["wind"]["speed"],
            "feels_like": round(curr_data["main"]["feels_like"]),
            "pressure": curr_data["main"]["pressure"],
            "forecast": daily_forecast,
            # Pass the new AQI data to the frontend
            "aqi": aqi_val,
            "aqi_text": aqi_mapping.get(aqi_val, "Unknown"),
            "pm25": aqi_data['list'][0]['components']['pm2_5'],
            "pm10": aqi_data['list'][0]['components']['pm10']
        }

        # Error Handling
    except requests.exceptions.Timeout:
            # Handles when the OpenWeatherMap server is too slow
            return {"success": False, "error": "API timeout. The weather service is taking too long."}

    except requests.exceptions.HTTPError as e:
        # Handles specific API rejection codes
        if e.response.status_code == 404:
            return {"success": False, "error": "City not found. Please check your spelling."}
        elif e.response.status_code == 401:
            return {"success": False, "error": "Invalid API Key. Please check your configuration."}
        else:
            return {"success": False, "error": f"API Error: Received status code {e.response.status_code}"}

    except requests.exceptions.ConnectionError:
        # Handles when the user's internet is down
        return {"success": False, "error": "Network error. Please check your internet connection."}

    except requests.exceptions.RequestException:
        # A catch-all for any other requests-related issue
        return {"success": False, "error": "A network error occurred while fetching data."}

    except Exception as e:
        # A final safety net for internal code bugs
        return {"success": False, "error": "An unexpected internal error occurred."}