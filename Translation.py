# coding=utf-8

import requests
import json

class Translation:
    ''' A <<Proxy>> class that communicates with a translation api '''

    def __init__(self, base_url, app_id):
        self.base_url = base_url
        self.app_id = app_id

    def translate(self, text, lang_from, lang_to):
        translation_url = u'{}key={}&text={}&lang={}-{}'.format(self.base_url, self.app_id, text, lang_from, lang_to)
        tresp = requests.get(translation_url)
        tdata = tresp.json()
        text = tdata['text'][0]
        return text
