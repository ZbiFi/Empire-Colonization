# localization.py
import json
import os
from typing import Any, Dict, Optional


class Localization:
    """
    Simple i18n loader.
    - loads locales/<lang>.json
    - fallback to pl, then to key
    - supports {placeholders} formatting
    """

    def __init__(self, lang: str = "pl", locales_dir: str = "loc", fallback_lang: str = "pl"):
        self.locales_dir = locales_dir
        self.fallback_lang = fallback_lang
        self.lang = lang
        self._data: Dict[str, Any] = {}
        self._fallback_data: Dict[str, Any] = {}
        self.load_language(lang)
        if fallback_lang != lang:
            self._fallback_data = self._load_file(fallback_lang)

    def _load_file(self, lang: str) -> Dict[str, Any]:
        path = os.path.join(self.locales_dir, f"{lang}.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_language(self, lang: str):
        self.lang = lang
        self._data = self._load_file(lang)

    def t(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        raw = self._data.get(key)
        if raw is None:
            raw = self._fallback_data.get(key)
        if raw is None:
            raw = default if default is not None else key

        if isinstance(raw, str) and kwargs:
            try:
                return raw.format(**kwargs)
            except Exception:
                return raw
        return raw if isinstance(raw, str) else str(raw)
