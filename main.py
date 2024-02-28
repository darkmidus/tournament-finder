import pysmashgg
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy.distance import geodesic
from datetime import datetime
from time import sleep
from flask import Flask, redirect, url_for, request

app = Flask(__name__)
future_tournaments = []

# Initialize the SmashGGPy class
smash = pysmashgg.SmashGG("be71a5a727a0ec1ff01980dffcfb2958")
geolocator = Nominatim(user_agent="MyApp")


# NOTE: page_num is the third arg, allowing you to do your own pagination
def tournament_info(location, radius):
    try:
        address = geolocator.geocode(location)
        page_num = 1
        tournaments_by_radius = smash.tournament_show_by_radius(
            f'{address.latitude},{address.longitude}', radius, page_num)

        while True:
            for x in tournaments_by_radius:
                if datetime.fromtimestamp(int(x["startTimestamp"])) > datetime.now():
                    future_tournaments.append(x)

            if len(future_tournaments) % len(tournaments_by_radius) == 0:
                page_num += 1
                tournaments_by_radius = smash.tournament_show_by_radius(
                    f'{address.latitude},{address.longitude}', '150mi', page_num)
            else:
                break

            # Add a delay between requests to avoid overwhelming the SmashGG API
            sleep(1)

    except GeocoderUnavailable as e:
        # Handle geocoding service being unavailable
        print(f"GeocoderUnavailable: {e}")


@app.route('/results')
def display_tournaments():
    result = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }

            .container {
                max-width: 800px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }

            .title-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #4CAF50;  /* Green */
                color: white;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;  /* Added margin-bottom for a small gap */
            }

            .title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
            }

            .tournament {
                border: 3px solid black;
                border-radius: 4%;
                aspect-ratio: 1 / 0.9;
                padding: 10px;
                text-align: center;
                margin-bottom: 10px;
                background-color: #f9f9f9;  /* Light gray */
            }

            a {
                text-decoration: none;
                color: inherit;
            }

            .back-button {
                padding: 10px;
                background-color: #3498db;  /* Blue */
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
        <title>Nearest Tournaments</title>
    </head>
    <body>
        <div class="container">
            <div class="title-container">
                <div class="title">Nearest Tournaments</div>
                <a href="/" class="back-button">Back to Search</a>
            </div>
    '''
    original_location = geolocator.geocode(request.args.get('location'))

    for tournament in future_tournaments:
        time = datetime.fromtimestamp(int(tournament["startTimestamp"]))

        try:
            tournament_location = geolocator.geocode(tournament["city"] + ", " + tournament["state"], timeout=10)

            if tournament_location is not None:
                tournament_latitude = float(tournament_location.latitude)
                tournament_longitude = float(tournament_location.longitude)

                distance = geodesic((original_location.latitude, original_location.longitude),
                                    (tournament_latitude, tournament_longitude)).miles

                result += (
                    f'<a href="https://www.start.gg/tournament/{tournament["slug"]}">'
                    f'<div class="tournament">'
                    f'{tournament["name"]} <hr> Location: {tournament["city"]}, {tournament["state"]} <hr> Entrants: {tournament["entrants"]} <hr> Date: {time.strftime("%I:%M%p %m-%d-%Y")} <hr> Distance: {distance:.2f} miles'
                    f'</div></a>'
                )
            else:
                result += (
                    f'<div class="tournament">'
                    f'{tournament["name"]} <hr> Location: {tournament["city"]}, {tournament["state"]} <hr> Entrants: {tournament["entrants"]} <hr> Date: {time.strftime("%I:%M%p %m-%d-%Y")} <hr> Distance: Not Available'
                    f'</div>'
                )

        except GeocoderUnavailable as e:
            # Handle geocoding service being unavailable
            print(f"GeocoderUnavailable: {e}")
            result += (
                f'<div class="tournament">'
                f'{tournament["name"]} <hr> Location: {tournament["city"]}, {tournament["state"]} <hr> Entrants: {tournament["entrants"]} <hr> Date: {time.strftime("%I:%M%p %m-%d-%Y")} <hr> Distance: Not Available (Geocoder Unavailable)'
                f'</div>'
            )

        # Add a delay between requests to avoid overwhelming the geocoding service
        sleep(0.5)

    result += '''
        </div>
    </body>
    </html>
    '''
    return result


@app.route('/', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        try:
            location = request.form['location']
            radius = request.form['radius']

            if not location or not radius:
                return "Please enter both a location and a radius."
            future_tournaments.clear()
            tournament_info(location, radius)
            return redirect(url_for('display_tournaments', location=location))

        except Exception as e:
            return f"An error occurred: {e}"

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }

            form {
                background-color: #e6e6e6;  /* Lighter gray */
                padding: 20px;
                border-radius: 10px;
                max-width: 400px;
                margin: auto;
            }

            .title {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 20px;
                background-color: #3498db;  /* Blue */
                color: white;
                padding: 10px;
                border-radius: 10px;
            }

            label {
                color: #8e44ad;  /* Purple */
                display: block;
                margin-bottom: 5px;
            }

            input {
                width: 100%;
                box-sizing: border-box;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
            }

            input[type="submit"] {
                width: 100%;
                box-sizing: border-box;
                border-radius: 5px;
                padding: 10px;
                background-color: #3498db;  /* Blue */
                color: white;
                cursor: pointer;
            }

            @media (min-width: 768px) {
                form {
                    max-width: 600px;
                }
            }
        </style>
        <title>Tournament Finder</title>
    </head>
    <body>
        <div class="title">Tournament Finder</div>
        <form method="post">
            <label for="location">Location:</label>
            <input type="text" id="location" name="location">
            <label for="radius">Radius:</label>
            <input type="text" id="radius" name="radius">
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
