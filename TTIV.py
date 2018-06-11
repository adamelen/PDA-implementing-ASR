import requests
import json

def TTIV(access_token, base_url, text):
    ''' Sends a request to wit.ai that includes the "text", gets a response, and extracts an intent and its parameters'''

    # request - response
    headers = {'authorization': 'Bearer ' + access_token}
    resp = requests.get(base_url % text, headers = headers)
    data = json.loads(resp.content) 
    
    # extract intent and parameters
    parameters = {}
    for key in data['entities'].keys():
        if (key == 'keywords'):
            intent = (((data['entities'])[key])[0])['value']
        else:
            if ((((data['entities'])[key])[0])['type']=='interval'):
                parameters[key] = {}
                (parameters[key])['from'] = (((data['entities'])[key])[0])['from']['value']
                (parameters[key])['to'] = (((data['entities'])[key])[0])['to']['value']
            else:
                parameters[key] = (((data['entities'])[key])[0])['value']
    return (intent, parameters)
