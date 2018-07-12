# coding=utf-8

import ConfigParser
import requests
import json
import codecs
from Service import Service

class Places(Service):
    ''' A <<Proxy>> class that implements the abstract class Service in order to get info about places (like hospitals, pharmacies) '''

    def __init__(self, place_type, place_type_pl):
        self.place_type = place_type
        self.place_type_pl = place_type_pl
        # get information from config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        self.base_url = config.get('PLACES', 'PLACES_BASE_URL')
        self.app_id = config.get('PLACES', 'APP_ID')
        self.loc_base_url = config.get('PLACES', 'FIND_LOCATION_BASE_URL')
        

    def getInfo(self, vc, trl):
        ''' Sends a request to google API "Places" to find places of type place_type in a certain region and returns a text that contains names and addresses of these places'''

        if ('location' in vc.parameters):
            if  ('near' in vc.parameters['location']):
                del vc.parameters['location']  # because wit.ai stores words like "nearby" in "location", but I don't want this to happen
    
        # Find places in 'location'
        if 'location' in vc.parameters:
            location = vc.parameters['location']
            query = "{}+in+{}".format(self.place_type_pl, location)
            place_url = "{}textsearch/json?query={}&key={}".format(self.base_url, query, self.app_id)
            place_resp = requests.get(place_url)
            place_data = json.loads(place_resp.content)
            results = place_data['results']
            textToTell = ""
            for res in results:
                textToTell = textToTell + res['name'] + " - " + res['formatted_address'] + "\n"

        # Find places in a range=dist around user's location
        else:
            if 'distance' in vc.parameters:    # distance must be in kilometers
                dist = vc.parameters['distance']
            elif vc.parameters=={}:
                dist = 3
            # find user's location through his IP, using the "ip-api.com"
            loc_resp = requests.get(self.loc_base_url)
            loc_data = json.loads(loc_resp.text)
            lat = str(loc_data['lat'])
            lng = str(loc_data['lon']) 
            location = lat+","+lng
            place_url = "{}nearbysearch/json?location={}&radius={}&name={}&type={}&key={}".format(self.base_url, location, str(dist*1000), self.place_type, self.place_type, self.app_id)
            place_resp = requests.get(place_url)
            place_data = json.loads(place_resp.content)
            results = place_data['results']
            textToTell = ""
            for res in results:
                textToTell = textToTell + res['name'] + " - " + res['vicinity'] + "\n"

        vc.textToTell = textToTell
        return vc    
