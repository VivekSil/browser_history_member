import os
from pathlib import Path
import json
from syftbox.lib import Client, SyftPermission
import diffprivlib.tools as dp
import time
import psutil
from statistics import mean
import sqlite3
import platform
from datetime import datetime, timedelta
from typing import List, Dict
import shutil
from urllib.parse import urlparse, parse_qs
from browser_history import *
import tldextract

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
        }
        if private:
            if parsed_url.query:
                components["query_params"] = parse_qs(parsed_url.query)

        return components
    except Exception as e:
        return {"error": str(e)}


def save(path: str, browser_history: List[Dict], mode: str = "all"):
    current_time = datetime.utcnow()
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    if mode == "all":
        with open(path, "w") as json_file:
            json.dump(
                {"browser_history": browser_history, "timestamp": timestamp_str},
                json_file,
                indent=4,
            )
    elif mode == "scheme":
        with open(path, "w") as json_file:
            json.dump(
                {
                    "scheme_avg": len(
                        [
                            bh["scheme"]
                            for bh in browser_history
                            if bh["scheme"] == "https"
                        ]
                    )
                    / len(browser_history),
                    "timestamp": timestamp_str,
                },
                json_file,
                indent=4,
            )


if __name__ == "__main__":

    # Get browser data
    combined_history = fetch_combined_history()
    browser_history_private, browser_history_public = [
        split_url(urlstr["url"]) for urlstr in combined_history
    ], [split_url(urlstr["url"], private=True) for urlstr in combined_history]

    save("./browser_history_private.json", browser_history_private)
    save("./browser_history_public.json", browser_history_public)
    save("./scheme_stats.json", browser_history_public, mode="scheme")
