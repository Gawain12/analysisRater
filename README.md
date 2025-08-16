# CineSync: Douban & IMDb Rating Synchronization Tool

CineSync is a powerful, command-line tool designed to synchronize your movie ratings between Douban and IMDb. If you keep ratings on both platforms, this tool automates the process of keeping them consistent.

## Features

- **Two-Way Sync**: Synchronize ratings from Douban to IMDb or from IMDb to Douban.
- **Incremental Updates**: The scrapers are designed to only fetch your newest ratings, making subsequent runs fast and efficient.
- **Safe by Default**: The `sync` command performs a "dry run" by default, showing you which movies it will update without making any changes.
- **Direct API Interaction**: The tool uses the official platform APIs to update ratings, ensuring reliability.

## Project Structure

```
.
├── main.py             # The main CLI entry point for all operations.
├── data/               # Stores all generated CSVs and auth files.
├── scrapers/           # Contains the scripts for fetching ratings.
├── utils/              # Contains helper modules for merging and syncing.
├── config/             # All your personal configuration lives here.
└── requirements.txt    # Python package dependencies.
```

## Getting Started

### 1. Prerequisites

- Python 3.10+
- Git

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd CineSync
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

This is the most important step. The tool needs your browser cookies to authenticate with Douban and IMDb.

1.  Open `config/config.py`.
2.  Follow the detailed instructions in the file to get your `Cookie` string from your browser for both Douban and IMDb.
3.  Paste the cookies into the `DOUBAN_CONFIG` and `IMDB_CONFIG` sections.
4.  Make sure your Douban and IMDb usernames are correctly set in the config file.

## Usage

All commands are run through `main.py`.

### Step 1: Scrape Your Latest Ratings

Before you can sync, you need to fetch your ratings from both platforms. The scraper will save them as CSV files in the `data/` directory.

```bash
# Scrape ratings from both Douban and IMDb
python main.py scrape all
```

### Step 2: Compare and Synchronize Your Ratings

Once you have your ratings scraped, you can use the `compare` and `sync` commands.

**Important:** The order of the platforms matters. The first platform is always the **source** (where the ratings are coming FROM), and the second is the **target** (where the ratings are going TO).

**Compare (Dry Run):**

This command is for safely previewing changes. It shows you which movies are rated on the source but not the target. No changes will be made.

```bash
# Show movies rated on Douban but missing from IMDb
python main.py compare douban imdb

# Show movies rated on IMDb but missing from Douban
python main.py compare imdb douban
```

**Sync (Live Run):**

This command will add the missing ratings to the target platform. You must use the `--live` flag to execute the changes.

```bash
# Sync ratings FROM Douban TO IMDb
python main.py sync douban imdb --live

# Sync ratings FROM IMDb TO Douban
python main.py sync imdb douban --live
```

You can also use the `--limit` flag to test the sync on a small number of the oldest movies:

```bash
# Test by syncing the 2 oldest un-synced movies from Douban to IMDb
python main.py sync douban imdb --live --limit 2
```