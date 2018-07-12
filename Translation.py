# coding=utf-8

import requests
import json

class Translation:
    ''' A <<Proxy>> class that communicates with a translation API (https://translate.yandex.net) '''

    def __init__(self, base_url, app_id):
        self.base_url = base_url
        self.app_id = app_id

    def translation(self, text, lang_from, lang_to):
        ''' Takes a text as input and translates it from "lang_from" to "lang_to" '''
        translation_url = "{}key={}&text={}&lang={}-{}".format(self.base_url, self.app_id, text, lang_from, lang_to)
        tresp = requests.get(translation_url)
        tdata = tresp.json()
        text = tdata['text'][0]
        return text        
    
