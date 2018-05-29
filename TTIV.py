import requests
import json

def TTIV(access_token, base_url, text):
    ''' Sends a request to wit.ai that includes the "text", gets a response, and extracts an intent and its value'''

    # request - response
    headers = {'authorization': 'Bearer ' + access_token}
    resp = requests.get(base_url % text, headers = headers)
    data = json.loads(resp.content) 
    
    # extract intent and value
    intent = (((data['entities'])['intent'])[0])['value']
    # edw, otan oloklhrw8oun ta intents, analoga me to intent pou vrhka 8a anazhtw to katallhlo value (p.x location, date etc)
    value = (((data['entities'])['location'])[0])['value']
    return (intent, value)
