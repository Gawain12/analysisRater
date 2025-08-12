# encoding:utf-8
# FileName: myDb
# Author:   gawain
# email:    tankaiyuan33@gmail.com
# Date:     2020/2/14 16:18
# Description: 数据库的相关操作

# 创建对象的基类:
from sqlalchemy import create_engine, Column, String, Text, DATETIME, FLOAT, INT, INTEGER, ForeignKey, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.config import DATABASE_CONFIG


#  创建基类

Base = declarative_base()
def CreateTb(name):
    class MyDoubanList(Base):
        """
        创建表
        """
        __tablename__ = name
        __table_args__ = {'extend_existing': True,
                          'mysql_charset': 'utf8mb4'
                          }
        # Corresponds to IMDB's 'Const'
        IMDB_ID = Column(String(100), primary_key=True)
        # Corresponds to IMDB's 'Your Rating'
        YourRating = Column(INTEGER)
        # Corresponds to IMDB's 'Date Rated'
        DateRated = Column(String(20))
        # Corresponds to IMDB's 'Title'
        Title = Column(String(200))
        # Corresponds to IMDB's 'URL'
        URL = Column(String(200))
        # Corresponds to IMDB's 'Title Type'
        TitleType = Column(String(50))
        # Corresponds to IMDB's 'IMDb Rating'
        IMDbRating = Column(FLOAT)
        # Corresponds to IMDB's 'Runtime (mins)'
        Runtime = Column(INTEGER)
        # Corresponds to IMDB's 'Year'
        Year = Column(INTEGER)
        # Corresponds to IMDB's 'Genres'
        Genres = Column(String(200))
        # Corresponds to IMDB's 'Num Votes'
        NumVotes = Column(INTEGER)
        # Corresponds to IMDB's 'Release Date'
        ReleaseDate = Column(String(20))
        # Corresponds to IMDB's 'Directors'
        Directors = Column(String(200))
        # Douban specific fields
        MyComment = Column(Text)
    return MyDoubanList
class TSPDT(Base):
    __tablename__ = 'tspdt'
    __table_args__ = {
            'mysql_charset': 'utf8mb4'
    }
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    Name = Column(String(255), unique=True)
class User(Base):
    __tablename__ = 'user'
    __table_args__ = {
                      'mysql_charset': 'utf8mb4'
                      }
    Id = Column(INTEGER,autoincrement=True)
    Name = Column(String(100), primary_key=True,)
    Nick=Column(Text)
    Rvolume = Column(Text)
    Type = Column(Text)
    Tspdt = Column(Text)
    Wrate =Column(Text)
    Score =Column(Text)
def connection_to_mysql(name, drop_existing=False):
    """
    连接数据库
    @return:
    """
    engine = create_engine(
        f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['db_name']}?charset={DATABASE_CONFIG['charset']}"
    )
    Session = sessionmaker(bind=engine)
    db_session = Session()
    # 创建数据表
    inspector = inspect(engine)
    if drop_existing and inspector.has_table(name):
        MyDoubanList = CreateTb(name)
        Base.metadata.drop_all(engine, tables=[MyDoubanList.__table__])
    Base.metadata.create_all(engine)
    return engine, db_session
if __name__ == '__main__':
    engine, db_session = connection_to_mysql()
