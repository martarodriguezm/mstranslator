# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import datetime
import json
try:
    basestring
except NameError:
    basestring = (str, bytes)


class AccessError(Exception):
    def __init__(self, response):
        self.status_code = response.status_code
        data = response.json()
        super(AccessError, self).__init__(data["message"])


class ArgumentOutOfRangeException(Exception):
    def __init__(self, message):
        self.message = message.replace('ArgumentOutOfRangeException: ', '')
        super(ArgumentOutOfRangeException, self).__init__(self.message)


class TranslateApiException(Exception):
    def __init__(self, message, *args):
        self.message = message.replace('TranslateApiException: ', '')
        super(TranslateApiException, self).__init__(self.message, *args)


class AccessToken(object):
    access_url = "https://api.cognitive.microsoft.com/sts/v1.0/issueToken"
    expire_delta = datetime.timedelta(minutes=9)  # Translator API valid for 10 minutes, actually

    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self._token = None
        self._expdate = None

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer " + self.token
        return r

    def request_token(self):
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-type': 'application/json',
        }
        resp = requests.post(self.access_url, headers=headers)
        if resp.status_code == 200:
            self._token = resp.text
            self._expdate = datetime.datetime.now() + self.expire_delta
        else:
            raise AccessError(resp)

    @property
    def expired(self):
        return datetime.datetime.now() > self._expdate

    @property
    def token(self):
        if not self._token or self.expired:
            self.request_token()
        return self._token


class Translator(object):
    api_url = "https://api.cognitive.microsofttranslator.com/"

    def __init__(self, subscription_key):
        self.auth = AccessToken(subscription_key)

    def make_url(self, action):
        return self.api_url + action + '?api-version=3.0'

    def make_request(self, action, params=None, json=None, headers=None, is_post=True):
        url = self.make_url(action)
        if(is_post):
            resp = requests.post(url, auth=self.auth, params=params, json=json, headers=headers)
        else:
            resp = requests.get(url, auth=self.auth, params=params, headers=headers)
        return self.make_response(resp)

    def make_response(self, resp):
        resp.encoding = 'UTF-8-sig'
        data = resp.json()

        if isinstance(data, basestring) and data.startswith("ArgumentOutOfRangeException"):
            raise ArgumentOutOfRangeException(data)

        if isinstance(data, basestring) and data.startswith("TranslateApiException"):
            raise TranslateApiException(data)

        return data

    def _translate(self, action, json, lang_from, lang_to, contenttype, category, include_alignment=False):
        if not lang_to:
            raise ValueError('lang_to parameter is required')
        if contenttype not in ('text/plain', 'text/html'):
            raise ValueError('Invalid contenttype value')

        params = {
            'to': lang_to,
            'category': category,
            'includeAlignment': 'true' if include_alignment else 'false'
        }

        if lang_from:
            params['from'] = lang_from

        return self.make_request(action, params, json)

    def translate(self, text, lang_from=None, lang_to=None,
                  contenttype='text/plain', category='general'):
        json = [{
            'Text' : text
        }]
        response = self._translate('translate', json, lang_from, lang_to,
                               contenttype, category)
        if 'error' in response:
            raise ArgumentOutOfRangeException(response['error']['message'])
        else:
            return response[0]['translations'][0]['text']

    def translate_array(self, texts=[], lang_from=None, lang_to=None,
                        contenttype='text/plain', category='general'):
        json = [
            {'Text' : text} for text in texts
        ]
        return self._translate('translate', json, lang_from, lang_to,
                               contenttype, category)

    def translate_array2(self, texts=[], lang_from=None, lang_to=None,
                        contenttype='text/plain', category='general'):
        json = [
            {'Text' : text} for text in texts
        ]
        return self._translate('translate', json, lang_from, lang_to,
                               contenttype, category, include_alignment=True)

    def break_sentences(self, text, lang):
        if len(text) > 10000:
            raise ValueError('The text maximum length is 10000 characters')
        params = {
            'language': lang,
        }
        json = [
            {'Text': text}
        ]
        lengths = self.make_request('breaksentence', params, json)
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        c = 0
        result = []
        for i in lengths[0]['sentLen']:
            result.append(text[c:c+i])
            c += i
        return result

    def get_langs(self):
        params = {
            'scope': 'translation'
        }

        response = self.make_request('languages', params, is_post=False)
        result = [lang for lang in response['translation']]
        return result

    def get_lang_names(self, langs, lang_to):
        params = {
            'scope': 'translation'
        }
        headers = {
            'Accept-Language': lang_to
        }
        response = self.make_request('languages', params, headers=headers, is_post=False)
        result = []
        for lang in langs:
            if lang in response['translation']:
                result.append(response['translation'][lang]['name'])
        return result

    def detect_lang(self, text):
        json = [
            {'Text': text}
        ]
        response = self.make_request('detect', json=json)
        return response[0]["language"]

    def detect_langs(self, texts=[]):
        json = [
            {'Text' : text} for text in texts
        ] 
        response = self.make_request('detect', json=json)
        parsedResponse = [ 
            language["language"] for language in response
        ]
        return parsedResponse
