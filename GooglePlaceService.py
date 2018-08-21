# coding=utf-8

import ConfigParser
import requests
import json
from PlaceService import PlaceService

class GooglePlaceService(PlaceService):
    ''' A <<Proxy>> that communicates with the https://maps.googleapis.com/maps/api/place/ API and collects information about places in a certain region '''

    def __init__(self):
        self.place_type = None
        # get information from config file
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        self.base_url = config.get('PLACES', 'PLACES_BASE_URL')
        self.app_id = config.get('PLACES', 'APP_ID')
        self.responses = {
            'el':
            [u"Δε βρέθηκε διεύθυνση",
             u"Δε βρέθηκε τηλέφωνο",
             u"Ανοιχτό τώρα",
             u"Κλειστό τώρα",
             u"Δεν υπάρχουν πληροφορίες για το αν είναι ανοιχτό τώρα"],
            'en':
            ["Address not found",
             "Telephone number not found",
             "Open now",
             "Closed now",
             "There is no information about whether it is open now"]
            }

    def getPlaceInfo(self, loc, dist, city_name, lang):
        if city_name != '':  # find places in a city
            query = "query={}+in+{}".format(self.place_type, city_name)
            location = ''
            radius = ''
            ptype = ''
        else:  # find places within a radius around location
            query = ''
            location = "location={},{}".format(loc[0], loc[1])
            radius = "&radius={}".format(dist)
            ptype = "&type={}".format(self.place_type)
        place_url = "{}textsearch/json?{}{}{}{}&key={}".format(self.base_url, query, location, radius, ptype, self.app_id)
        place_resp = requests.get(place_url)
        place_data = json.loads(place_resp.content)
        results = place_data['results']
        if (len(results) == 0):
            return results
        # Results are stored in a list. Every position in the list contains a dictionary, which contains the name, address, phone number of a place of type place_type and whether it is open now
        place_list = []

        # Send a request for each one of the results above, in order to get the place's phone number
        for res in results:
            details_url = "{}details/json?placeid={}&fields=formatted_phone_number,opening_hours&key={}".format(self.base_url, res['place_id'], self.app_id)
            details_resp = requests.get(details_url)
            details_data = json.loads(details_resp.content)
            # check if the following fields exist in the result in order to avoid any errors
            if 'formatted_address' in res:
                address = res['formatted_address']
            else:
                address = self.responses[lang][0]
            if 'formatted_phone_number' in details_data['result']:
                phone_number = details_data['result']['formatted_phone_number']
            else:
                phone_number = self.responses[lang][1]
            if 'opening_hours' in details_data['result']:
                if (details_data['result']['opening_hours']['open_now']==True):
                    open_now = self.responses[lang][2]
                else:
                    open_now = self.responses[lang][3]
            else: 
                open_now = self.responses[lang][4]
            place_list.append({'name': res['name'], 'address': address, 'phone_number': phone_number, 'open_now': open_now})

        return place_list

