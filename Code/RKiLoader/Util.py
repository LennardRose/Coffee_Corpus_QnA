import json
import time
from datetime import datetime


def replace_all_mutated_vowels(json_object):
    """Replaces all 'Umlaute' or mutated vowels in a json object
        does this by converting to string and then replacing and then back to json object


        Args:
            json_object (dict): json object you want to filter

        Returns:
            dict: filtered json object
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


def current_milli_time():
    """get current time in milliseconds
    Returns:
        int: current time milliseconds
    """
    return round(time.time() * 1000)


def round_time_milli_to_day(timestamp, milli_flag):
    """round a timestamp to the next lower day

    Args:
        timestamp (int): the timestamp, can be milliseconds
        milli_flag (bool): wether timestamp is in milliseconds

    Returns:
        int: timestamp rounded to day
    """
    if milli_flag:
        timestamp = timestamp/1000
    dt = datetime.fromtimestamp(timestamp)
    # First zero out seconds and micros
    dt_rounded = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if milli_flag:
        return int(dt_rounded.timestamp() * 1000)
    else:
        return int(dt_rounded.timestamp())


def get_current_date():
    """get current date in YYYY_MM_DD format

    Returns:
        string: date in the above mentioned format as string
    """
    return datetime.today().strftime('%Y_%m_%d')
