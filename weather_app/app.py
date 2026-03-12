from flask import Flask, render_template, request, jsonify
import os
import requests
import sqlite3
from dotenv import load_dotenv
from service.weather_service import get_weather_data

load_dotenv()
app = Flask(__name__)


# --- SQLITE DATABASE SETUP ---
def init_db():
    with sqlite3.connect('weather.db') as conn:
        # UNIQUE ensures we don't save "London" 5 times in a row
        conn.execute('''CREATE TABLE IF NOT EXISTS searches 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        city TEXT UNIQUE, 
                        last_searched DATETIME DEFAULT CURRENT_TIMESTAMP)''')


init_db()


def add_to_history(city):
    with sqlite3.connect('weather.db') as conn:
        # If the city exists, just update the timestamp
        conn.execute(
            'INSERT INTO searches (city, last_searched) VALUES (?, CURRENT_TIMESTAMP) ON CONFLICT(city) DO UPDATE SET last_searched=CURRENT_TIMESTAMP',
            (city,))


def get_history():
    with sqlite3.connect('weather.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT city FROM searches ORDER BY last_searched DESC LIMIT 5')
        return [row[0] for row in cur.fetchall()]


@app.route('/', methods=['GET', 'POST'])
def home():
    api_key = os.getenv("API_KEY")
    weather_result = None
    lat, lon = request.args.get('lat'), request.args.get('lon')
    history = get_history()  # Grab the latest history for the UI

    if request.method == 'POST':
        city_name = request.form.get('city', '').strip()
        if city_name:
            weather_result = get_weather_data(api_key=api_key, city_name=city_name)
            if weather_result and weather_result.get("success"):
                add_to_history(weather_result["city"])  # Save to SQLite!
                history = get_history()  # Refresh history list
    elif lat and lon:
        weather_result = get_weather_data(api_key=api_key, lat=lat, lon=lon)

    if weather_result:
        if weather_result.get("success"):
            return render_template('index.html', data=weather_result, history=history)
        else:
            return render_template('index.html', error=weather_result.get("error"), history=history)

    return render_template('index.html', history=history)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    if len(query) < 3:
        return jsonify([])

    api_key = os.getenv("API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={api_key}"

    try:
        res = requests.get(url, timeout=3)
        res.raise_for_status()
        suggestions = []
        for item in res.json():
            label = f"{item.get('name')}, {item.get('state', '')}, {item.get('country', '')}".replace(", ,", ",")
            if label not in suggestions:
                suggestions.append(label)
        return jsonify(suggestions)
    except Exception:
        return jsonify([])


if __name__ == '__main__':
    app.run(debug=True)