# coding=utf-8

import ConfigParser
import requests
import json
from Service import Service
from HospitalService import HospitalService
from PharmacyService import PharmacyService

class PlaceServiceAdapter(Service):
    ''' A class that acts as an adapter between Service and place interfaces (like GooglePlaceService) '''

    def __init__(self, place_type):
        # get information from config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        self.tz_base_url = config.get('TIMEZONE', 'BASE_URL')
        self.tz_app_id = config.get('TIMEZONE', 'APP_ID')
        self.loc_base_url = config.get('PLACES', 'FIND_LOCATION_BASE_URL')
        self.GooglePlaceServices = {
            'hospital': lambda: HospitalService(),
            'pharmacy': lambda: PharmacyService()
            }
        self.APIs = {
            'googlePlaces': lambda: self.GooglePlaceServices[place_type]()
            }
        self.p = self.APIs[config.get('PLACES','CHOOSE_API')]()
        self.responses = {
            'el':
            [u"Η ακτίνα γύρω από την τοποθεσία σου στην οποία βρέθηκαν τα παραπάνω αποτελέσματα είναι 3 χιλιόμετρα. Αν θέλεις τα αποτελέσματα να είναι μέσα σε κάποια άλλη ακτίνα από την τοποθεσία σου, δήλωσέ το στο ερώτημά σου.",
             u"Δε βρέθηκε κάποιο αποτέλεσμα"],
            'en':
            ["The distance around your location in which the above places were found is 3 kilometers. If you want to get results about places in another distance from your location, specify it in your query.",
             "No results found"]
            }

    def find_coordinates(self, city_name):
        ''' Find the coordinates of the given city '''
        geocode_url = "{}geocode/json?address={}&key={}".format(self.tz_base_url, city_name.capitalize(), self.tz_app_id)
        gcresp = requests.get(geocode_url)
        gcdata = gcresp.json()
        lat = ((((gcdata['results'])[0])['geometry'])['location'])['lat']
        lng = ((((gcdata['results'])[0])['geometry'])['location'])['lng']
        return (lat, lng)

    def getInfo(self, vc, trl, lang):

        if ('location' in vc.parameters):
            if  ('near' in vc.parameters['location'] or 'here' in vc.parameters['location']):
                del vc.parameters['location']  # because wit.ai stores words like "nearby" in "location", but I don't want this to happen

        addText = ''  # text to add to the textToTell in order to inform the user for any parameters he could add
        city_name = ''  # in all but one cases city_name is an empty string
        if 'location' not in vc.parameters:
            # find user's location
            loc_resp = requests.get(self.loc_base_url)
            loc_data = json.loads(loc_resp.text)
            loc = (str(loc_data['lat']), str(loc_data['lon']))
            if 'distance' in vc.parameters: #  an example input for that case: "hospitals 10 km away"
                dist = vc.parameters['distance']*1000
            else:                          # ex: "hospitals here"
                dist = 3*1000  # use a default distance
                addText = self.responses[lang][0]
        else:
            if 'distance' in vc.parameters: # ex: "hospitals 10 km away from Athens")
                loc = self.find_coordinates(vc.parameters['location'])
                dist = vc.parameters['distance']*1000
            else:                           # ex: "hospitals in Athens"
                loc = (0, 0)
                dist = 0
                city_name = vc.parameters['location']

        place_list = self.p.getPlaceInfo(loc, dist, city_name, lang)
        if (len(place_list)==0):
            vc.textToTell = self.responses[lang][1]
        else:
            textToTell = ""
            for place in place_list:
                textToTell = u"{}- {} - {} - {}\n  {}\n".format(textToTell, place['name'], place['address'], place['phone_number'], place['open_now'])
            # translate some words that might not be in the right langauge (like the name of the place or its address) 
            if (lang == 'el'):
                textToTell = trl.translate(textToTell, 'en', 'el')
            else:
                textToTell = trl.translate(textToTell, 'el', 'en')
            vc.textToTell = textToTell + addText
        return vc
