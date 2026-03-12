import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_niche_products():
    file_path = DATA_DIR / "niche_products.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
