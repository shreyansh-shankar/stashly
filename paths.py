import os
import json
import platform

def get_data_file_path():
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ["APPDATA"], "Stashly")
    else:
        base_dir = os.path.expanduser("~/.stashly")

    os.makedirs(base_dir, exist_ok=True)
    file_path = os.path.join(base_dir, "data.json")

    # Create file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)  # Start with empty list

    return file_path
