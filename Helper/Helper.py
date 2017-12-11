import re


def get_duration_from_time_string(str_time):
    """
    Convert the time string to minutes (in int)
    :param str_time: layout: xxh xxmin
    :return: int
    """
    matchs = re.findall(r"(?:(\d*)h[^\d]*)?(?:(\d*)min)?", str_time)
    hours, mins = matchs[0]
    return int(hours or '0') * 60 + int(mins or '0')
