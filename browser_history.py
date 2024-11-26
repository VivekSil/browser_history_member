import os
import sqlite3
import platform
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
import shutil


def fetch_safari_history() -> List[Dict]:
    if platform.system() != "Darwin":
        return []
    safari_db_path = os.path.expanduser("~/Library/Safari/History.db")
    if not os.path.exists(safari_db_path):
        print("Safari history database not found.")
        return []

    # Copying is necessary because databases are locked
    # Copies are intentionally outside syftbox, but we can process them locally
    temp_db_path = Path("~/.tmp/Safary_History.db").expanduser()
    shutil.copy(safari_db_path, temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            history_items.url,
            history_visits.visit_time
        FROM
            history_visits
        JOIN
            history_items
        ON
            history_items.id = history_visits.history_item
        ORDER BY
            visit_time DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    # Remove tmp copy as we are done with it
    temp_db_path.unlink(missing_ok=True)

    history = []
    for url, visit_time in rows:
        visit_time = datetime(2001, 1, 1) + timedelta(seconds=visit_time)
        history.append({"url": url, "visit_time": visit_time, "browser": "safari"})
    return history


def fetch_chrome_history() -> List[Dict]:
    db_paths = {
        "Darwin": os.path.expanduser(
            "~/Library/Application Support/Google/Chrome/Default/History"
        ),
        "Linux": os.path.expanduser("~/.config/google-chrome/Default/History"),
    }
    chrome_db_path = db_paths.get(platform.system())
    if not chrome_db_path or not os.path.exists(chrome_db_path):
        print("Chrome history database not found.")
        return []

    # Copying is necessary because databases are locked
    # Copies are intentionally outside syftbox, but we can process them locally
    temp_db_path = Path("~/.tmp/Chrome_History").expanduser()
    shutil.copy(chrome_db_path, temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            urls.url,
            urls.last_visit_time
        FROM
            urls
        ORDER BY
            last_visit_time DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    temp_db_path.unlink(missing_ok=True)

    history = []
    for url, last_visit_time in rows:
        visit_time = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
        history.append({"url": url, "visit_time": visit_time, "browser": "chrome"})
    return history


def fetch_firefox_history() -> List[Dict]:
    db_paths = {
        "Darwin": os.path.expanduser("~/Library/Application Support/Firefox/Profiles"),
        "Linux": os.path.expanduser("~/.mozilla/firefox"),
    }
    firefox_profile_path = db_paths.get(platform.system())
    if not firefox_profile_path or not os.path.exists(firefox_profile_path):
        print("Firefox profile directory not found.")
        return []

    history = []
    for profile in os.listdir(firefox_profile_path):
        profile_path = os.path.join(firefox_profile_path, profile)
        if not os.path.isdir(profile_path):
            continue
        places_db = os.path.join(profile_path, "places.sqlite")

        if not os.path.exists(places_db):
            continue

        # Copying is necessary because databases are locked
        # Copies are intentionally outside syftbox, but we can process them locally
        temp_db_path = Path("~/.tmp/Firefox_places.sqlite").expanduser()
        shutil.copy(places_db, temp_db_path)

        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                moz_places.url,
                moz_historyvisits.visit_date
            FROM
                moz_places
            JOIN
                moz_historyvisits
            ON
                moz_places.id = moz_historyvisits.place_id
            ORDER BY
                visit_date DESC
        """
        )
        rows = cursor.fetchall()
        conn.close()

        temp_db_path.unlink(missing_ok=True)

        for url, visit_date in rows:
            visit_time = datetime(1970, 1, 1) + timedelta(microseconds=visit_date)
            history.append({"url": url, "visit_time": visit_time, "browser": "firefox"})
    return history


def fetch_brave_history() -> List[Dict]:
    db_paths = {
        "Darwin": os.path.expanduser(
            "~/Library/Application Support/BraveSoftware/Brave-Browser/Default/History"
        ),
        "Linux": os.path.expanduser(
            "~/.config/BraveSoftware/Brave-Browser/Default/History"
        ),
    }

    brave_profile_path = db_paths.get(platform.system())
    if not brave_profile_path or not os.path.exists(brave_profile_path):
        print("brave profile directory not found.")
        return []

    # Copying is necessary because databases are locked
    # Copies are intentionally outside syftbox, but we can process them locally
    temp_db_path = Path("~/.tmp/brave_places.sqlite").expanduser()
    shutil.copy(brave_profile_path, temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT url,last_visit_time FROM urls ORDER BY last_visit_time DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()
    ""
    temp_db_path.unlink(missing_ok=True)
    history = []
    print(rows)
    for data in rows:
        (url, visit_time) = data
        visit_time = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
        history.append({"url": url, "visit_time": visit_time, "browser": "brave"})
    return history


def fetch_combined_history() -> List[Dict]:
    temp_folder = Path("~/.tmp").expanduser()
    os.makedirs(temp_folder, exist_ok=True)

    print("Fetching Safari history...")
    safari_history = fetch_safari_history()
    print(f"Safari history: {len(safari_history)} items")

    print("\nFetching Chrome history...")
    chrome_history = fetch_chrome_history()
    print(f"Chrome history: {len(chrome_history)} items")

    print("\nFetching Firefox history...")
    firefox_history = fetch_firefox_history()
    print(f"Firefox history: {len(firefox_history)} items")

    print("\nFetching Brave history...")
    brave_history = fetch_brave_history()
    print(f"Brave history: {len(brave_history)} items")

    print("\nSafari sample history:", safari_history[:5])
    print("Chrome sample history:", chrome_history[:5])
    print("Firefox sample history:", firefox_history[:5])
    print("Brave sample history:", brave_history[:5])
    combined_history = safari_history + chrome_history + firefox_history + brave_history
    return combined_history
