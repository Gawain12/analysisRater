import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.myDb import connection_to_mysql
from config import IMDB_CONFIG, DOUBAN_CONFIG

def read_imdb_csv(file_path):
    """
    Reads the IMDB CSV file into a pandas DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"IMDB ratings file not found at: {file_path}")
    
    try:
        # IMDB ratings files are typically encoded with 'latin-1' or 'cp1252'
        df = pd.read_csv(file_path, encoding='latin-1')
        return df
    except Exception as e:
        print(f"Error reading IMDB csv: {e}")
        return None

def get_douban_data(db_session, table_name):
    """
    Retrieves the user's Douban movie data from the database.
    """
    try:
        query = f"SELECT * FROM `{table_name}`"
        df = pd.read_sql(query, db_session.bind)
        return df
    except Exception as e:
        print(f"Error reading Douban data from database: {e}")
        return None

def compare_data(douban_df, imdb_df):
    """
    Compares the Douban and IMDB data and returns the result as a dictionary of DataFrames.
    """
    if douban_df is None or imdb_df is None:
        print("Could not perform comparison due to missing data.")
        return None

    # --- Data Cleaning and Preparation ---
    douban_relevant = douban_df[['Name', 'MyRate', 'IMDB']].copy()
    douban_relevant.rename(columns={'Name': 'DoubanTitle', 'MyRate': 'DoubanRating'}, inplace=True)
    
    if 'Const' not in imdb_df.columns or 'Your Rating' not in imdb_df.columns:
        print("IMDB CSV is missing required columns: 'Const' and 'Your Rating'")
        return None
        
    imdb_relevant = imdb_df[['Const', 'Title', 'Your Rating']].copy()
    imdb_relevant.rename(columns={'Const': 'IMDB', 'Title': 'IMDBTitle', 'Your Rating': 'IMDBRating'}, inplace=True)

    douban_relevant.dropna(subset=['IMDB'], inplace=True)
    
    if douban_relevant.empty:
        print("No movies with IMDB IDs found in your Douban data to compare.")
        return None

    # --- Merging and Analysis ---
    merged_df = pd.merge(douban_relevant, imdb_relevant, on='IMDB', how='outer')
    both_rated = merged_df.dropna(subset=['DoubanRating', 'IMDBRating'])
    douban_only = merged_df[merged_df['IMDBRating'].isnull() & merged_df['DoubanTitle'].notnull()]
    imdb_only = merged_df[merged_df['DoubanRating'].isnull() & merged_df['IMDBTitle'].notnull()]

    return {
        "summary": {
            "movies_in_both": len(both_rated),
            "movies_only_in_douban": len(douban_only),
            "movies_only_in_imdb": len(imdb_only),
        },
        "matched_movies": both_rated[['DoubanTitle', 'IMDBTitle', 'DoubanRating', 'IMDBRating', 'IMDB']],
        "douban_only_movies": douban_only[['DoubanTitle', 'DoubanRating', 'IMDB']],
        "imdb_only_movies": imdb_only[['IMDBTitle', 'IMDBRating', 'IMDB']],
    }


def access_imdb_unrated(douban_only_df, cookies):
    """
    Placeholder for accessing and rating movies on IMDB that are only in the Douban list.
    """
    print("\\n--- Accessing IMDB for unrated movies (d2i) ---")
    if not cookies.get('imdb'):
        print("IMDB cookie not configured in config.py. Skipping.")
        return
    print("This function is not yet implemented.")


def access_douban_unrated(imdb_only_df, cookies):
    """
    Placeholder for accessing and rating movies on Douban that are only in the IMDB list.
    """
    print("\\n--- Accessing Douban for unrated movies (i2d) ---")
    if not cookies.get('douban'):
        print("Douban cookie not configured in config.py. Skipping.")
        return
    print("This function is not yet implemented.")


def main(douban_user, imdb_csv_path, comparison_mode=None):
    """
    Main function to run the comparison.

    :param douban_user: The Douban username.
    :param imdb_csv_path: Path to the IMDB ratings CSV file.
    :param comparison_mode: 'd2i' (Douban to IMDB) or 'i2d' (IMDB to Douban).
    """
    engine, db_session = connection_to_mysql(douban_user)
    
    douban_df = get_douban_data(db_session, douban_user)
    imdb_df = read_imdb_csv(imdb_csv_path)

    if douban_df is None or imdb_df is None:
        print("Exiting due to data loading errors.")
        return

    result = compare_data(douban_df, imdb_df)
    if result is None:
        return

    summary_df = pd.DataFrame.from_dict(result['summary'], orient='index', columns=['Count'])
    print("--- Comparison Summary ---")
    print(summary_df)
    print("\\n--- Movies Rated on Both Platforms ---")
    print(result['matched_movies'].to_string(index=False))

    cookies = {'imdb': IMDB_CONFIG.get('cookie'), 'douban': DOUBAN_CONFIG.get('cookie')}

    if comparison_mode == 'd2i':
        print("\\n--- Movies Only in Your Douban Ratings (d2i) ---")
        print(result['douban_only_movies'].to_string(index=False))
        access_imdb_unrated(result['douban_only_movies'], cookies)

    elif comparison_mode == 'i2d':
        print("\\n--- Movies Only in Your IMDB Ratings (i2d) ---")
        print(result['imdb_only_movies'].to_string(index=False))
        access_douban_unrated(result['imdb_only_movies'], cookies)
    
    else:
        print("\\n--- Movies Only in Your Douban Ratings ---")
        print(result['douban_only_movies'].to_string(index=False))
        print("\\n--- Movies Only in Your IMDB Ratings ---")
        print(result['imdb_only_movies'].to_string(index=False))


if __name__ == '__main__':
    # --- Example Usage ---
    # 1. Provide the path to your IMDB ratings CSV file.
    imdb_ratings_csv = 'ratings.csv' # <-- IMPORTANT: CHANGE THIS PATH

    # 2. Choose a comparison mode: None, 'd2i', or 'i2d'.
    mode = None 

    if not os.path.exists(imdb_ratings_csv):
        print(f"IMDB ratings file not found at '{imdb_ratings_csv}'. Please update the path.")
    else:
        main('gawaint', imdb_ratings_csv, comparison_mode=mode)
