# coding=utf-8

import ConfigParser
import requests
import json
import codecs
from places import places

def pharmacy(parameters):
    ''' Sends a request to google API "Places" to find pharmacies in a certain region and returns a text that contains names and addresses of these pharmacies'''

    textToTell = places(parameters, 'pharmacy', 'pharmacies')
    return textToTell
