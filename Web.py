from flask import Flask
app = Flask(__name__)

@app.route("/graph")
def graph():
    import matplotlib
    matplotlib.use('Agg')  # 不出现画图的框
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    # 这段正常画图
    plt.axis([0, 5, 0, 20])  # [xmin,xmax,ymin,ymax]对应轴的范围
    plt.title('My first plot')  # 图名
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')  # 图上的点,最后一个参数为显示的模式
    # -----------

    # 转成图片的步骤
    sio = BytesIO()
    plt.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    print(data)
    html = '''
       <html>
           <body>
               <img src="data:image/png;base64,{}" />
           </body>
        <html>
    '''
    plt.close()
    # 记得关闭，不然画出来的图是重复的
    return html.format(data)
    #format的作用是将data填入{}

if __name__ == '__main__':
    app.run()
