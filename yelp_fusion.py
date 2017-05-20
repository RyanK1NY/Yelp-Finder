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

- restaurants dict = {'name':"name", 'address':"display address entire list", 'categories': "category ids" }
- categories dict = {'category'}

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

'''
def update_dict(dict_input, item):
    assert type(dict_input) is dict
    try:
        if item not in dict_input:
            dict_input[item]
'''

def update_categories(dict_input):
    assert type(dict_input) is dict
    assert 'aliases' in dict_input
    assert 'titles' in dict_input
    assert 'id' in dict_input
    try:
        for index, value in enumerate(dict_input['aliases']):
            if value not in categories:
                categories[value] = {
                    'title': dict_input['titles'][index],
                    'businesses': [dict_input['id']]
                }
            else:
                categories[value]['businesses'].append(dict_input['id'])
    except AssertionError:
        print("Argument to update_categories must be a dict")
    except KeyError:
        print("Input to update_categories missing key")
    return categories


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

# Takes a list of business names, adds them to business_list(To do) and sends info on category to update_categories to update that dict
def get_business_info(business_names):
    assert type(business_names) is list
    business_info = {}
    try:
        for item in business_names:
            business = search_business(item)
            # only enter into new_entry if not closed
            # check if entry exists, if not put into "cannot find" file
            # Only process if business is still open
            business = business['businesses'][0]
            if business['is_closed'] is False:
                business_categories = business['categories']
                aliases = []
                titles = []

                for sub_category in business_categories:
                    aliases.append(sub_category['alias'])
                    titles.append(sub_category['title'])

                business_entry = {
                    'id': business['id'],
                    'name': business['name'],
                    'location': ' '.join(business['location']['display_address']),
                    'categories': aliases
                }
                update_categories({'aliases': aliases, 'titles': titles, 'id': business['id']})
                print(business_entry)
    except AssertionError:
        print("Invalid: Argument for get_business_info must be list")
    return business_names


# Searches business by id
def search_business(business_name):
    search_url = 'https://api.yelp.com/v3/businesses/search?location=nyc&term='+business_name+'&limit=1'
    headers = {
        'Authorization': 'Bearer %s' % token
    }
    r = requests.get(search_url, headers=headers)
    return r.json()



restaurant_file = "restaurants.txt"
credentials = get_credentials()
token = credentials['access_token']

categories = {}

business_info = get_business_info(['hotel chantel'])
business_file = open('output_test.json', 'w')
json.dump(business_info, business_file)
business_file.close()

categories_file = open('categories_output.json', 'w')
json.dump(categories, categories_file)
categories_file.close()

print(categories)
print("Done")
