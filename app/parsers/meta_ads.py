import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_meta_ads_mock():
    file_path = DATA_DIR / "meta_ads_mock.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
