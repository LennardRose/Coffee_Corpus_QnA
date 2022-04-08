import requests
import json
import pandas as pd
from Config import *


def round_unix_date(timestamp, seconds=60, up=False):
    """
    Takes an unix timestamp and rounds it up or down to the provided amount of seconds
    Standard = 60 meaning to the minute
    :param timestamp:
    :param seconds: the amount of seconds you want to round up or down to
    :param up: whether you wand to round up or down
    :return: the rounded timestamp
    """
    return timestamp // seconds * seconds + seconds * up


def round_down_timestamp_to_day(timestamp):
    """
    wrapper to round a timestamp down to a day
    :param timestamp:
    :return: rounded timestamp
    """
    return round_unix_date(timestamp, 60 * 60 * 24)


def round_up_timestamp_to_day(timestamp):
    """
    wrapper to round a timestamp down to a day
    :param timestamp:
    :return: rounded timestamp
    """
    return round_unix_date(timestamp, 60 * 60 * 24, True)


def replace_all_mutated_vowels(json_object):
    """
    Replaces all 'Umlaute' or mutated vowels in a json object
    does this by converting to string and then replacing and then back to json object
    :param json_object: json object you want to filter
    :return: filtered json object
    """
    string = repr(json_object)
    string = string.replace(chr(252), 'ue')
    string = string.replace(chr(246), 'oe')
    string = string.replace(chr(228), 'ae')
    string = string.replace(chr(214), 'Oe')
    string = string.replace(chr(220), 'Ue')
    string = string.replace(chr(196), 'Ae')
    string = string.replace('\'', '"')
    return json.loads(string)


def download_weather_data_from_api(city, api_key):
    """
    download weather data for a specific city through openweatherapi with a rest request
    :param city: the city the weather data should be about
    :return: the weather data as a json object
    """
    build_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + \
        city + '&appid=' + api_key + '&units=metric'
    print(build_url)
    print(requests.utils.quote(build_url))
    res = requests.get(build_url).json()
    res = replace_all_mutated_vowels(res)
    print(res)
    res['dt'] = round_down_timestamp_to_day(res['dt'])
    return res
