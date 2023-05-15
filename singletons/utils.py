import os
import json
import pathlib

# Pulled this out as a solo function. Might be redundant.
def path_to_dict(dict_path):
    """Path goes in, dict comes out. Can't explain that."""
    if not os.path.isfile(dict_path):
        print("Config Not Found!")
    with open(dict_path) as json_file:
        some_dict = json.load(json_file)
    return some_dict


def get_local_content():
    base_dir = pathlib.Path(os.path.realpath(__file__)).parents[1] / 'cfg'


package = __package__.split(".")[0]