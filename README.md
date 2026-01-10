# ClashWarAnalytics

ClashWarAnalytics is a modular Python ETL (Extract, Transform, Load) pipeline designed to provide advanced analytics for Clash of Clans Clan War Leagues (CWL).

Unlike standard in-game statistics, this tool performs a comprehensive analysis of both offense and defense across **multiple clans simultaneously**. It calculates the "Net Star Balance" for each member, creating a true performance index that is automatically uploaded to Google Drive with professional formatting and status notifications via Telegram.

## Core Features

* **Multi-Clan Support:** Process multiple clans in a single run by defining a list of tags in the configuration.
* **Automated Data Extraction:** Connects to the Supercell API to fetch real-time data for the current Clan War League group and rounds.
* **Net Balance Metric:** Calculates a custom performance metric defined as `Total Offensive Stars - Total Defensive Stars Conceded`.
* **Google Drive Integration:**
    * Uses the **XlsxWriter** engine to generate files 100% compatible with Google Sheets.
    * Supports real Excel Tables with sorting and filtering capabilities directly in Drive.
    * Generates heatmaps (Conditional Formatting) for visual performance tracking.
* **Telegram Notifications:**
    * Sends automated status updates (Success, Error, or Waiting for War End).
    * Provides a summary of processed clans directly to your mobile.
* **Historical Tracking:** Automatically appends new data to a persistent Excel history file, creating a new sheet for each clan/month (e.g., "MainClan Jan 2026").

## Technical Architecture

The project follows a clean, modular architecture:

* **`src/api`**: Handles HTTP requests, authentication, and error handling with the Supercell API.
* **`src/logic`**: Contains the business logic for processing raw JSON data and calculating aggregated statistics.
* **`src/report`**: Manages Excel generation using **XlsxWriter** for robust formatting.
* **`src/notifications`**: Handles Telegram API integration for real-time alerts.
* **`src/upload_drive`**: Manages the connection and file replacement on Google Drive.

## Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/Kevin0018/ClashWarAnalytics.git](https://github.com/Kevin0018/ClashWarAnalytics.git)
    cd ClashWarAnalytics
    ```

2.  Create a virtual environment:
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
2.  Obtain a Telegram Bot Token via @BotFather and your Chat ID via @userinfobot.
3.  Create a `.env` file based on `.env.example`:

    ```ini
    COC_API_TOKEN=your_jwt_token_here
    
    # Support for multiple clans (comma separated)
    CLAN_TAGS=#TAG1,#TAG2
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID=your_folder_id
    GOOGLE_CREDENTIALS_FILE=credentials.json
    
    # Telegram
    TELEGRAM_BOT_TOKEN=12345:YourToken
    TELEGRAM_CHAT_ID=123456789
    ```

## Usage

Run the main pipeline script manually:

```bash
python3 main.py