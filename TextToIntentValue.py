import requests
import json

class TextToIntentValue:
    ''' A <<Proxy>> class that communicates with wit.ai in order to split a text to an intent-value pair '''

    def __init__(self, access_token, base_url):
        self.base_url = base_url
        self.headers = {'authorization': 'Bearer ' + access_token}

    def TTIV(self, vc):
        # request - response
        resp = requests.get(self.base_url % vc.text, headers = headers)
        data = json.loads(resp.content) 
    
        # extract intent and parameters
        parameters = {}
        for key in data['entities'].keys():
            if (key == 'keywords'):
                intent = (((data['entities'])[key])[0])['value']
            else:
                if key == 'datetime':
                    if ((((data['entities'])[key])[0])['type']=='interval'):
                        parameters[key] = {}
                        (parameters[key])['from'] = (((data['entities'])[key])[0])['from']['value']
                        (parameters[key])['to'] = (((data['entities'])[key])[0])['to']['value']
                    else:
                        parameters[key] = (((data['entities'])[key])[0])['value']
                else:
                    parameters[key] = (((data['entities'])[key])[0])['value']

        # save intent and parameters to the respective attributes of VoiceCommand
        vc.intent = intent
        vc.parameters = parameters
        return vc
