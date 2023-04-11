import psutil
import sqlite3
import datetime
from PyQt5.Qt import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import time
import threading
import  sys




class Flow_monitoring(QMainWindow):
    printsignal = pyqtSignal(str)

    def getConnectInfo(self):
        self.initData()
        self.printsignal.connect(self.printLog)
        getNumber = 1
        while(1):
            tmpRemotip = []

            for i in psutil.net_connections():
                remotip=""
                if(len(i[4])!=0):
                    remotip=i[4][0]
                if(remotip!="" and remotip!="0.0.0.0" and remotip!="127.0.0.1" and remotip!="::" and "192.168" not in remotip and remotip!="::1"):
                    #print("ip:{0} 状态:{1}".format(remotip,i[5]))
                    if(i[5]=="ESTABLISHED" and not remotip  in tmpRemotip):
                        processname= psutil.Process(i[6]).name()
                        self.insertData(remotip,processname)
                        tmpRemotip.append(tmpRemotip)
            time.sleep(20)
            getNumber+=1
            self.printsignal.emit("当前监测次数{0}".format(getNumber))
    def StartGetConnect(self):
        if(threading.activeCount()>=2):
            self.printLog("请勿重复开启")
            return
        self.m = threading.Thread(target=self.getConnectInfo)
        self.m.start()

    def insertData(self,ip,processname):
        sql3con = sqlite3.connect(self.dbname)
        sql3cur = sql3con.cursor()
        sql3cur.execute("insert into FlowTable(ip,time,ProcessName) values ('{0}','{1}','{2}')".format(ip,int(datetime.datetime.now().timestamp()),processname))
        sql3con.commit()

    def initData(self):
        self.dbname = "流量记录.db"
        self.sql3con =sqlite3.connect(self.dbname)
        self.sql3cur = self.sql3con.cursor()
        self.sql3cur.execute("create table if not exists FlowTable(ip text,time long,ProcessName text);")
        self.sql3con.commit()
    def printLog(self,text):
        content=self.qTextEdit.toPlainText()
        if(len(content.split("\n"))>10):
            self.qTextEdit.clear()
            content="\n".join(content.split("\n")[:-2])+"\n"+text+"\n"
        else:
            content=text+"\n"
        self.qTextEdit.insertPlainText(content)

    def __init__(self):
        super(QMainWindow,self).__init__()
        self.SearchText = ""
        self.SearchList = [""]
        self.resize(900,400)
        self.move(300,300)
        self.setWindowTitle("连接统计by Yitaiqi")
        self.setCentralWidget(self.getInitView())
    def getTimeByip(self,ip):
        sql3con = sqlite3.connect(self.dbname)
        sql3cur = sql3con.cursor()
        result =sql3cur.execute("select time from FlowTable where ip='{0}'".format(ip))
        sql3con.commit()
        ret=[]
        for item in result:
            ret.append(item[0])
        return ret
    def getIPS(self,starttime,endtime):
        sql3con = sqlite3.connect(self.dbname)
        sql3cur = sql3con.cursor()
        result = sql3cur.execute("select ip,time from FlowTable where time>{0} and time<{1}".format(starttime,endtime))
        sql3con.commit()
        self.ipAData={}
        maxcount=1

        for item in result:
            if(item[0] in self.ipAData.keys()):
                lc=self.ipAData[item[0]]
                lc.append(item[1])
                #self.ipAData[item[0]]=
                if(len(self.ipAData[item[0]])>maxcount):
                    maxcount=len(self.ipAData[item[0]])
            else:
                self.ipAData[item[0]]=[item[1]]
        ips=list(range(0,maxcount+1,1))
        for key in self.ipAData.keys():
            ips[len(self.ipAData[key])]=key
        ret=[]
        for ip in ips:
            if("." in str(ip)):
                ret.append(ip)
        ret.reverse()
        return ret
    def UpdateXialaLabel(self):
        starttime=int(time.mktime(self.StartDate.dateTime().toPyDateTime().timetuple()))
        endtime=int(time.mktime(self.EndDate.dateTime().toPyDateTime().timetuple()))
        print()
        self.Xialalabel.addItems(self.getIPS(starttime,endtime))
    def DeleteAll(self):
        sql3con = sqlite3.connect(self.dbname)
        sql3cur = sql3con.cursor()
        result = sql3cur.execute("delete from FlowTable")
        sql3con.commit()
        self.printLog("清除成功")
    def drawTable(self,index):
        sql3con = sqlite3.connect(self.dbname)
        sql3cur = sql3con.cursor()
        ip=self.Xialalabel.itemText(index)
        result = sql3cur.execute("select time,ProcessName from FlowTable where ip='{0}' order by time ASC".format(ip))
        sql3con.commit()
        timelist=[]
        processName=[]
        for res in result:
            timelist.append(res[0])
            processName.append(res[1])
        processName=list(set(processName))
        x=list(range(timelist[0],timelist[-1],int(self.Timelabel.currentText().replace("分钟",""))*60))
        y=[]
        for xplottime in x:
            fl=False
            for xtime in timelist:
                if(xtime-xplottime>0 and xtime-xplottime<int(self.Timelabel.currentText().replace("分钟",""))*60):
                    y.append(1)
                    fl=True
                    break
            if(fl==False):
                y.append(0)
        newtime=[datetime.datetime.fromtimestamp(d).strftime("%Y-%m-%d %H:%M:%S") for d in x]
        fig, ax = plt.subplots(figsize=(12, 7))
        plt.title(ip+"({0})".format(",".join(processName)), fontdict={"family": "SimHei", "color": "red", "size": 20}, loc="left")
        ax.plot(newtime,y, color="red", linestyle="solid", linewidth=2)
        plt.gcf().autofmt_xdate()
        plt.show()

    def getInitView(self):
        self.initData()
        self.isEditorView = False
        self.centerWindow = QWidget()
        # 最外层垂直布局
        self.OuterLayer = QVBoxLayout()
        # 第一层水平布局
        self.OneBox = QGroupBox("")
        self.OneLayer = QHBoxLayout()
        # 第1.5层水平布局
        self.One2Box = QGroupBox("")
        self.One2Layer = QHBoxLayout()
        # 第1.6层水平布局
        self.One3Box = QGroupBox("")
        self.One3Layer = QHBoxLayout()

        # 第二层水平布局
        self.TowBox = QGroupBox("")
        self.TowLayer = QHBoxLayout()

        # 第2.5层垂直布局(左)
        self.Tow_fiveBox = QGroupBox("")
        self.Tow_five_Layer = QVBoxLayout()



        # 第三层水平布局
        self.ThreeBox = QGroupBox("")
        self.ThreeLayer = QHBoxLayout()
        self.ThreeBox.setLayout(self.ThreeLayer)

        # 第一层。

        self.DnslogInputButton1 = QPushButton("开始监测")
        self.DnslogInputButton2 = QPushButton("清除所有数据")

        self.OneLayer.addWidget(self.DnslogInputButton1)
        self.OneLayer.addWidget(self.DnslogInputButton2)
        self.OneBox.setLayout(self.OneLayer)
        self.DnslogInputButton1.clicked.connect(self.StartGetConnect)

        self.DnslogInputButton2.clicked.connect(self.DeleteAll)


        #第一点五层

        self.labStartDate=QLabel("起始时间:")
        self.StartDate=QDateTimeEdit()
        self.EndDate=QDateTimeEdit()
        self.labEndDate=QLabel("结束时间:")
        self.One2Layer.addWidget(self.labStartDate)
        self.One2Layer.addWidget(self.StartDate)
        self.StartDate.setDisplayFormat("yyyy:MM:dd HH:mm:ss")
        self.One2Layer.addWidget(self.labEndDate)
        self.One2Layer.addWidget(self.EndDate)
        self.EndDate.setDisplayFormat("yyyy:MM:dd HH:mm:ss")
        self.Timelabel = QComboBox(self)
        self.Timelab = QLabel("时间尺度:")
        self.Timelabel.addItems(["60分钟","30分钟","10分钟","5分钟","1分钟"])
        self.One2Layer.addWidget(self.Timelab)
        self.One2Layer.addWidget(self.Timelabel)
        self.One2Box.setLayout(self.One2Layer)
        self.StartDate.setDate(datetime.datetime.now())
        self.EndDate.setDate(datetime.datetime.now()+ datetime.timedelta(days=1))

        #1.6层


        self.Xialalabel = QComboBox(self)
        self.DnslogInputButton3 = QPushButton("更新")
        self.One3Layer.addWidget(self.Xialalabel)
        self.One3Layer.addWidget(self.DnslogInputButton3)
        self.One3Box.setLayout(self.One3Layer)
        self.DnslogInputButton3.clicked.connect(self.UpdateXialaLabel)
        self.Xialalabel.activated.connect(self.drawTable)
        self.Xialalabel.setFixedSize(200,25)
        # 第二层

        #self.qListview.clicked[QModelIndex].connect(self.doClickListView)

        #self.PocSearchInput.textChanged.connect(self.doSearch)

        self.qTextEdit = QTextEdit(self)
        self.TowLayer.addWidget(self.qTextEdit)
        self.TowBox.setLayout(self.TowLayer)

        self.OuterLayer.addWidget(self.OneBox)
        self.OuterLayer.addWidget(self.One2Box)
        self.OuterLayer.addWidget(self.One3Box)
        self.OuterLayer.addWidget(self.TowBox)
        self.centerWindow.setLayout(self.OuterLayer)
        return self.centerWindow

if __name__=="__main__":
    app=QApplication(sys.argv)
    print(threading.activeCount())
    maingui=Flow_monitoring()
    maingui.show()
    sys.exit(app.exec_())