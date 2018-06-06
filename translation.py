# coding=utf-8

import requests
import json

def translation(base_url, app_id, text, lang):
    '''Sends a text in a translation_API and returns translated text'''
    translation_url = base_url + 'key=' + app_id + '&text=' + text + '&lang=' + lang
    tresp = requests.get(translation_url)
    tdata = tresp.json()
    translated_text = tdata['text'][0]
    return translated_text
