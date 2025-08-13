import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Movie data scraping and analysis tool.")
    parser.add_argument('--scrape', choices=['douban', 'imdb', 'all'], help="Run the specified scraper(s).")
    parser.add_argument('--load', action='store_true', help="Load data from CSV files into the database.")
    parser.add_argument('--analyze', action='store_true', help="Run data analysis on the database.")
    parser.add_argument('--merge', action='store_true', help="Merge Douban and IMDb CSV files.")
    parser.add_argument('--compare', action='store_true', help="Compare the merged data.")
    parser.add_argument('--full-scrape', action='store_true', help="Perform a full scrape, ignoring previous data.")
    parser.add_argument('--full-pipeline', action='store_true', help="Run the full pipeline: scrape, load, analyze, merge, compare.")
    parser.add_argument('--user', type=str, default='gawaint', help="Specify the Douban username.")

    args = parser.parse_args()
    
    python_executable = "/Users/gawaintan/miniforge3/envs/film/bin/python"

    if args.scrape or args.full_pipeline:
        if args.scrape == 'douban' or args.scrape == 'all' or args.full_pipeline:
            print("--- Running Douban Scraper ---")
            douban_command = [python_executable, "scrapers/douban_scraper.py"]
            if args.full_scrape:
                douban_command.append("--full-scrape")
            subprocess.run(douban_command, check=True)
        if args.scrape == 'imdb' or args.scrape == 'all' or args.full_pipeline:
            print("--- Running IMDb Scraper ---")
            subprocess.run([python_executable, "scrapers/imdb_scraper.py"], check=True)

    if args.load or args.full_pipeline:
        print("--- Loading data into database ---")
        subprocess.run([python_executable, "analysis/data_processor.py", "--load", "--user", args.user], check=True)

    if args.analyze or args.full_pipeline:
        print("--- Analyzing data ---")
        subprocess.run([python_executable, "analysis/data_processor.py", "--analyze", "--user", args.user], check=True)
        
    if args.merge or args.full_pipeline:
        print("--- Merging data ---")
        subprocess.run([python_executable, "analysis/merge_data.py", "--user", args.user], check=True)

    if args.compare or args.full_pipeline:
        print("--- Comparing data ---")
        subprocess.run([python_executable, "analysis/compare_movies.py", "--user", args.user], check=True)

if __name__ == '__main__':
    main()
