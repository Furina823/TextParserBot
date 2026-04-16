# database.py
import json
import os
from datetime import datetime, timezone, timedelta
from config import DATA_DIR

def get_db_file(guild_id: int):
    """Get the database file path for a specific guild"""
    return os.path.join(DATA_DIR, f"{guild_id}.json")

def get_bindings_file(guild_id: int):
    """Get bindings file path for a specific guild"""
    return os.path.join(DATA_DIR, f"{guild_id}_bindings.json")

def get_gmt8_time():
    """Get current time in GMT+8 timezone"""
    gmt8 = timezone(timedelta(hours=8))
    return datetime.now(gmt8).strftime("%Y-%m-%d %H:%M:%S")

def normalize_username(username: str) -> str:
    """Normalize usernames for case-insensitive matching."""
    return username.strip().lower()

def save_to_db(data, uploader_name, upload_time, guild_id):
    """Save character data to guild-specific database"""
    db_file = get_db_file(guild_id)

    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = []

    data["uploaded_by"] = uploader_name
    data["uploaded_at"] = upload_time

    normalized_username = normalize_username(data.get("username", ""))

    # Remove duplicate entries (same username + class), ignoring username case
    replaced = any(
        normalize_username(entry.get("username", "")) == normalized_username
        and entry.get("class") == data.get("class")
        for entry in db
    )
    db = [
        entry for entry in db
        if not (
            normalize_username(entry.get("username", "")) == normalized_username
            and entry.get("class") == data.get("class")
        )
    ]

    db.append(data)

    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    return replaced

def load_db(guild_id):
    """Load database for a specific guild"""
    db_file = get_db_file(guild_id)
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_bindings(guild_id: int) -> dict:
    """Load username->discord_id bindings for this guild."""
    path = get_bindings_file(guild_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    return {}

def save_bindings(guild_id: int, bindings: dict) -> None:
    """Persist bindings for this guild."""
    path = get_bindings_file(guild_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bindings, f, indent=4, ensure_ascii=False)

def set_binding(guild_id: int, username: str, discord_id: int) -> None:
    bindings = load_bindings(guild_id)
    bindings[username.lower()] = int(discord_id)
    save_bindings(guild_id, bindings)

def remove_binding(guild_id: int, username: str) -> bool:
    bindings = load_bindings(guild_id)
    key = username.lower()
    existed = key in bindings
    if existed:
        bindings.pop(key, None)
        save_bindings(guild_id, bindings)
    return existed

def get_binding(guild_id: int, username: str) -> int | None:
    bindings = load_bindings(guild_id)
    return bindings.get(username.lower())

def delete_character(guild_id, username, class_name):
    """Delete a specific character from database"""
    db = load_db(guild_id)
    original_count = len(db)
    normalized_username = normalize_username(username)
    
    db = [
        entry for entry in db
        if not (
            normalize_username(entry.get("username", "")) == normalized_username
            and entry["class"] == class_name
        )
    ]
    
    if len(db) == original_count:
        return False  # Nothing deleted
    
    db_file = get_db_file(guild_id)
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    return True  # Successfully deleted

def delete_user(guild_id, username):
    """Delete all characters for a username from database"""
    db = load_db(guild_id)
    normalized_username = normalize_username(username)
    
    matching_entries = [
        entry for entry in db
        if normalize_username(entry.get("username", "")) == normalized_username
    ]
    count = len(matching_entries)
    
    if count == 0:
        return 0  # No entries found
    
    db = [
        entry for entry in db
        if normalize_username(entry.get("username", "")) != normalized_username
    ]
    
    db_file = get_db_file(guild_id)
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    return count  # Number of entries deleted