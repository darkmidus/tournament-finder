import pysmashgg
from geopy.geocoders import Nominatim
from datetime import datetime
# Asks the user for the starting location
locationAddress = input("What is the location: ")

# Grabs the lat/lon of address given
geolocator = Nominatim(user_agent="MyApp")
location = geolocator.geocode(locationAddress)

# Initialize the SmashGGPy class
smash = pysmashgg.SmashGG('be71a5a727a0ec1ff01980dffcfb2958')

# Shows tournaments by radius around a point
# NOTE: page_num is the third arg, allowing you to do your own pagination
tournaments_by_radius = smash.tournament_show_by_radius(str(location.latitude) + "," + str(location.longitude), '50mi', 1)

start_date = datetime.fromtimestamp(int(tournaments_by_radius[0]["startTimestamp"]))

# format of date/time strings; assuming dd/mm/yyyy
now = datetime.now()

if start_date < now:
    print("Event in the past")
elif start_date > now:
    print("Event in the future")

