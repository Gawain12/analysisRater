import pandas as pd
import os

def compare_movie_lists(merged_csv_path):
    """
    Analyzes a merged movie data CSV to find movies unique to each platform.
    """
    if not os.path.exists(merged_csv_path):
        print(f"Error: Merged CSV file not found at {merged_csv_path}")
        return

    merged_df = pd.read_csv(merged_csv_path)
    print(f"Loaded {len(merged_df)} records from {merged_csv_path}")

    # Identify movies only in Douban (where IMDb-specific columns are null)
    # A key IMDb column is 'Your Rating_imdb'. If it's null, the movie is likely only on Douban.
    douban_only = merged_df[merged_df['Your Rating_imdb'].isnull()]

    # Identify movies only in IMDb (where Douban-specific columns are null)
    # A key Douban column is 'YourRating'. If it's null, the movie is likely only on IMDb.
    imdb_only = merged_df[merged_df['YourRating'].isnull()]

    print("\n--- Comparison Report ---")
    print(f"Movies found only in Douban list: {len(douban_only)}")
    print(f"Movies found only in IMDb list: {len(imdb_only)}")

    if not douban_only.empty:
        print("\nMovies to add to IMDb:")
        print(douban_only[['Title_douban', 'URL_douban']].head())
        douban_only.to_csv('douban_only.csv', index=False, encoding='utf-8-sig')
        print("Full list saved to douban_only.csv")


    if not imdb_only.empty:
        print("\nMovies to add to Douban:")
        print(imdb_only[['Title_imdb', 'URL_imdb']].head())
        imdb_only.to_csv('imdb_only.csv', index=False, encoding='utf-8-sig')
        print("Full list saved to imdb_only.csv")


if __name__ == '__main__':
    # Example usage, assuming merge_data.py has been run
    douban_user = 'gawaint'
    imdb_user = 'ur79467081'
    merged_file = f"merged_{douban_user}_{imdb_user}.csv"
    
    if os.path.exists(merged_file):
        compare_movie_lists(merged_file)
    else:
        print(f"Merged file '{merged_file}' not found. Please run merge_data.py first.")
