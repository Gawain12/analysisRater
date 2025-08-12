import pandas as pd
import os
from config.config import FILE_PATHS

def merge_movie_data(douban_user, imdb_user):
    """
    Merges movie data from Douban and IMDb CSV files into a single DataFrame.
    """
    douban_csv_path = FILE_PATHS['output_csv'].format(douban_user)
    imdb_csv_path = 'imdb_ratings_export.csv' # Assuming this is the standard name from the imdb_scraper

    if not os.path.exists(douban_csv_path):
        print(f"Error: Douban CSV file not found at {douban_csv_path}")
        return
    if not os.path.exists(imdb_csv_path):
        print(f"Error: IMDb CSV file not found at {imdb_csv_path}")
        return

    # Load the datasets
    douban_df = pd.read_csv(douban_csv_path)
    imdb_df = pd.read_csv(imdb_csv_path)

    print(f"Loaded {len(douban_df)} records from Douban.")
    print(f"Loaded {len(imdb_df)} records from IMDb.")

    # Standardize column names for merging
    # This is a placeholder - we'll need to align the columns properly
    douban_df.rename(columns={'IMDB_ID': 'Const'}, inplace=True)

    # Merge the dataframes based on IMDb ID ('Const')
    # We'll use an outer merge to keep all records from both files
    merged_df = pd.merge(douban_df, imdb_df, on='Const', how='outer', suffixes=('_douban', '_imdb'))

    # Simple deduplication: prioritize IMDb data for overlapping columns
    for col in imdb_df.columns:
        if col + '_imdb' in merged_df.columns and col + '_douban' in merged_df.columns:
            merged_df[col] = merged_df[col + '_imdb'].fillna(merged_df[col + '_douban'])
            merged_df.drop(columns=[col + '_douban', col + '_imdb'], inplace=True)

    # Save the merged data
    output_filename = f"merged_{douban_user}_{imdb_user}.csv"
    merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"Successfully merged data into {output_filename}")

if __name__ == '__main__':
    # Example usage:
    douban_user_id = 'gawaint'
    imdb_user_id = 'ur79467081' # This should match the one in your config
    merge_movie_data(douban_user_id, imdb_user_id)
