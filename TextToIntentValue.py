import requests
import json

class TextToIntentValue:
    ''' A <<Proxy>> class that communicates with wit.ai in order to split a text to an intent-value pair '''

    def __init__(self, access_token, base_url):
        self.access_token = access_token
        self.base_url = base_url

    def TTIV(self, vc):
        # request - response
        headers = {'authorization': 'Bearer ' + self.access_token}
        resp = requests.get(self.base_url % vc.text, headers = headers)
        data = json.loads(resp.content) 
    
        # extract intent and parameters
        intent = ''
        parameters = {}
        if 'entities' in data:
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

        vc.intent = intent
        vc.parameters = parameters
        return vc
