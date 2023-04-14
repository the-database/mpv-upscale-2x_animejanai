import configparser
import os


def read_config():
    bools = {
        'logging',
        'upscale_4x',
        'resize_720_to_1080_before_first_2x',
        'upscale_2x',
        'resize_to_1080_before_second_2x',
        'rife'
    }
    floats = {
        'resize_factor_before_first_2x',
        'resize_height_before_first_2x'
    }

    parser = configparser.ConfigParser()
    conf = {}
    parser.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./animejanai_v2.conf"))

    for section in parser.sections():

        if section not in conf:
            conf[section] = {}

        for key in parser[section]:
            if key in bools:
                conf[section][key] = True if parser[section][key].casefold() == 'yes'.casefold() else False
            elif key in floats:
                conf[section][key] = float(parser[section][key])
            else:
                conf[section][key] = parser[section][key]

    return conf
