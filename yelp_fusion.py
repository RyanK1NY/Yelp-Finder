'''
Using Yelp Fusion API
'''

import json
import requests
from rauth import OAuth2Service

'''
Workflow:
- access_token.txt contains token
- if token from file not valid, retrieve a token
- make request

- OAuth2 version WIP
example from https://github.com/litl/rauth/blob/master/docs/index.rst
yelp = OAuth2Service(
    client_id = credentials['client_id'],
    client_secret = credentials['client_secret'],
    name = 'yelp',
    base_url = 'https://api.yelp.com/v3/',
    authorize_url = 'https://api.yelp.com/v3/',
    access_token_url = 'https://api.yelp.com/oauth2/token'
)
'''
# Opens file and populates credentials dict
def get_credentials():
    api_keys = {}
    with open('yelp_keys.txt', 'r') as f:
        for line in f:
            line_split = line.split()
            api_keys[line_split[0]] = str(line_split[1])

    credentials = {
        'grant_type' : 'client_credentials',
        'client_id' : api_keys['CLIENT_ID'],
        'client_secret' : api_keys['CLIENT_SECRET']
    }

    try:
        ft = open('access_token.txt', 'r')
        for line in ft:
            access_token = str(line)
    # If file isn't found, runs refresh_token
    except IOError:
        access_token = refresh_token(credentials)
    credentials['access_token'] = access_token
    return credentials

# Refreshes token and writes it to a text file
def refresh_token(credentials):
    token_url = 'https://api.yelp.com/oauth2/token'
    r = requests.post(token_url, params={'client_id': credentials['client_id'], 'client_secret': credentials['client_secret']})
    token = r.json()
    f = open('access_token.txt', 'w')
    f.write(token['access_token'])
    return token['access_token']

# Get list of businesses from text file, separated by line, put into list and return
def get_businesses(business_list): 
    try:
        business_file = open(business_list, 'r')
    except IOError:
        print("File "+business_list+" not found")
    else:
        restaurant_names = []
        with business_file as f:
            for line in f:
                restaurant_names.append(line)
        return restaurant_names


# Searches business by id
def search_business(business_name):
    search_url = 'https://api.yelp.com/v3/businesses/search?location=nyc&term='+business_name
    headers = {
        'Authorization': 'Bearer %s' % token
    }
    r = requests.get(search_url, headers=headers)
    return r.json()

restaurant_file = "restaurants.txt"
credentials = get_credentials()
token = credentials['access_token']
restaurant_list = get_businesses(restaurant_file)