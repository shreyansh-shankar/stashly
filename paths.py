import os
import json
import platform
import shutil



def get_base_dir():
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ["APPDATA"], "Stashly")
    else:
        base_dir = os.path.expanduser("~/.stashly")

    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def get_icons_dir():
    icon_dir = os.path.join(get_base_dir(), "icons")
    os.makedirs(icon_dir, exist_ok=True)
    return icon_dir

def get_icon_mapping_file():
    return os.path.join(get_base_dir(), "icons.json")

def load_icon_mapping():
    path = get_icon_mapping_file()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_icon_mapping(mapping):
    with open(get_icon_mapping_file(), 'w') as f:
        json.dump(mapping, f, indent=2)

def slugify(text):
    return "".join(c if c.isalnum() else "_" for c in text.lower())

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