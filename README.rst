==============================================
mstranslator: Microsoft Translator API wrapper
==============================================

.. image:: https://travis-ci.org/wronglink/mstranslator.png?branch=master
   :target: https://travis-ci.org/wronglink/mstranslator
   :alt: Travis-ci: continuous integration status.

.. image:: https://badge.fury.io/py/mstranslator.png
   :target: http://badge.fury.io/py/mstranslator
   :alt: PyPI version

Installation
============

Install with pip:

.. code-block:: console

    $ pip install mstranslator

Usage
=====

1. Subscribe to the Translator API
----------------------------------
To access Translator API you need a `Microsoft Azure`_ account. Note that subscriptions,
up to 2 million characters a month, are free. Translating more than 2 million characters per
month requires a payment.

2. Add Translator subscription to your Azure account
----------------------------------------------------
1. Select the **+ New** -> **Intelligence + analytics** -> **Cognitive Services APIs**.
2. Select the **API Type** option.
3. Select either **Text Translation** or **Speech Translation**.﻿Select the pricing tier that fits your needs.
4. Fill out the rest of the form, and press the **Create** button. You are now subscribed to Microsoft Translator.
5. Now retrieve your subscription key for authentication. You can find it in **All Resources** -> **Keys** option.

That's all. Now you have a Subscription Key and can use Microsoft Translator API.

Example Usage:

.. code-block:: pycon

    >>> from mstranslator import Translator
    >>> translator = Translator('<Subscription Key>')
    >>> print(translator.translate('Привет, мир!', lang_from='ru', lang_to='en'))
    Hello World!

3. Translator Text API V2 to V3 Migration
-----------------------------------------

Translator Text API V2 was deprecated on April 30, 2018 and will be discontinued on April 30, 2019. So this API wrapper has been updated to V3 API version.

Microsoft has moved some features to other APIs and other are not longer supported. Check the official `Translator Text API V2 to V3 Migration`_ documentation for details.

With this update we have tried to keep the functions input and output as they were, but it has not been posible in all cases.

No changes needed for:

- translate
- break_sentences
- get_langs
- get_lang_names
- detect_lang
- detect_langs

Output has changed for:

- translate_array: The output json is different, check official docs for details
- translate_array2: The output json is different, check official docs for details

Input has changed for:

- get_langs: speakable input parameter has been removed

Following functions have been removed because the API features have been moved to other APIs:

- get_translations
- add_translation
- speak
- speak_to_file


Testing
=======
To run tests you need to set ``TEST_MSTRANSLATOR_SUBSCRIPTION_KEY`` environment variable
and install `tox`_ package. After that run shell command:

.. code-block:: console

    $ tox

.. _Microsoft Azure: http://azure.com
.. _tox: http://tox.readthedocs.org/en/latest/
.. _Translator Text API V2 to V3 Migration: https://docs.microsoft.com/en-us/azure/cognitive-services/translator/migrate-to-v3
