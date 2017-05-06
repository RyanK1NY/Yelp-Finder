# Uses Yelp v2 API, going to update to Yelp Fusion API
# 1) Have user enter comma separate list 
# 2) For each item in list, run request function
# 3) Pull relevant information into a dict, with each index pertaining to a restaurant
# 4) Put into text file
# 5) Use lat and lngs to make google maps route

import json
import rauth

'''
Makes call to Yelp API and returns results_list and locations_list
Takes in all API keys and dest2.txt
results_list is the entire response in a json file, goes into results.json
locations_list goes into the locations.csv to be imported into google maps
'''
def make_request(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET, input_list):
    session = rauth.OAuth1Session(
        consumer_key = CONSUMER_KEY,
        consumer_secret = CONSUMER_SECRET,
        access_token = TOKEN,
        access_token_secret = TOKEN_SECRET)
    
    locations_list = []
    
    for item in input_list:
        print(item)
        request = session.get(API_HOST, params={"term":item, "location":"nyc", "limit":"1"})
        data = request.json()
        
        if data:
            # If business is closed, doesn't add to results or location
            if data["businesses"][0]["is_closed"] is False:
                results_list.update({item:data["businesses"]})
                locations_list.append(data["businesses"][0]["name"] + ',' + ' '.join(data["businesses"][0]["location"]["display_address"]))
        else:
            locations_list.append(item)
        
    session.close()
    return results_list, locations_list[0:]

def run_yelp_v2():
    input_list = []

    with open('restaurants.txt') as f:
        for line in f:
            input_list.append(line)

    input_list = sorted(input_list, key=str.lower)
    results_list = {}
    output = open('results_from_api.json', 'w')

    API_HOST = "http://api.yelp.com/v2/search"

    # Imports credentials from yelp_keys.txt
    api_keys = {}
    with open('yelp_keys.txt', 'r') as f:
        for line in f:
            line_split = line.split()
            api_keys[line_split[0]] = str(line_split[1])

    CONSUMER_KEY = api_keys['CONSUMER_KEY']
    CONSUMER_SECRET = api_keys['CONSUMER_SECRET']
    TOKEN = api_keys['TOKEN']
    TOKEN_SECRET = api_keys['TOKEN_SECRET']

    results_list, locations_list = make_request(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET, input_list)
    json.dump(results_list, output)

    with open('locations_to_map.csv', 'w') as out_file:
        out_file.write('\n'.join(locations_list))