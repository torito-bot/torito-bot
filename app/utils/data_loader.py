import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str):
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
