# handle map functionality

import googlemaps
import json

# Imports credentials from maps_keys.txt
api_keys = {}
with open('maps_keys.txt', 'r') as f:
    for line in f:
        line_split = line.split()
        api_keys[line_split[0]] = str(line_split[1])

gmaps_key = api_keys['API_KEY']

gmaps = googlemaps.Client(key = gmaps_key)

