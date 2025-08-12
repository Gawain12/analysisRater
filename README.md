# Douban Movie Analysis Pipeline

This project is a command-line data pipeline for scraping, storing, and analyzing movie rating data from Douban and IMDb.

## Features

- **Modular Architecture**: Clear separation between scraping, data processing, and orchestration.
- **Command-Line Interface**: All pipeline steps are managed through a powerful CLI (`main.py`).
- **Dual Platform Scraping**: Supports fetching data from both Douban and IMDb.
- **Persistent Storage**: Scraped data is loaded into a MySQL database for analysis.
- **Data Analysis**: Includes scripts to calculate weighted scores and analyze user viewing habits.
- **Incremental Scraping**: Scrapers are designed to fetch only new data, saving time on subsequent runs.

## Project Structure

```
.
├── main.py             # Main CLI entry point to orchestrate the pipeline
├── analysis/           # Data loading, processing, and analysis scripts
│   └── data_processor.py
├── config/             # Configuration files for database, APIs, etc.
│   └── config.py
├── Database/           # SQLAlchemy models and database connection logic
│   └── myDb.py
├── scrapers/           # Scripts to scrape data from Douban and IMDb
│   ├── douban_scraper.py
│   └── imdb_scraper.py
├── web/                # (Optional) Decoupled Flask web interface
├── requirements.txt    # Python package dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server
- Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:Gawain12/Douban.git
    cd Douban
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the application:**
    - Open `config/config.py`.
    - Fill in your `DATABASE_CONFIG` with your MySQL credentials.
    - Add your Douban `cookie` to the `DOUBAN_CONFIG`.
    - For the IMDb scraper, follow the in-script instructions to generate an `auth.json` file.

### Usage

The primary entry point is `main.py`. You can control the entire pipeline from here.

**Run the full pipeline (Scrape Douban -> Load to DB -> Analyze):**
```bash
python main.py --full-pipeline --user <your_douban_id>
```

**Run individual steps:**

- **Scrape Douban:**
  ```bash
  python main.py --scrape douban --user <your_douban_id>
  ```

- **Load CSV data into the database:**
  ```bash
  python main.py --load --user <your_douban_id>
  ```

- **Perform data analysis:**
  ```bash
  python main.py --analyze --user <your_douban_id>
  ```
