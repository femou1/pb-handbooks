# Pinewood Builders Automatic Handbook Merge
# By femou

import re
import requests
import subprocess

EXPECTED_AUTHORS = {
    "PBST": "yoshifan0312",
    "PET":  "HandbookPET",
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

def is_redirect(content):
    """Returns (True, link) if content looks like a redirected page:
    very low character count AND contains a link to another dev forum page.
    This pattern indicates the handbook URL has likely changed."""
    text = content.decode('utf-8', errors='replace')
    if len(text) < 500:
        match = re.search(r'https://devforum\.roblox\.com/\S+', text)
        if match:
            return True, match.group(0)
    return False, None

def parse_header(content):
    """Parse 'author | timestamp | #n' from the first line. Returns (author, timestamp) or (None, None)."""
    first_line = content.decode('utf-8', errors='replace').split('\n')[0].strip()
    match = re.match(r'^(\S+)\s*\|\s*(.+?)\s*\|\s*#\d+$', first_line)
    if match:
        return match.group(1), match.group(2).strip()
    return None, None

def check_and_update(name, path, latest_data):
    """Returns the update timestamp string if changed, None otherwise."""
    if latest_data is None:
        return None  # fetch() already logged why this source was skipped

    first_line = latest_data.content.decode('utf-8', errors='replace').split('\n')[0].strip()

    if is_error(latest_data.content):
        print(f"{name}: Error response received, skipping. First line: {first_line!r}")
        return None

    redirected, link = is_redirect(latest_data.content)
    if redirected:
        print(f"{name}: ERROR - Handbook URL has likely changed! Content is very short and contains a link to: {link} — update the handbook ID in this script.")
        return None

    author, timestamp = parse_header(latest_data.content)
    if author is None:
        print(f"{name}: Could not parse header, skipping. First line: {first_line!r}")
        return None

    # The author is text inside the fetched post, not an authenticated identity, so this is NOT
    # provenance verification. Its purpose is to catch pages the wiki serves with a 200 OK whose
    # first line isn't the real "author | timestamp | #n" header (error/placeholder pages).
    expected_author = EXPECTED_AUTHORS.get(name)
    if expected_author and author != expected_author:
        print(f"{name}: Unexpected author '{author}' (expected '{expected_author}'), skipping. First line: {first_line!r}")
        return None

    with open(path, 'rb') as f:
        current = f.read()

    if latest_data.content != current:
        # Refuse to overwrite a healthy handbook with a suspiciously tiny response (truncated
        # fetch, moderated stub, etc.). This is the guard that prevents a repeat of the incident
        # where pet_handbook.md was clobbered down to 2 lines.
        if len(latest_data.content) < len(current) * 0.25:
            print(f"{name}: SUSPICIOUS - new content {len(latest_data.content)}B vs current "
                  f"{len(current)}B (<25%), refusing to overwrite. First line: {first_line!r}")
            return None
        with open(path, 'wb') as f:
            f.write(latest_data.content)
        print(f"{name}: Change detected (updated {timestamp}), staged for commit.")
        subprocess.run(["git", "add", path], check=True)
        return timestamp
    else:
        print(f"{name}: No changes.")
        return None

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
REQUEST_TIMEOUT = 180  # seconds; hard cap on each grab so a stalled socket can't hang the job

def fetch(name, url):
    """GET the raw handbook. Returns the response on a clean 200 OK, else None (reason logged).
    A failure here skips only this source rather than crashing the whole run."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        print(f"{name}: Request failed ({e}), skipping.")
        return None
    if resp.status_code != 200:
        print(f"{name}: HTTP {resp.status_code} (expected 200), skipping.")
        return None
    return resp

print("Fetching handbooks from DevForum...")
latestpbst_data = fetch("PBST", 'https://devforum.roblox.com/raw/3894621')
latestpet_data  = fetch("PET",  'https://devforum.roblox.com/raw/4691725')
latesttms_data  = fetch("TMS",  'https://devforum.roblox.com/raw/3281561')
latestpb_data   = fetch("PB",   'https://devforum.roblox.com/raw/907637')
print("Finished fetching sources.")

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
    subprocess.run(["git", "commit", "-m", git_message], check=True)
    subprocess.run(["git", "push"], check=True)
    print("Push complete.")
else:
    print("No handbooks changed, skipping push.")
