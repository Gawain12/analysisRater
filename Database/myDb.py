# encoding:utf-8
# FileName: init_db
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2019/12/14 16:18
# Description: 数据库的相关操作

# 创建对象的基类:
from sqlalchemy import create_engine, Column, String, Text, DATETIME, FLOAT, INT, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#  创建基类
Base = declarative_base()
def CreateTb(name):
    class MyDoubanList(Base):
        """
        创建表
        """
        __tablename__ = name
        __table_args__ = {"useexisting": True}
        # 表的结构:
        Id = Column(INTEGER, primary_key=True, autoincrement=True)
        Name = Column(String(100), primary_key=True)
        Rate = Column(Text)
        MyRate = Column(Text)
        Num = Column(Text)
        Director = Column(String(200))
        Type = Column(String(200))
        MyComment = Column(String(200))
    return MyDoubanList
class TSPDT(Base):
    __tablename__ = 'tspdt'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    Name = Column(String(100), primary_key=True)
class User(Base):
    __tablename__ = 'user'
    Id = Column(INTEGER, primary_key=True, autoincrement=True)
    Name = Column(String(100), primary_key=True)
    Rvolume = Column(Text)
    Type = Column(Text)
    Tspdt = Column(Text)
    Wrate =Column(Text)
    Score =Column(Text)
def connection_to_mysql():
    """
    连接数据库
    @return:
    """
    engine = create_engine('mysql+pymysql://root:password@localhost:3306/douban?charset=utf8mb4')
    Session = sessionmaker(bind=engine)
    db_session = Session()
    # 创建数据表
    Base.metadata.create_all(engine)
    return engine, db_session
if __name__ == '__main__':
    engine, db_session = connection_to_mysql()

