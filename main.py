import requests
import json
from ruamel.yaml import YAML
import os
import re


def fix_json(broken_json: str):
    """JSONs are parsed from Lua, so we need to fix some things manually."""

    # Patches for compatibility with Python
    # 1. math.huge replaced by "inf"
    broken_json = re.sub(r'\bmath\.huge\b', '"inf"', broken_json)
    # 2. standalone inf (not already in quotes) replaced by "inf"
    broken_json = re.sub(r':\s*inf\b', ': "inf"', broken_json)
    # 3. Fix boolean keys: true/false as object keys need to be strings
    broken_json = re.sub(r'(\{|,)\s*true\s*:', r'\1"true":', broken_json)
    broken_json = re.sub(r'(\{|,)\s*false\s*:', r'\1"false":', broken_json)
    
    fixed_json = json.loads(broken_json, parse_constant=lambda x: {
        'Infinity': float('inf'),
        '-Infinity': float('-inf'),
        'NaN': float('nan')
    }.get(x, float(x)))

    return fixed_json


def get_last_updated(title: str, wiki_url: str) -> str:
    """Get the last updated timestamp for a wiki page."""
    body = {
        "action": "query",
        "format": "json",
        "prop": "info",
        "titles": title,
        "formatversion": "2",
    }
    try:
        response = requests.post(wiki_url, data=body).json()
        page = response["query"]["pages"][0]

        if "touched" in page:
            return page["touched"]
        elif "missing" in page:
            print(f"    Warning: Page '{title}' does not exist")
            return ""
        else:
            return ""
    except Exception as e:
        print(f"    Warning: Could not get timestamp for '{title}': {e}")
        return ""


def load_yaml_file(filepath: str) -> dict:
    """Load YAML data from file."""
    if not os.path.exists(filepath):
        return {}
    try:
        yaml = YAML()  # Use round-trip mode to preserve formatting
        with open(filepath, 'r') as f:
            return yaml.load(f)
    except (Exception):
        return {}


def save_yaml_file(filepath: str, data: dict) -> None:
    """Save YAML data to file preserving multiline formatting."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping

    with open(filepath, 'w') as f:
        yaml.dump(data, f)


def should_update(module_title: str, last_updated: dict, wiki_url: str) -> tuple[bool, str]:
    """Check if module should be updated based on last modified timestamp."""
    current_timestamp = get_last_updated(module_title+"/data", wiki_url)
    
    if not current_timestamp:
        print(f"  → Could not get timestamp, skipping")
        return False, ""
    
    if module_title not in last_updated:
        print(f"  → New module, will download")
        return True, current_timestamp
    
    last_timestamp = last_updated[module_title]
    if current_timestamp != last_timestamp:
        print(f"  → Changed (last: {last_timestamp}, current: {current_timestamp})")
        return True, current_timestamp
    
    print(f"  → No changes since {last_timestamp}")
    return False, current_timestamp


def fetch_and_save_module(title: str, config: dict, wiki_url: str) -> tuple[bool, str, str]:
    """Fetch and save a single module's data. Returns (updated, timestamp, error)."""
    filepath = config["file"]
    last_updated = config.get("last_updated", "")
    
    print(f"\n[{title}] Checking...")
    
    last_updated_dict = {title: last_updated} if last_updated else {}
    needs_update, current_timestamp = should_update(title, last_updated_dict, wiki_url)
    
    if not needs_update:
        return False, current_timestamp, ""
    
    print(f"  → Downloading data...")
    
    body = config["request_body"]

    try:
        response = requests.post(wiki_url, data=body).json()
        data = fix_json(response["print"])
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✓ Saved to {filepath}")
        return True, current_timestamp, ""
    except Exception as e:
        error_msg = str(e)
        print(f"  ✗ Error: {error_msg}")
        return False, "", error_msg


def main():

    WIKI_URL_BASE = "https://wiki.warframe.com/api.php"
    MODULES_FILE = "./modules.yaml"
    
    print("=" * 60)
    print("Warframe Wiki Scraper - Starting update check")
    print("=" * 60)
    
    modules_data = load_yaml_file(MODULES_FILE)
    
    if not modules_data:
        print("Error: Could not load modules.yaml")
        return
    
    # Extract modules from the 'modules' key in the YAML
    modules = modules_data.get("modules", {})
    
    if not modules:
        print("Error: No modules found in modules.yaml")
        return
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    # get wiki token
    body = {
        "action": "query",
        "meta": "tokens",
        "format": "json",
    }
    response = requests.post(WIKI_URL_BASE, data=body)
    csrf_token = response.json()['query']['tokens']['csrftoken']

    for title, config in modules.items():
        config["request_body"]["token"] = csrf_token
        was_updated, new_timestamp, error = fetch_and_save_module(title, config, WIKI_URL_BASE)
        
        modules[title]["error"] = error
        
        if error:
            error_count += 1
        elif was_updated:
            modules[title]["last_updated"] = new_timestamp
            updated_count += 1
        else:
            skipped_count += 1
    
    # Save back to YAML
    modules_data["modules"] = modules
    save_yaml_file(MODULES_FILE, modules_data)
    
    print("\n" + "=" * 60)
    print(f"Update complete!")
    print(f"  Updated: {updated_count} modules")
    print(f"  Skipped: {skipped_count} modules (no changes)")
    print(f"  Errors:  {error_count} modules")
    print("=" * 60)


if __name__ == "__main__":
    main()