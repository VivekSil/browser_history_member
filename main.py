import hashlib
import os
from pathlib import Path
import json
from syftbox.lib import Client, SyftPermission
from datetime import datetime, timezone
from typing import List, Dict
from urllib.parse import urlparse, parse_qs
import tldextract

from src.browser_history import fetch_combined_history
from src.educational_content_classifier import classify_url
from src.utils.config_reader import ConfigReader

config_reader = ConfigReader()

API_NAME = config_reader.get_api_name()
AGGREGATOR_DATASITE = config_reader.get_aggregator_datasite()
INTERVAL = config_reader.get_interval()
ALLOW_TOP = config_reader.get_allow_top()


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
            # "query": parsed_url.query, # Skip for privacy
            # "fragment": parsed_url.fragment, # Skip for privacy
            "classification": classify_url(url),
        }
        if private:
            if parsed_url.query:
                components["query_params"] = parse_qs(parsed_url.query)

        # Skip fetching the title
        # if components["classification"] != "general":
        #     components["title"] = get_webpage_title(url)

        return components
    except Exception as e:
        return {"error": str(e), "url": url}

def get_paper_stats(filtered_urls: List[Dict[str, str]]) -> List[str]:
    cs_research_domains = [
        "arxiv.org",
        "ieee.org",
        "acm.org",
        "neurips.cc",
        "icml.cc",
        "iclr.cc",
        "aaai.org",
        "ijcai.org",
        "usenix.org",
        "aclweb.org",
        "openreview.net",
        "dl.acm.org",
        "computer.org",
        "semantic.scholar.org",
        "dblp.org",
        "researchgate.net" 
    ]
    
    cs_paper_list = []
    for url in filtered_urls:
        if url["netloc"].startswith("www."):
            netloc = url["netloc"][4:]
        else:
            netloc = url["netloc"]
        
        if netloc in cs_research_domains:
            path = url["path"].lower()
            
            is_valid_paper = any([
                (netloc == "arxiv.org" and path.startswith("/pdf/")),
                (netloc == "researchgate.net" and path.startswith("/publication/")),
                (netloc not in ["researchgate.net", "arxiv.org"] and 
                 not any(skip in path for skip in [
                     "search", 
                     "profile",
                     "citations",
                     "author",
                     "browse",
                     "/",
                     "index"
                 ]))
            ])
            
            if is_valid_paper:
                cs_paper_list.append(netloc + url["path"])
    
    return cs_paper_list


def create_restricted_public_folder(browser_history_path: Path) -> None:
    """
    Create an output folder for browser history data within the specified path.

    This function creates a directory structure for storing browser history data under
    `api_data/browser_history`. If the directory
    already exists, it will not be recreated. Additionally, default permissions for
    accessing the created folder are set using the
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

    This function creates a directory structure for storing browser history data under
    `private/browser_history`.
    If the directory already exists, it will not be recreated. Additionally, default
    permissions for
    accessing the created folder are set using the `SyftPermission` mechanism, allowing
    the data to be
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
    current_time = datetime.now(timezone.utc)
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as json_file:
        json.dump(
            {"browser_history": browser_history, "timestamp": timestamp_str},
            json_file,
            indent=4,
        )

def save_papers(path: str, paper_list: List[str]):
    current_time = datetime.now(timezone.utc)
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w") as json_file:
        json.dump(
            {"papers": paper_list, "timestamp": timestamp_str},
            json_file,
            indent=4,
        )



def should_run() -> bool:
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

def hash_url(domain):
    """
    Creates a SHA-256 hash of a domain string after normalizing it.

    Args:
        domain: A string representing a domain name or URL

    Returns:
        str: A hexadecimal string representation of the SHA-256 hash,
             or None if the input is invalid
    """
    try:
        # Handle empty or None input
        if not domain:
            return None

        # Normalize the domain
        domain = domain.lower().strip()

        # If it's a full URL, extract just the domain
        if '://' in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc

        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Remove trailing dots
        domain = domain.rstrip('.')

        # Create hash
        hash_object = hashlib.sha256(domain.encode())
        return hash_object.hexdigest()

    except Exception as e:
        print(f"Error hashing domain {domain}: {str(e)}")
        return None

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
    processed_history_public = [split_url(urlstr["url"]) for urlstr in combined_history]

    # Filter out non-educational URLs
    filtered_history_public = [
        urlstr
        for urlstr in processed_history_public
        if urlstr["classification"] != "general"
        and urlstr["scheme"].lower() in {"http", "https"}
    ]

    # Get the list of research papers browsed by the user
    cs_paper_list = get_paper_stats(filtered_history_public)

    # Saving public browser history added in it.
    file_enc: Path = restricted_public_folder / "browser_history_enc.json"
    file_clear: Path = restricted_public_folder / "browser_history_clear.json"
    file_papers: Path = restricted_public_folder / "paper_stats.json"

    # Keep only information we need to save
    history_to_file = [
        urlstr["netloc"]
        for urlstr in filtered_history_public
    ]
    hash_history = [hash_url(url) for url in history_to_file]

    # Save the hashed history and the clear history if allowed
    save(path=str(file_enc), browser_history=hash_history)

    if ALLOW_TOP:
        save(path=str(file_clear), browser_history=history_to_file)
        save_papers(path=str(file_papers), paper_list=cs_paper_list)
