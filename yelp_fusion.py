'''
Using Yelp Fusion API

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

import json
import requests
from rauth import OAuth2Service
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
Updates global categories dict with aliases, titles, and business ids.
- aliases is list of the category aliases as per Yelp docs
- title is official name for display
- id is business id for businesses that belong to category, businesses can be in multiple categories.
returns categories dict
'''
def update_categories(dict_input, categories):
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
def get_businesses_from_file(business_list): 
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
def search_business(business_name, token):
    search_url = 'https://api.yelp.com/v3/businesses/search?location=nyc&term='+business_name+'&limit=1'
    headers = {
        'Authorization': 'Bearer %s' % token
    }
    r = requests.get(search_url, headers=headers)
    return r.json()

# Takes a list of business names, adds them to business_list(To do) and sends info on category to update_categories to update that dict
# todo: account for no results being found
def get_business_info(business_names, token):
    assert type(business_names) is list
    business_info = {}
    categories = {}
    try:
        for item in business_names:
            business = search_business(item, token)
            # only enter into new_entry if not closed
            # check if entry exists, if not put into "cannot find" file
            # Only process if business is still open
            if business['total'] == 0:
                print(item+" not found.")
            else:
                business = business['businesses'][0]
                print(business['id'])
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
                    categories = update_categories({'aliases': aliases, 'titles': titles, 'id': business['id']}, categories)
                    business_info[business['id']] = business_entry
    except AssertionError:
        print("Invalid: Argument for get_business_info must be list")
    # Puts categories into file
    categories_file = open('categories_output.json', 'w')
    json.dump(categories, categories_file)
    categories_file.close()
    return business_info

def main():
    restaurant_file = "restaurants.txt"
    credentials = get_credentials()
    token = credentials['access_token']
    businesses = get_businesses_from_file(restaurant_file)
    business_info = get_business_info(businesses, token)

    business_file = open('output_test.json', 'w')
    json.dump(business_info, business_file)
    business_file.close()

if __name__ == '__main__':
    main()


# print(search_business("swelt generation"))
# print(search_business("hotel chantel")