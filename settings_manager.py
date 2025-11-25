import os, json

DEFAULTS = {
    "lang": "pl",
    "music_volume": 0.2,
    "sfx_volume": 0.5,
}

def settings_path(base_dir):
    return os.path.join(base_dir, "settings.json")

def load_settings(base_dir, defaults=None):
    defaults = dict(defaults or DEFAULTS)
    path = settings_path(base_dir)
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            defaults.update(data)
        return defaults
    except Exception:
        return defaults

def save_settings(base_dir, settings_dict):
    path = settings_path(base_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings_dict, f, ensure_ascii=False, indent=2)
