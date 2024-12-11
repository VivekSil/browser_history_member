---
name: browser_history_member
author: "Irina, Vivek, Giulia, Gustavo"
version: 1.0.0
source: https://github.com/VivekSil/browser_history_member
home: https://syftbox.openmined.org/datasites/irina@openmined.org/browser_history_agg
icon: https://raw.githubusercontent.com/OpenMined/ftop/refs/heads/main/icon.png
---

# Browser History Analysis and Classification

![Python](https://img.shields.io/badge/python-3.8%2B-blue)

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
  - open a new terminal window
  - install the app by running the bash commands as follows:
  ```bash
  syftbox app install VivekSil/browser_history_member
  ```

### Prerequisites

- Python 3.8+ (Python 3.12 highly suggested)
- [SyftBox](https://syftbox.openmined.org) installed and configured


## How to Locally Test the Code

To run tests locally, follow these steps:

1. **Create and activate a virtual environment**:
   - Create a virtual environment:
     ```sh
     python3 -m venv .venv
     ```
   - Activate the virtual environment:
     - On macOS and Linux:
       ```sh
       source .venv/bin/activate
       ```
     - On Windows:
       ```sh
       .venv\Scripts\activate
       ```

2. **Install the required dependencies**:
   - Use the [requirements.txt](http://_vscodecontentref_/1) file to install the dependencies:
     ```sh
     pip install -r requirements.txt
     ```

3. **Run the tests**:
   - Use `pytest` to run all tests in the `test/` directory:
     ```sh
     python -m pytest test/
     ```


## Workflow in SyftBox

1. The [`browser_history_member`](https://github.com/VivekSil/browser_history_member) app writes intermediary outputs to a folder where only the client and the aggregator has access.
2. The aggregator app, [`browser_history_aggregator`](https://github.com/IrinaMBejan/browser_history_aggregator), computes the final results and pushes them to a file where they can be used by the static website. Only one person needs to run this app.
3. A static website reads the final results file and renders the view at this [link](https://syftbox.openmined.org/datasites/irina@openmined.org/browser_history_agg/).
