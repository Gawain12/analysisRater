from Douban.Analysis import DataProcessing
from Douban.Database.myDb import *
from sqlalchemy import *
import numpy as np
from flask import Flask
app = Flask(__name__)
#import Analysis
import matplotlib
matplotlib.use('Agg')  # 不出现画图的框
import matplotlib.pyplot as plt
from io import BytesIO
import base64

engine, db_session = connection_to_mysql()
plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# 使用ggplot的绘图风格
#plt.style.use('ggplot')


def Tspdt(name):
    Names =db_session.execute("select Count(*) from tspdt where exists (select 1 from {} where Name=tspdt.Name)".format(name)).fetchall()
    #Names = db_session.execute('select * from tspdt').fetchall()
    print(Names[0][0])
    Rate1=100*Names[0][0]/600
    print('The Rate of Tspdt is  %f' %Rate1)
    '''for Name in Names:
        print(Name[0])'''
    return Rate1

def ARate(name):

    ANum=db_session.execute("SELECT SUM(Num) from {}".format(name)).fetchall()
    A=db_session.execute("SELECT SUM(Rate*Num) from {}".format(name)).fetchall()
    B=db_session.execute("SELECT SUM(MyRate*Num) from {}".format(name)).fetchall()
    C=db_session.execute("SELECT SUM(abs(MyRate-Rate)*Num) from {}".format(name)).fetchall()
    all=float(A[0][0]/ANum[0][0])
    my=float(B[0][0]/ANum[0][0])
    dif=float(C[0][0]/ANum[0][0])
    print('All rate avarage is: %f' % all)
    #print(C[0][0]/ANum[0][0])
    print('My Rate average is: %f' % my)
    print('The difference of Me and Standard is: %f' % dif)
    if dif>1.5:
        Rate2=all-10*(dif-1.5)
    else:
        Rate2 = all
    return 10*Rate2
    #print(Rate2)
def RVolume(name):
    Num=db_session.execute("select Count(*) from {}".format(name)).fetchall()
    print('My Reading Volume is %f' %Num[0][0])
    Rate3=100*Num[0][0]/4000
    print(Rate3)
    return Rate3
def Type(name):
    #mylist = CreateTb(name)
    A=['剧情','喜剧','动作','爱情','科幻','动画','悬疑','惊悚','恐怖','犯罪','同性','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠','情色']
    rate=0
    #Type=db_session.execute("select Count(*) from {}".format(name)).fetchall()
    data=DataProcessing.read_data(name)
    a,b=DataProcessing.type(data)
    for i in range(0,len(a)):
        if a[i] in A:
            if b[i]<200:
                rate+=b[i]/200
            else:
                rate+=1
        else:
            print('%s is not in the list' %a[i])
    print("My Type Rate is: %f"%rate)
    #print(Type[0][0])
    Rate4=rate/22*100
    print(Rate4)
    return Rate4

if __name__ == '__main__':
    #Tspdt()
    #ARate()
    #RVolume('mylist')
    #RadarChart()
    Type("mylist")
    #ARate()
    '''Total = ARate() * 0.3 + RVolume() * 0.18 + Type() * 0.22 + Tspdt() * 0.3
    Users = User(Id=None,Name=name, Rvolume=RVolume(), Type=Type(), Tspdt=Tspdt(), Wrate=ARate(), Score=Total)
    db_session.add(Users)
    db_session.commit()'''

    #app.run()