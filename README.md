# ClashWarAnalytics

ClashWarAnalytics is a modular Python ETL (Extract, Transform, Load) pipeline designed to provide advanced analytics for Clash of Clans Clan War Leagues (CWL).

While standard in-game statistics focus primarily on offensive performance, this tool leverages the official Supercell API to perform a comprehensive analysis of both offense and defense. Its primary goal is to calculate the "Net Star Balance" for each member, quantifying their true contribution to the clan's success by subtracting stars conceded in defense from stars earned in attacks.

## Core Features

* **Automated Data Extraction:** Connects to the Supercell API to fetch real-time data for the current Clan War League group and rounds.
* **Net Balance Metric:** Calculates a custom performance metric defined as `Total Offensive Stars - Total Defensive Stars Conceded`.
* **Detailed Statistical Breakdown:** Tracks specific attack outcomes (3-star, 2-star, 1-star, and 0-star rates) per player.
* **Historical Tracking:** Automatically appends new data to a persistent Excel history file, creating a new sheet for the current month (e.g., "Jan 2026") to allow for long-term trend analysis.
* **Automated Reporting:** Generates a professional Excel report (`CWL_History.xlsx`) with:
    * Auto-adjusted column widths for readability.
    * Conditional formatting (heatmaps) to visually highlight top performers and defensive liabilities.
    * Smart filtering to exclude inactive members from the report.

## Technical Architecture

The project follows a clean, modular architecture separating concerns:

* **`src/api`**: Handles HTTP requests, authentication, and error handling with the Supercell API.
* **`src/logic`**: Contains the business logic for processing raw JSON data and calculating aggregated statistics.
* **`src/models`**: Defines data structures using Python Dataclasses for type safety.
* **`src/report`**: Manages Excel generation using Pandas and OpenPyXL.

## Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/Kevin0018/ClashWarAnalytics.git](https://github.com/Kevin0018/ClashWarAnalytics.git)
    cd ClashWarAnalytics
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Obtain a generic API Token from the [Clash of Clans Developer Portal](https://developer.clashofclans.com/).
2.  Create a `.env` file in the root directory based on the provided `.env.example`.
3.  Add your credentials:

    ```ini
    COC_API_TOKEN=your_jwt_token_here
    CLAN_TAG=#YOUR_CLAN_TAG
    ```

## Usage

Run the main pipeline script:

```bash
python3 main.py