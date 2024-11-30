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
import pandas as pd

from src.browser_history import fetch_combined_history
import tldextract
from src.utils.config_reader import ConfigReader
from src.educational_content_classifier import classify_url, get_webpage_title
from src.similarity import compare_browser_histories

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
            "classification": classify_url(url),
        }
        if private:
            if parsed_url.query:
                components["query_params"] = parse_qs(parsed_url.query)

        if components["classification"] != "general":
            components["title"] = get_webpage_title(url)

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
                    / max(1, len(browser_history)),
                    "timestamp": timestamp_str,
                },
                json_file,
                indent=4,
            )


def add_title(urlstr):
    urlstr["title"] = get_webpage_title(urlstr["path"])

    return urlstr


if __name__ == "__main__":
    config_reader = ConfigReader()
    temp_data_folder = config_reader.get_temp_data_folder()
    
    # Check if files exist
    if not (
        os.path.exists(f"{temp_data_folder}/browser_history_private.json") 
        and os.path.exists(f"{temp_data_folder}/browser_history_public.json")
    ):
        print("Fetch combined history..")
        combined_history = fetch_combined_history()

        print("Process history..")
        processed_history_private = [
            split_url(urlstr["url"], private=True) for urlstr in combined_history
        ]
        processed_history_public = [split_url(urlstr["url"]) for urlstr in combined_history]

        print("Filter history..")
        filtered_history_private = [
            urlstr
            for urlstr in processed_history_private
            if urlstr["classification"] != "general"
            and urlstr["scheme"].lower() in {"http", "https"}
        ]
        filtered_history_public = [
            urlstr
            for urlstr in processed_history_public
            if urlstr["classification"] != "general"
            and urlstr["scheme"].lower() in {"http", "https"}
        ]

        print("Save history..")
        save(f"{temp_data_folder}/browser_history_private.json", filtered_history_private)
        save(f"{temp_data_folder}/browser_history_public.json", filtered_history_public)
        save(f"{temp_data_folder}/scheme_stats.json", filtered_history_public, mode="scheme")
    else:
        print("Files already exists..")
    
    # Test Similarity
    print("Compute Similarity between your own Private and Public history..")
    history1 = Path(f"{temp_data_folder}/browser_history_private.json",)
    history2 = Path(f"{temp_data_folder}/browser_history_public.json",)
    results = compare_browser_histories(history1, history2)
    print("Results:")
    df_results = pd.DataFrame(results)
    # Save
    df_results.to_csv(f"{temp_data_folder}/similarity_private_public_results.csv", index=False)
    print(df_results.mean().mean()) # 0.8198000660078747
