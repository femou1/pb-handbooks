# Pinewood Builders Automatic Handbook Merge
# By femou

import re
import requests
import subprocess

EXPECTED_AUTHORS = {
    "PBST": "yoshifan0312",
    "PET":  "BananaJeans92",
    "TMS":  "LordOfDisco",
    "PB":   "Coasterteam",
}

def is_error(content):
    return (
        content == b''
        or content.startswith(b'<html')
        or b'502 Bad Gateway' in content
        or b'504 Gateway' in content
    )

def parse_header(content):
    """Parse 'author | timestamp | #n' from the first line. Returns (author, timestamp) or (None, None)."""
    first_line = content.decode('utf-8', errors='replace').split('\n')[0].strip()
    match = re.match(r'^(\S+)\s*\|\s*(.+?)\s*\|\s*#\d+$', first_line)
    if match:
        return match.group(1), match.group(2).strip()
    return None, None

def check_and_update(name, path, latest_data):
    """Returns the update timestamp string if changed, None otherwise."""
    first_line = latest_data.content.decode('utf-8', errors='replace').split('\n')[0].strip()

    if is_error(latest_data.content):
        print(f"{name}: Error response received, skipping. First line: {first_line!r}")
        return None

    author, timestamp = parse_header(latest_data.content)
    if author is None:
        print(f"{name}: Could not parse header, skipping. First line: {first_line!r}")
        return None

    expected_author = EXPECTED_AUTHORS.get(name)
    if expected_author and author != expected_author:
        print(f"{name}: Unexpected author '{author}' (expected '{expected_author}'), skipping. First line: {first_line!r}")
        return None

    with open(path, 'rb') as f:
        current = f.read()

    if latest_data.content != current:
        with open(path, 'wb') as f:
            f.write(latest_data.content)
        print(f"{name}: Change detected (updated {timestamp}), staged for commit.")
        subprocess.run(["git", "add", path])
        return timestamp
    else:
        print(f"{name}: No changes.")
        return None

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

print("Fetching handbooks from DevForum...")
latestpbst_data = requests.get('https://devforum.roblox.com/raw/3894621', headers=HEADERS)
latestpet_data  = requests.get('https://devforum.roblox.com/raw/3323409', headers=HEADERS)
latesttms_data  = requests.get('https://devforum.roblox.com/raw/3281561', headers=HEADERS)
latestpb_data   = requests.get('https://devforum.roblox.com/raw/907637',  headers=HEADERS)
print("Fetched all 4 sources.")

results = {
    "PBST": check_and_update("PBST", "pbst_handbook.md", latestpbst_data),
    "PET":  check_and_update("PET",  "pet_handbook.md",  latestpet_data),
    "TMS":  check_and_update("TMS",  "tms_handbook.md",  latesttms_data),
    "PB":   check_and_update("PB",   "pb_gamerules.md",  latestpb_data),
}

changed = [(name, ts) for name, ts in results.items() if ts is not None]

if changed:
    names_str = ", ".join(name for name, _ in changed)
    timestamps_str = "; ".join(f"{name}: {ts}" for name, ts in changed)
    git_message = f"Handbook update for {names_str}\n\nSource timestamps: {timestamps_str}"
    print(f"Pushing {len(changed)} file(s): {names_str}")
    subprocess.run(["git", "commit", "-m", git_message])
    subprocess.run(["git", "push"])
    print("Push complete.")
else:
    print("No handbooks changed, skipping push.")
