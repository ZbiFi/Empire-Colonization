# translation_audit.py
import os
import re
import json
from pathlib import Path

# ===== konfiguracja =====
# katalog z tłumaczeniami
LOC_DIR = Path("loc")

DEFAULT_LANG_FILES = {
    "pl": LOC_DIR / "pl.json",
    "en": LOC_DIR / "en.json",
    "de": LOC_DIR / "de.json",
}

# Regex na loc t("key") / self loc t('key')
LOC_T_RE = re.compile(
    r"""(?:self\.)?loc\.t\(\s*(?:[fr]?)?["']([^"']+)["']""",
    re.MULTILINE
)

# Regex na dynamiczne klucze f"xxx.{var}.yyy"
FSTRING_DYN_RE = re.compile(r"{[^}]+}")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def flatten(d, prefix=""):
    """Spłaszcza zagnieżdżone jsony do postaci key.subkey -> value."""
    out = {}
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, full))
        else:
            out[full] = v
    return out


def scan_code_keys(root: Path):
    """
    Zwraca:
      - keys: set kluczy statycznych
      - dynamic: set kluczy dynamicznych (z f-stringów)
    """
    keys = set()
    dynamic = set()

    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = Path(dirpath) / fn
            try:
                text = p.read_text(encoding="utf8")
            except Exception:
                continue

            for m in LOC_T_RE.finditer(text):
                key = m.group(1)

                if FSTRING_DYN_RE.search(key):
                    skeleton = FSTRING_DYN_RE.sub("{}", key)
                    dynamic.add(skeleton)
                    pref = skeleton.split("{}")[0].rstrip(".")
                    if pref:
                        dynamic.add(pref + ".*")
                    continue

                keys.add(key)

    return keys, dynamic


def audit_translations(project_root=".", lang_files=None):
    root = Path(project_root).resolve()
    lang_files = lang_files or DEFAULT_LANG_FILES

    # 1) klucze z kodu
    code_keys, dynamic_keys = scan_code_keys(root)

    # 2) klucze z jsonów
    flat = {}
    for lang, path in lang_files.items():
        data = load_json(root / path)
        flat[lang] = flatten(data)

    # 3) raport braków
    missing = {lang: sorted([k for k in code_keys if k not in flat[lang]]) for lang in flat}
    unused = {lang: sorted([k for k in flat[lang].keys() if k not in code_keys]) for lang in flat}

    return {
        "code_keys": sorted(code_keys),
        "dynamic_keys": sorted(dynamic_keys),
        "missing": missing,
        "unused": unused,
    }


def print_report(report):
    code_keys = report["code_keys"]
    dynamic_keys = report["dynamic_keys"]
    missing = report["missing"]
    unused = report["unused"]

    print("\n=== TRANSLATION AUDIT ===\n")
    print(f"Statyczne klucze w kodzie: {len(code_keys)}")
    print(f"Dynamiczne klucze (f-string): {len(dynamic_keys)}")
    if dynamic_keys:
        print("Dynamiczne przykłady:")
        for k in dynamic_keys[:20]:
            print("  -", k)
        if len(dynamic_keys) > 20:
            print("  ...")

    print("\n--- BRAKUJĄCE TŁUMACZENIA ---")
    any_missing = False
    for lang, keys in missing.items():
        if keys:
            any_missing = True
            print(f"\n[{lang}] brak {len(keys)} kluczy:")
            for k in keys:
                print("  -", k)
        else:
            print(f"\n[{lang}] OK (brak braków)")

    if not any_missing:
        print("\nBrak brakujących tłumaczeń 🎉")

    print("\n--- NIEUŻYWANE KLUCZE (opcjonalnie do sprzątania) ---")
    for lang, keys in unused.items():
        print(f"\n[{lang}] nieużywane: {len(keys)}")
        for k in keys[:30]:
            print("  -", k)
        if len(keys) > 30:
            print("  ...")

    print("\n=== KONIEC ===\n")


if __name__ == "__main__":
    rep = audit_translations(".")
    print_report(rep)
