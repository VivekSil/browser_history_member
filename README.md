---
name: browser_history_member
author: "Irina, Vivek, Giulia, Gustavo"
version: 1.0.0
source: https://github.com/VivekSil/browser_history_member
home: https://syftbox.openmined.org/datasites/irina@openmined.org/browser_history_agg
icon: https://raw.githubusercontent.com/OpenMined/ftop/refs/heads/main/icon.png
---

# Browser History Analysis and Classification

This project provides tools for analyzing, classifying, and comparing browser history data, focusing on privacy and educational content. It integrates privacy-preserving techniques and classification methods to manage browser history data securely.

## Features

- **Browser History Fetching**: Supports Safari, Chrome, Firefox, and Brave.
- **URL Classification**: Categorizes URLs into educational, research, tutorials, and more using domain patterns and content analysis.
- **Privacy-Preserving Tools**:
  - Hashing of domain names for anonymization.
  - Separation of public and private datasets.
- **Similarity Analysis**: Computes similarity scores between URLs or browser histories.
- **Integration with SyftBox**: Enables privacy-enhancing workflows.

## Setup and Participate

1. Run SyftBox
  ```bash
  curl -LsSf https://syftbox.openmined.org/install.sh | sh
  ```

2. Install this app:
  ```bash
  syftbox app install VivekSil/browser_history_member
  ```

### Prerequisites

- Python 3.8+
- [SyftBox](https://github.com/OpenMined/syftbox) installed and configured

## How locally test the code
1. create and activate an environment with `requirements.txt` and `python` (highly suggested `3.12` version!)
2. `python -m pytest test/` to run all tests
