# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from StringIO import StringIO
except ImportError:
    # Python 3
    from io import BytesIO as StringIO

from mstranslator import AccessToken, AccessError, Translator, ArgumentOutOfRangeException
import requests

SUBSCRIPTION_KEY = os.environ['TEST_MSTRANSLATOR_SUBSCRIPTION_KEY']


class TranslatorMock(Translator):
    """
    A Translator mock that returns url on `.make_request()` method call without
    making a real HTTP request.
    """
    def make_request(self, action, params=None):
        prepped = requests.Request('GET',
                                   url=self.make_url(action),
                                   params=params).prepare()
        return prepped.url

class AccessTokenTestCase(unittest.TestCase):
    def test_access(self):
        at = AccessToken(SUBSCRIPTION_KEY)
        assert at.token

    def test_access_denied(self):
        at = AccessToken("AN_INVALID_SUBSCRIPTION_KEY")
        self.assertRaises(AccessError, at.request_token)


class TranslatorTestCase(unittest.TestCase):
    def setUp(self):
        self.translator = Translator(SUBSCRIPTION_KEY)
        self.translator_mock = TranslatorMock(SUBSCRIPTION_KEY)

    def test_translate(self):
        t = self.translator.translate('world', 'en', 'es')
        self.assertEqual('Mundo', t)

    def test_translate_exception(self):
        self.assertRaises(ArgumentOutOfRangeException, self.translator.translate, 'world', 'en', 'asdf')

    def test_translate_array(self):
        ts = self.translator.translate_array(['hello', 'world'], 'en', 'es')
        translations = [t['translations'][0]['text'] for t in ts]
        self.assertEqual(['Hola', 'Mundo'], translations)

    def test_translate_array2(self):
        ts = self.translator.translate_array2(['The answer lies in machine translation.'], 'en', 'es')
        translations = [t['translations'][0]['text'] for t in ts]
        self.assertEqual(['La respuesta radica en la traducción automática.'], translations)
        alignments = [t['translations'][0]['alignment']['proj'] for t in ts]
        self.assertEqual('0:2-0:1 4:9-3:11 11:14-13:18 16:17-20:21 19:25-37:46 27:37-26:35 38:38-47:47', alignments[0])

    def test_break_sentences(self):
        t = self.translator.break_sentences('Hello. How are you?', 'en')
        self.assertEqual(['Hello. ', 'How are you?'], t)

    def test_get_langs(self):
        langs = self.translator.get_langs()
        self.assertIsInstance(langs, list)
        self.assertIn('en', langs)

    def test_get_lang_names(self):
        lang_names = self.translator.get_lang_names(['ru', 'en'], 'en')
        self.assertEqual(['Russian', 'English'], lang_names)

    def test_detect_lang(self):
        self.assertEqual('en', self.translator.detect_lang('Hello'))

    def test_detect_langs(self):
        self.assertEqual(['en', 'ru'], self.translator.detect_langs(['Hello', 'Привет']))
