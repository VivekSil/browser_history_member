from difflib import SequenceMatcher
from w3lib.url import canonicalize_url
from urllib.parse import urlparse
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd

def compare_urls(url1: dict, url2: dict) -> float:
    """
    Compares two URLs based on their components and returns a similarity score.

    Args:
        url1 (dict): The first URL components as a dictionary.
        url2 (dict): The second URL components as a dictionary.

    Returns:
        float: The average similarity score between the two URLs.
    """
    key_components = ["scheme", "subdomain", "domain", "tld", "netloc", "path", "query", "fragment", "classification"]
    results = []
    for key in key_components:
        value = SequenceMatcher(None, url1[key], url2[key]).ratio()
        results.append(value)
    # TODO: now equal weight is given to all components. We can add weights to each component to give more importance to some components
    avg_result = sum(results) / len(results)
    return avg_result

def compare_browser_histories(path_browser_history1: Path, path_browser_history2: Path) -> List[List[float]]:
    """
    Compares two browser histories and returns a matrix of similarity scores.

    Args:
        path_browser_history1 (Path): The path to the first browser history JSON file.
        path_browser_history2 (Path): The path to the second browser history JSON file.

    Returns:
        List[List[float]]: A matrix of similarity scores between the URLs in the two browser histories.
    """
    print("Opening browser history files...")
    with open(path_browser_history1, 'r') as file1:
        browser_history1 = json.load(file1)["browser_history"]
    with open(path_browser_history2, 'r') as file2:
        browser_history2 = json.load(file2)["browser_history"]
    
    matrix = []
    print("Comparing browser histories...")
    for entry1 in browser_history1:
        row = []
        for entry2 in browser_history2:
            comparison = compare_urls(entry1, entry2)
            row.append(comparison)
        matrix.append(row)
    return matrix