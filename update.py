import json
import urllib.request
from datetime import date
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

VERSIONS_TXT_URL = (
    "https://raw.githubusercontent.com/"
    "16BitWonder/nx-versions/master/versions.txt"
)

VERSIONS_JSON_URL = (
    "https://raw.githubusercontent.com/"
    "blawar/titledb/refs/heads/master/versions.json"
)

OUTPUT_FILE = "versions.json"

# Set to True if you want to keep the existing local
# versions.json and merge the new data into it.
USE_LOCAL_JSON = True

# ============================================================
# Download helper
# ============================================================

def download_text(url):
    print(f"Downloading:")
    print(f"  {url}")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


# ============================================================
# Load existing versions.json
# ============================================================

if USE_LOCAL_JSON and Path(OUTPUT_FILE).exists():

    print()
    print(f"Loading existing {OUTPUT_FILE}...")

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            versions = json.load(f)

    except Exception as e:
        print(f"ERROR: Could not read {OUTPUT_FILE}")
        print(e)
        raise SystemExit(1)

else:

    print()
    print("No local versions.json found.")
    print("Downloading the current titledb versions.json...")

    try:
        json_data = download_text(VERSIONS_JSON_URL)
        versions = json.loads(json_data)

    except Exception as e:
        print("ERROR: Could not download or parse versions.json")
        print(e)
        raise SystemExit(1)


# ============================================================
# Download versions.txt
# ============================================================

print()

try:
    txt_data = download_text(VERSIONS_TXT_URL)

except Exception as e:
    print("ERROR: Could not download versions.txt")
    print(e)
    raise SystemExit(1)


# ============================================================
# Parse versions.txt
# ============================================================

print()
print("Processing versions.txt...")

today = str(date.today())

added_titles = 0
updated_titles = 0
unchanged_titles = 0
invalid_lines = 0

for line_number, line in enumerate(txt_data.splitlines(), start=1):

    line = line.strip()

    # Ignore blank lines
    if not line:
        continue

    # Ignore header
    if line.lower() == "id|version":
        continue

    # Make sure the line contains the separator
    if "|" not in line:
        invalid_lines += 1
        print(
            f"WARNING: Invalid line {line_number}: {line}"
        )
        continue

    title_id, version = line.split("|", 1)

    title_id = title_id.strip().lower()
    version = version.strip()

    # --------------------------------------------------------
    # Validate title ID
    # --------------------------------------------------------

    if len(title_id) != 16:

        invalid_lines += 1

        print(
            f"WARNING: Invalid title ID on line "
            f"{line_number}: {title_id}"
        )

        continue

    try:
        title_id_number = int(title_id, 16)

    except ValueError:

        invalid_lines += 1

        print(
            f"WARNING: Invalid hexadecimal title ID "
            f"on line {line_number}: {title_id}"
        )

        continue

    # --------------------------------------------------------
    # Convert nx-versions ID to titledb ID
    #
    # Example:
    #
    # 0100000000010800
    #
    # becomes:
    #
    # 0100000000010000
    #
    # The IDs differ by 0x800.
    # --------------------------------------------------------

    normalized_id = f"{title_id_number - 0x800:016x}"

    # --------------------------------------------------------
    # Validate version
    # --------------------------------------------------------

    try:
        version_number = int(version)

    except ValueError:

        invalid_lines += 1

        print(
            f"WARNING: Invalid version on line "
            f"{line_number}: {version}"
        )

        continue

    version = str(version_number)

    # --------------------------------------------------------
    # Title doesn't exist in current versions.json
    # --------------------------------------------------------

    if normalized_id not in versions:

        versions[normalized_id] = {
            version: today
        }

        added_titles += 1

        continue

    # --------------------------------------------------------
    # Title already exists
    # --------------------------------------------------------

    existing_versions = versions[normalized_id]

    # Make sure the existing entry is a dictionary
    if not isinstance(existing_versions, dict):

        print(
            f"WARNING: Unexpected format for title "
            f"{normalized_id}"
        )

        continue

    # Find highest existing version
    try:
        highest_existing = max(
            int(v) for v in existing_versions.keys()
        )

    except ValueError:

        highest_existing = 0

    # --------------------------------------------------------
    # New version is newer
    # --------------------------------------------------------

    if version_number > highest_existing:

        existing_versions[version] = today

        updated_titles += 1

    else:

        unchanged_titles += 1


# ============================================================
# Save merged versions.json
# ============================================================

print()
print("Saving merged versions.json...")

try:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            versions,
            f,
            indent=4,
            sort_keys=True
        )

        f.write("\n")

except Exception as e:

    print("ERROR: Could not save versions.json")
    print(e)

    raise SystemExit(1)


# ============================================================
# Results
# ============================================================

print()
print("=" * 60)
print("Update complete")
print("=" * 60)

print(f"Titles in database : {len(versions):,}")
print(f"New titles         : {added_titles:,}")
print(f"Updated titles     : {updated_titles:,}")
print(f"Unchanged titles   : {unchanged_titles:,}")
print(f"Invalid lines      : {invalid_lines:,}")
print(f"Date               : {today}")
print(f"Output             : {Path(OUTPUT_FILE).resolve()}")

print("=" * 60)