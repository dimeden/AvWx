import csv
import requests
from haversine import haversine, Unit
from flask import Flask, render_template

app = Flask(__name__)

OKC_LAT = 35.4676
OKC_LON = -97.5164
RADIUS_NM = 250
AVIATIONWEATHER_API_KEY = '_aXUbcGDw8ZG3dqjqZaIniGomrbbCkO08aG4kCh5Syk'

flight_categories = {
    'VFR': {'min_visibility': 5, 'min_ceiling': 3000, 'color': 'green'},
    'MVFR': {'min_visibility': 3, 'min_ceiling': 1000, 'color': 'blue'},
    'IFR': {'min_visibility': 1, 'min_ceiling': 500, 'color': 'red'},
    'LIFR': {'min_visibility': 0, 'min_ceiling': 0, 'color': 'purple'},
}

def determine_flight_category(vis, ceiling):
    for category, limits in flight_categories.items():
        if vis >= limits['min_visibility'] and ceiling >= limits['min_ceiling']:
            return category, limits['color']
    return 'Unknown', 'black'

def get_metar_data(icao):
    url = f'https://avwx.rest/api/metar/{icao}'
    headers = {'Authorization': f'Bearer {AVIATIONWEATHER_API_KEY}', 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metar_data = response.json()
        visibility = int(metar_data['visibility']['value'])
        ceiling = int(metar_data['clouds'][0]['altitude']) if metar_data['clouds'] else 9999
        return determine_flight_category(visibility, ceiling)
    else:
        return None, None
    
def get_airports_within_radius(airports_csv, lat, lon, radius_nm):
    results = []
    with open(airports_csv, newline='') as csvfile:
        airport_reader = csv.reader(csvfile, delimiter=',')
        for row in airport_reader:
            icao, name, airport_lat, airport_lon = row
            airport_lat, airport_lon = float(airport_lat), float(airport_lon)
            distance = haversine((lat, lon), (airport_lat, airport_lon), unit=Unit.NAUTICAL_MILES)
            if distance <= radius_nm:
                category, color = get_metar_data(icao)
                if category:
                    results.append((icao, name, category, color, distance))
    return results

@app.route('/')
def index():
    airports_csv = "airports_new.csv"
    airports = get_airports_within_radius(airports_csv, OKC_LAT, OKC_LON, RADIUS_NM)
    airports = sorted(airports, key=lambda x: x[4])  # Sort results based on distance
    return render_template('index.html', airports=airports)
    
if __name__ == "__main__":
    app.run(debug=True)


