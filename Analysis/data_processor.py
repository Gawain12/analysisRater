import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from Database.myDb import connection_to_mysql, User, CreateTb, Base
import numpy as np

def read_data(name, db_session):
    """
    读取数据库中的数据
    """
    engine = db_session.get_bind()
    sql = f"select * from `{name}` where LENGTH(NumVotes)<10"
    data = pd.read_sql(sql, con=engine)
    data['MyComment'] = data['MyComment'].fillna(data['YourRating'])
    data['Genres'] = data['Genres'].str.replace(' ', '').str.replace('/',',')
    data['IMDbRating'] = data['IMDbRating'].astype(float)
    data['NumVotes'] = data['NumVotes'].astype(int)
    return data

def type_stats(df_data):
    if df_data.empty:
        return [], []
    df_data['TypeArr'] = df_data['Genres'].map(lambda e: e.split(','))
    list_of_lists = df_data['TypeArr'].values.tolist()
    if not any(list_of_lists):
        return [], []
    movie_type_list = np.concatenate(list_of_lists)
    movie_type_counter = pd.DataFrame(movie_type_list, columns=['Genres'])['Genres'].value_counts()
    movie_type_x = movie_type_counter.index.tolist()
    movie_type_y = movie_type_counter.values.tolist()
    return movie_type_x,movie_type_y

def load_csv_to_db(file_path, table_name):
    """
    Loads a CSV file into a database table.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} records from {file_path}")

    # Basic data cleaning and standardization
    df.rename(columns={'Const': 'IMDB_ID', 'Your Rating': 'YourRating', 'Date Rated': 'DateRated'}, inplace=True)
    
    engine, db_session = connection_to_mysql(table_name)
    
    # Create table if it doesn't exist
    MyTable = CreateTb(table_name)
    Base.metadata.create_all(engine)

    for _, row in df.iterrows():
        try:
            row.to_frame().T.to_sql(table_name, engine, if_exists='append', index=False)
        except IntegrityError:
            # Handle duplicates - for now, we'll just skip them
            print(f"Skipping duplicate entry: {row.get('IMDB_ID')}")
            db_session.rollback()
            continue
    
    print(f"Successfully loaded data into table '{table_name}'")

def analyze_data(user_name):
    """
    Runs the analysis for a given user.
    """
    engine, db_session = connection_to_mysql(user_name)
    nick = db_session.execute(text(f"SELECT Nick FROM `user` WHERE `Name`='{user_name}'")).scalar() or user_name
    
    print("Calculating ARate...")
    arate = ARate(user_name, db_session)
    print("Calculating RVolume...")
    rvolume = RVolume(user_name, db_session)
    print("Calculating Type...")
    type_score = Type(user_name, db_session)
    print("Calculating Tspdt...")
    tspdt_score = Tspdt(user_name, db_session)
    Total = arate * 0.3 + rvolume * 0.18 + type_score * 0.22 + tspdt_score * 0.3
    n =  db_session.execute(text('select Count(*)  FROM `user`')).fetchall()[0][0]

    Users = User(Id=n+1,Name=user_name,Nick=nick, Rvolume=RVolume(user_name, db_session), Type=Type(user_name, db_session), Tspdt=Tspdt(user_name, db_session), Wrate=ARate(user_name, db_session), Score=float(Total))
    db_session.merge(Users)
    db_session.commit()
    print("Analysis complete.")

def Tspdt(name, db_session):
    query = text(f"""
        SELECT COUNT(DISTINCT t.Name)
        FROM tspdt t
        JOIN `{name}` u ON u.Title LIKE CONCAT('%', t.Name, '%')
    """)
    count_result = db_session.execute(query).scalar_one_or_none()
    count = count_result if count_result is not None else 0
    
    print(f"Found {count} matching movies in TSPDT list.")
    Rate1 = 100 * count / 1000
    print('The Rate of Tspdt is  %f' % Rate1)
    return Rate1

def ARate(name, db_session):
    ANum=db_session.execute(text("SELECT SUM(NumVotes) from `{}`where YourRating<>'0'and LENGTH(NumVotes)<10".format(name))).fetchall()
    A=db_session.execute(text("SELECT SUM(IMDbRating*NumVotes) from `{}`where YourRating<>'0'and LENGTH(NumVotes)<10".format(name))).fetchall()
    B=db_session.execute(text("SELECT SUM(YourRating*NumVotes) from `{}`where YourRating<>'0'and LENGTH(NumVotes)<10".format(name))).fetchall()
    C=db_session.execute(text("SELECT SUM(abs(YourRating-IMDbRating)*NumVotes) from `{}`where YourRating<>'0'and LENGTH(NumVotes)<10".format(name))).fetchall()
    try:
        all_rate_avg = 0
        if not all(A[0]) or not all(ANum[0]) or not all(B[0]) or not all(C[0]):
            return 0
        all_rate_avg=float(A[0][0])/float(ANum[0][0])
        my=float(B[0][0])/float(ANum[0][0])
        dif=float(C[0][0])/float(ANum[0][0])
        print('All rate avarage is: %f' % all_rate_avg)
        print('My Rate average is: %f' % my)
        print('The difference of Me and Standard is: %f' % dif)
        if dif>1.5:
            Rate2=all_rate_avg-10*(dif-1.5)
        else:
            Rate2 = all_rate_avg
        return 10*Rate2
    except Exception as e:
        print('Wrong parameter:',e)
        return 0

def RVolume(name, db_session):
    Num=db_session.execute(text("select Count(*) from `{}`".format(name))).fetchall()

    if not Num[0][0]:
        return 0
    print('My Reading Volume is %f' %Num[0][0])
    Rate3=100*Num[0][0]/4000
    print(Rate3)
    return Rate3

def Type(name, db_session):
    A=['剧情','喜剧','动作','爱情','科幻','动画','悬疑','惊悚','恐怖','犯罪','同性','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠','情色','运动','家庭']
    rate=0
    data=read_data(name, db_session)
    a,b=type_stats(data)
    for i in range(0,len(a)):
        if a[i] in A:
            if b[i]<200:
                rate+=b[i]/200
            else:
                rate+=1
        else:
            print('%s is not in the list' %a[i])
    print("My Type Rate is: %f"%rate)
    Rate4=rate/22*100
    print(Rate4)
    return Rate4

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Data processing tool.")
    parser.add_argument('--load', action='store_true', help="Load data from CSV files into the database.")
    parser.add_argument('--analyze', action='store_true', help="Run data analysis on the database.")
    parser.add_argument('--user', type=str, help="Specify the Douban username.")
    args = parser.parse_args()

    if args.user:
        douban_user = args.user
        imdb_user = 'ur79467081' # This should probably come from config
        
        douban_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f"douban_{douban_user}_ratings.csv")
        imdb_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f"imdb_{imdb_user}_ratings.csv")

        if args.load:
            print(f"Loading data for user {douban_user}...")
            load_csv_to_db(douban_csv, douban_user)
            # We can decide if we want to load imdb data here as well.
            # For now, assuming only douban is loaded via this script.
            # load_csv_to_db(imdb_csv, douban_user)
        
        if args.analyze:
            print(f"Analyzing data for user {douban_user}...")
            analyze_data(douban_user)
    else:
        print("Please specify a user with the --user argument.")
