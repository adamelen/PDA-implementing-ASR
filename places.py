# coding=utf-8

import ConfigParser
import requests
import json
import codecs

def places(parameters, place_type, place_type_pl):
    ''' Sends a request to google API "Places" to find places of type place_type in a certain region and returns a text that contains names and addresses of these places'''

    # get information from config file
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    base_url = config.get('PLACES', 'PLACES_BASE_URL')
    app_id = config.get('PLACES', 'APP_ID')
    loc_base_url = config.get('PLACES', 'FIND_LOCATION_BASE_URL')

    if ('location' in parameters):
        if  ('near' in parameters['location']):
            del parameters['location']  # because wit.ai stores words like "nearby" in "location", but I don't want this to happen
    
    # Find places in 'location'
    if 'location' in parameters:
        location = parameters['location']
        query = place_type_pl + '+in+' + location
        place_url = base_url + 'textsearch/json?query=' + query + '&key=' + app_id
        place_resp = requests.get(place_url)
        place_data = json.loads(place_resp.content)
        results = place_data['results']
        textToTell = ""
        for res in results:
            textToTell = textToTell + res['name'] + " - " + res['formatted_address'] + "\n"

    # Find places in a range=dist around user's location
    else:
        if 'distance' in parameters:    # distance must be in kilometers
            dist = parameters['distance']
        elif parameters=={}:
            dist = 3
        loc_resp = requests.get(loc_base_url)
        loc_data = json.loads(loc_resp.text)
        lat = str(loc_data['latitude'])
        lng = str(loc_data['longitude']) 
        location = lat+","+lng
        place_url = base_url + 'nearbysearch/json?' + 'location=' + location + '&radius=' + str(dist*1000) + '&name=' + place_type + '&type=' + place_type + '&key=' + app_id
        place_resp = requests.get(place_url)
        place_data = json.loads(place_resp.content)
        results = place_data['results']
        textToTell = ""
        for res in results:
            textToTell = textToTell + res['name'] + " - " + res['vicinity'] + "\n"

    return textToTell

