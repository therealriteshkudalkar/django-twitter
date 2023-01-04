import math


def int_to_string(value):
    if value < 1000:
        return str(value)
    suffixes = ["", "K", "M", "B", "T"]
    suffix_num = math.floor(len(str(value)) / 3)
    short_value = round(float(((value / pow(1000, suffix_num)) if suffix_num != 0 else value)), 2)
    if short_value % 1 != 0:
        short_value = round(short_value, 1)
    return str(short_value) + str(suffixes[suffix_num])
