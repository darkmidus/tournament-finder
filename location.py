import pysmashgg
from geopy.geocoders import Nominatim
from datetime import datetime
from pprintpp import pprint

# Grabs the lat/lon of address given
geolocator = Nominatim(user_agent="MyApp")
location = geolocator.geocode('hattiesburg mississippi')

# Initialize the SmashGGPy class
smash = pysmashgg.SmashGG('be71a5a727a0ec1ff01980dffcfb2958')

# Shows tournaments by radius around a point
# NOTE: page_num is the third arg, allowing you to do your own pagination
page_num = 1
tournaments_by_radius = smash.tournament_show_by_radius(str(location.latitude) + "," + str(location.longitude), '300mi', page_num)

def tournament_looper():
    future_tournaments = []
    for x in tournaments_by_radius:
        if datetime.fromtimestamp(int(x["startTimestamp"])) > datetime.now():
            future_tournaments += [x]
        if len(future_tournaments) % len(tournaments_by_radius) == 0:
            return page_num += 1



pprint(len(future_tournaments))
print(page_num)
