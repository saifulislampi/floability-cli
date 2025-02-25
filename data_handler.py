import os
import requests
import yaml
import shutil
from pathlib import Path
import hashlib

def checksum_matches(file_path: Path, expected_checksum: str) -> bool:
    """Compute MD5 checksum of a file and compare with expected checksum."""
    if not file_path.is_file():
        return False
    hasher = hashlib.md5()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest() == expected_checksum

def fetch_data_item(data_item: dict, backpack_root: Path):
    """
    Download or copy data item according to source_type.
    For 'backpack' source_type, treat `source` as relative to backpack_root.
    """
    target_path = Path(data_item["target_location"])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if data_item["source_type"] == "url":
        print(f"[data_handler] Downloading from URL: {data_item['source']} => {target_path}")
        response = requests.get(data_item["source"], stream=True)
        response.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    elif data_item["source_type"] == "filesystem":
        source_path = Path(data_item["source"].replace("*.crc.nd.eddu:", ""))  # Basic example
        print(f"[data_handler] Copying from filesystem: {source_path} => {target_path}")
        if source_path.is_file():
            shutil.copy2(source_path, target_path)
        elif source_path.is_dir():
            # Copy everything under that directory
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        else:
            print(f"[data_handler] Source not found: {data_item['source']}")

    elif data_item["source_type"] == "backpack":
        # The data is presumably within the backpack directory structure
        source_in_backpack = backpack_root / data_item["source"].lstrip("/")
        print(f"[data_handler] Copying from backpack: {source_in_backpack} => {target_path}")
        if source_in_backpack.is_file():
            shutil.copy2(source_in_backpack, target_path)
        elif source_in_backpack.is_dir():
            shutil.copytree(source_in_backpack, target_path, dirs_exist_ok=True)
        else:
            print(f"[data_handler] Source in backpack not found: {data_item['source']}")
    else:
        print(f"[data_handler] Unsupported source type: {data_item['source_type']}")
    
    if "verification" in data_item and "checksum" in data_item["verification"]:
        check_ok = checksum_matches(target_path, data_item["verification"]["checksum"])
        if not check_ok:
            print(f"[data_handler] WARNING: Checksum mismatch for {target_path}")
        else:
            print(f"[data_handler] Checksum verified for {target_path}")

def fetch_data_from_spec(data_yml_path: str, backpack_root: str = "."):
    """Fetch data from the specification file, if not already present or verified."""
    if not os.path.isfile(data_yml_path):
        print(f"[data_handler] Data spec file not found: {data_yml_path}")
        return

    with open(data_yml_path, "r") as f:
        data_spec = yaml.safe_load(f)

    if "data" not in data_spec:
        print("[data_handler] No 'data' section found in data spec.")
        return

    backpack_root_path = Path(backpack_root).resolve()

    for item in data_spec["data"]:
        target_path = Path(item["target_location"])
        item_checksum = item.get("verification", {}).get("checksum")

        # Check if file/dir is present and optionally verify checksum
        already_exists = target_path.exists()
        verified = False

        if already_exists and item_checksum:
            verified = checksum_matches(target_path, item_checksum)

        if already_exists and verified:
            print(f"[data_handler] Data item '{item['name']}' already exists and matches checksum.")
        else:
            # If missing or failed checksum, fetch it
            fetch_data_item(item, backpack_root_path)

def ensure_data_is_fetched(data_yml_path: str, backpack_root: str = "."):
    """
    Check if data from data.yml is present and correct. 
    If not, call fetch_data_from_spec to download/copy it.
    """
    fetch_data_from_spec(data_yml_path, backpack_root)