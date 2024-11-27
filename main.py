import os
from pathlib import Path
import json
from syftbox.lib import Client, SyftPermission
import diffprivlib.tools as dp
import time
import psutil
from statistics import mean
from datetime import datetime, UTC
import sqlite3
import platform
from datetime import datetime, timedelta
from typing import List, Dict
import shutil
from urllib.parse import urlparse, parse_qs
from browser_history import *
from educational_content_classifier import classify_url, get_webpage_title

API_NAME = "browser_history_member"
AGGREGATOR_DATASITE = "aggregator@openmined.org"


def split_url(url: List[str], private: bool = False):
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        # Extract domain details using tldextract
        extracted = tldextract.extract(url)

        components = {
            "scheme": parsed_url.scheme,
            "subdomain": extracted.subdomain,
            "domain": extracted.domain,
            "tld": extracted.suffix,  # Top-level domain
            "netloc": parsed_url.netloc,
            "path": parsed_url.path,
            "query": parsed_url.query,
            "fragment": parsed_url.fragment,
            "classification": classify_url(url)
        }
        if private:
            if parsed_url.query:
                components["query_params"] = parse_qs(parsed_url.query)

        if components["classification"] != "general":
            components["title"] = get_webpage_title(url)
            
        return components
    except Exception as e:
        return {"error": str(e)}


def create_restricted_public_folder(browser_history_path: Path) -> None:
    """
    Create an output folder for browser history data within the specified path.

    This function creates a directory structure for storing browser history data under `api_data/browser_history`. If the directory
    already exists, it will not be recreated. Additionally, default permissions for accessing the created folder are set using the
    `SyftPermission` mechanism to allow the data to be read by an aggregator.

    Args:
        path (Path): The base path where the output folder should be created.

    """
    os.makedirs(browser_history_path, exist_ok=True)

    # Set default permissions for the created folder
    permissions = SyftPermission.datasite_default(email=client.email)
    permissions.read.append(AGGREGATOR_DATASITE)
    permissions.save(browser_history_path)


def create_private_folder(path: Path) -> Path:
    """
    Create a private folder for browser history data within the specified path.

    This function creates a directory structure for storing browser history data under `private/browser_history`.
    If the directory already exists, it will not be recreated. Additionally, default permissions for
    accessing the created folder are set using the `SyftPermission` mechanism, allowing the data to be
    accessible only by the owner's email.

    Args:
        path (Path): The base path where the output folder should be created.

    Returns:
        Path: The path to the created `browser_history` directory.
    """
    browser_history_path: Path = path / "private" / "browser_history"
    os.makedirs(browser_history_path, exist_ok=True)

    # Set default permissions for the created folder
    permissions = SyftPermission.datasite_default(email=client.email)
    permissions.save(browser_history_path)

    return browser_history_path


def save(path: str, browser_history: List[Dict]):
    current_time = datetime.now(UTC)
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as json_file:
        json.dump(
            {"browser_history": browser_history, "timestamp": timestamp_str},
            json_file,
            indent=4,
        )


def should_run() -> bool:
    INTERVAL = 20  # 20 seconds
    timestamp_file = f"./script_timestamps/{API_NAME}_last_run"
    os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
    now = datetime.now().timestamp()
    time_diff = INTERVAL  # default to running if no file exists
    if os.path.exists(timestamp_file):
        try:
            with open(timestamp_file, "r") as f:
                last_run = int(f.read().strip())
                time_diff = now - last_run
        except (FileNotFoundError, ValueError):
            print(f"Unable to read timestamp file: {timestamp_file}")
    if time_diff >= INTERVAL:
        with open(timestamp_file, "w") as f:
            f.write(f"{int(now)}")
        return True
    return False


if __name__ == "__main__":
    if not should_run():
        print(f"Skipping {API_NAME}, not enough time has passed.")
        exit(0)

    client = Client.load()

    # Create an output file with proper read permissions
    restricted_public_folder = client.api_data("browser_history")
    create_restricted_public_folder(restricted_public_folder)

    # Create private folder
    private_folder = create_private_folder(client.datasite_path)

    combined_history = fetch_combined_history()
    processed_history_private = [split_url(urlstr["url"], private=True) for urlstr in combined_history]
    processed_history_public = [split_url(urlstr["url"]) for urlstr in combined_history]

    filtered_history_private = [urlstr for urlstr in processed_history_private if urlstr["classification"] != "general" and urlstr["scheme"].lower() in {'http', 'https'}]
    filtered_history_public = [urlstr for urlstr in processed_history_public if urlstr["classification"] != "general" and urlstr["scheme"].lower() in {'http', 'https'}]
    
    # Saving public browser history added in it.
    public_file: Path = restricted_public_folder / "browser_history.json"
    save(path=str(public_file), browser_history=filtered_history_public)

    # Saving the private browser history.
    private_file: Path = private_folder / "browser_history.json"
    save(path=str(private_file), browser_history=filtered_history_private)
