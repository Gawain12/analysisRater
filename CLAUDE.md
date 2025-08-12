# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based data pipeline for scraping and analyzing movie data from Douban and IMDb. The project has been refactored into a command-line application with a clear separation of concerns:
- **Scrapers**: Scripts dedicated to fetching data and saving it to CSV files.
- **Analysis**: A consolidated module for loading data from CSVs into a database and performing analysis.
- **Orchestrator**: A main entry point (`main.py`) to run the entire pipeline using command-line arguments.

The web application in the `web/` directory is currently separate from the main data pipeline.

## Commands

The main entry point for the application is `main.py`.

- **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

- **Run the full pipeline (scrape Douban, load, analyze):**
  ```bash
  python main.py --full-pipeline --user <douban_username>
  ```

- **Run specific steps:**
  - **Scrape Douban data:**
    ```bash
    python main.py --scrape douban --user <douban_username>
    ```
  - **Scrape IMDb data (requires authentication setup):**
    ```bash
    python main.py --scrape imdb
    ```
  - **Load data from CSV to database:**
    ```bash
    python main.py --load --user <douban_username>
    ```
  - **Run analysis:**
    ```bash
    python main.py --analyze --user <douban_username>
    ```

## Project Structure

-   `main.py`: The main entry point for the CLI application.
-   `web/`: Contains a Flask web application (currently decoupled from the main pipeline).
-   `scrapers/`: Contains the web scraping scripts (`douban_scraper.py`, `imdb_scraper.py`). Their only job is to produce CSV files.
-   `analysis/`: Contains the data processing and analysis logic (`data_processor.py`). Handles loading data into the database and calculating scores.
-   `config/`: Contains configuration files.
-   `Database/`: Contains database models and connection logic.
-   `requirements.txt`: Lists the Python dependencies for the project.

## Key Libraries

-   **argparse**: Used to create the command-line interface in `main.py`.
-   **subprocess**: Used by `main.py` to orchestrate the different pipeline scripts.
-   **Flask:** The web framework used for the user interface.
-   **SQLAlchemy:** The ORM used for interacting with the MySQL database.
-   **aiohttp:** Used for making asynchronous HTTP requests in the Douban scraper.
-   **pandas:** Used for data manipulation and creating Excel files.
-   **requests:** Used for synchronous HTTP requests.
-   **beautifulsoup4 / lxml / re:** Used for parsing HTML content.
-   **redis:** Used for tracking the progress of the scraping tasks.
-   **jieba:** Used for Chinese text segmentation for word cloud generation.
