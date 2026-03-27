# config.py
import os
from typing import Set
from dotenv import load_dotenv

load_dotenv()

# Environment variables
TOKEN = os.getenv("DISCORD_TOKEN")


def _parse_admin_ids(raw: str | None) -> Set[int]:
    ids: Set[int] = set()
    if not raw:
        return ids
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return ids


# Comma-separated Discord user IDs, e.g. "123,456,789"
ADMIN_IDS: Set[int] = _parse_admin_ids(os.getenv("ADMIN_IDS"))

# Constants (can be overridden via env if needed)
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "txt-upload-channel")
CLASS_TRANS_FILE = os.getenv("CLASS_TRANS_FILE", "class_translations.json")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)