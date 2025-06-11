import os
import json
import platform


def get_base_dir():
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ["APPDATA"], "Stashly")
    else:
        base_dir = os.path.expanduser("~/.stashly")

    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def get_data_file_path():
    base_dir = get_base_dir()

    # Ensure main data file exists
    file_path = os.path.join(base_dir, "data.json")
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)

    return file_path

def get_cache_dir():
    base_dir = get_base_dir()
    cache_dir = os.path.join(base_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir