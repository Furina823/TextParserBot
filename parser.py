# parser.py
import re
import json
import os
from config import CLASS_TRANS_FILE

def load_class_translations():
    """Load class name translations from JSON file"""
    if os.path.exists(CLASS_TRANS_FILE):
        with open(CLASS_TRANS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Load translations and class list
CLASS_TRANSLATIONS = load_class_translations()
CLASS_LIST = list(CLASS_TRANSLATIONS.keys())

# Alternate in-game class names mapped to their canonical class (color codes stripped)
CLASS_ALIASES = {
    "『真我之律者』": "Lightseeker",
}

def strip_color_codes(text):
    """Remove WC3 color codes (|cAARRGGBB and |r) from text"""
    return re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', text)

def normalize_class(class_name):
    """Map alternate class names to their canonical class"""
    return CLASS_ALIASES.get(strip_color_codes(class_name).strip(), class_name)

def get_class_display(class_name):
    """Get class name with Chinese translation"""
    chinese = CLASS_TRANSLATIONS.get(class_name, "")
    if chinese:
        return f"{class_name} ({chinese})"
    return class_name

def extract_info(text):
    """Extract character information from game save file"""
    def clean_match(pattern, content):
        match = re.search(pattern, content)
        if match:
            cleaned = match.group(1).replace('\\"', '').replace('"', '').strip()
            return cleaned
        return "N/A"

    username = clean_match(r'User Name:\s*([^"]+)', text)
    player_class = normalize_class(clean_match(r'Class:\s*([^"]+)', text))
    played_version = clean_match(r'Played Version:\s*([^"]+)', text)
    compatible_version = clean_match(r'Compatible Version:\s*([^"]+)', text)
    
    load_codes_raw = re.findall(r'(?:Load Code \d+: )(-load[^\"]+)', text)
    load_codes = [code.replace('\\"', '').replace('"', '').strip() for code in load_codes_raw]

    def parse_section(section_name):
        pattern = rf'----------{re.escape(section_name)}----------'
        lines = text.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            if re.search(pattern, line):
                in_section = True
                continue
            if in_section and '----------' in line:
                break
            if in_section:
                match = re.search(r'call Preload\(\s*"([^"]+)"\s*\)', line)
                if match:
                    item = match.group(1).replace('\\"', '').strip()
                    if not item.startswith('---'):
                        items.append(item)
        return items

    return {
        "username": username,
        "class": player_class,
        "played_version": played_version,
        "compatible_version": compatible_version,
        "load_codes": load_codes,
        "inventory": parse_section("Hero Inventory"),
        "bag": parse_section("Bag"),
        "storage": parse_section("Storage")
    }