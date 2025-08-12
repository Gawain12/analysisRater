
import pandas as pd
from Database.myDb import connection_to_mysql, TSPDT, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

def import_csv_to_db():
    """
    Imports movie titles from a CSV file into the tspdt database table.
    """
    engine, db_session = connection_to_mysql('tspdt_importer')

    try:
        # Clear the existing table
        print("Clearing the 'tspdt' table...")
        db_session.execute(text('TRUNCATE TABLE tspdt'))
        db_session.commit()
        print("'tspdt' table cleared.")

        # Read the CSV file
        csv_path = 'tspdt1000-2025.csv'
        print(f"Reading data from {csv_path}...")
        df = pd.read_csv(csv_path)

        # Check if 'Title' column exists
        if 'Title' not in df.columns:
            print("Error: 'Title' column not found in the CSV file.")
            return

        # Insert data into the database
        print("Inserting new data into the 'tspdt' table...")
        for title in df['Title']:
            # The schema has an auto-incrementing id, so we only provide the Name
            tspdt_entry = TSPDT(Name=title)
            db_session.add(tspdt_entry)

        db_session.commit()
        print(f"Successfully imported {len(df)} movie titles into the 'tspdt' table.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == '__main__':
    import_csv_to_db()
