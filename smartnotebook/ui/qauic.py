import os
import datetime
import sys
import threading
import time
from core import function
import cv2
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.qaui import Ui_MainWindow
from ui.qahistoryuic import uic as qahistoryuic
from ui.qaresultuic import uic as qaresultuic
import pyaudio
import wave

from app import app

class uic(QMainWindow, Ui_MainWindow):
    vedioconn = pyqtSignal(object)  # 处理动态数据
    voiceconn = pyqtSignal(object)
    def __init__(self,mainui):
        super(uic, self).__init__()
        self.setupUi(self)
        self.mainui = mainui
        #self.htmlresult
        self.result ,self.answer_json ="",""
        #= function.get_question_speech() #回答的结果
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.historybtn.clicked.connect(self.historybtn_clicked)
        self.voicebtn.clicked.connect(self.voicebtn_clicked)
        self.photobtn.clicked.connect(self.photobtn_clicked)
        self.qahistoryui = qahistoryuic(self)
        self.qaresultui = qaresultuic(self)
        self.vedioconn.connect(self.handelframe)
        self.camrun = threading.Event()
        self.camrun.set()
        self.voicerun = False
        self.vediorun = False
        self.voiceconn.connect(self.voiceconnhandel)
        

    # 录音信号的处理
    def voiceconnhandel(self,o):
        self.vediorun = False
        loading_img=cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "loading_img.png"))
        self.vedioconn.emit(loading_img)
        app.processEvents()  
        self.qaresultui.answer=""
        self.qaresultui.open()
        now = datetime.datetime.now()
        self.hide()
        self.question= function.get_question_speech()
        # self.qaresultui.question = self.question 
        
    def show(self):
        self.vediorun =True
        # th = threading.Thread(target=self.handelvedio)
        # th.setDaemon(True)
        # th.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = cv2.VideoCapture(0)
        self.timer.start(1000//30)
        self.vedioconn.emit(None)

        super(uic, self).show()
    def returnbtn_clicked(self):
        self.vediorun= False
        self.mainui.show()
        self.hide()

    # 点击录音按钮
    def voicebtn_clicked(self):
        if self.voicebtn.text() == "开\n始\n录\n音":
            self.voicebtn.setText("结\n束\n录\n音")
            self.voicerun = True
            th = threading.Thread(target=self.voicehandel)
            th.start()
        else:
            self.voicerun = False
            self.voicebtn.setText("开\n始\n录\n音")

    # 录音线程的具体执行
    def voicehandel(self):
        # 录音参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 8000
        CHUNK = 1024
        
        now = datetime.datetime.now()
        WAVE_OUTPUT_FILENAME = f"wave.wav"
        # 创建录音对象
        audio = pyaudio.PyAudio()

        # 打开录音流
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        #print("开始录音")

        frames = []

        # 开始录音
        while True:
            if not self.voicerun:
                break
            data = stream.read(CHUNK)
            frames.append(data)

        #print("录音结束")

        # 关闭录音流
        stream.stop_stream()
        stream.close()

        # 关闭录音对象
        audio.terminate()

        # 将录音数据保存到文件
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        self.voiceconn.emit("")

    def photobtn_clicked(self):
        self.vediorun = False
       
        while self.cap.isOpened():
            self.camrun.wait()
            # 获取画面
            success, frame = self.cap.read()
            if not success:
                #self.cap = cv2.VideoCapture(0)
                continue
            else:
                break
        
        loading_img=cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "loading_img.png"))        
        self.vedioconn.emit(loading_img)
        app.processEvents()  
        self.qaresultui.answer=""
        self.qaresultui.is_history=0
        self.qaresultui.open()                      
        self.hide()
        self.question= function.get_question_ocr(frame)
        # self.qaresultui.question = self.question 
        

    def historybtn_clicked(self):
        
        self.qahistoryui.updatelist()
        self.qahistoryui.show()
        self.hide()

    def handelframe(self,f):
        if f is not None:
            self.displayImage(f,self.imglb)
        else:
            self.imglb.setPixmap(QPixmap(""))

    # 显示图片
    def displayImage(self, img, qlabel):
        # BGR -> RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:  # rows[0], cols[1], channels[2]
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        qlabel.setPixmap(QPixmap.fromImage(outImage))

    # 执行具体的摄像头播放
    def handelvedio(self):
        pass
        
    def update_frame(self):
        self.camrun.wait()
                # 获取画面
        success, frame = self.cap.read()

        if frame is not None:
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.vedioconn.emit(frame)
        if not self.vediorun:
            self.cap.release()
            self.timer.stop()
            self.vedioconn.emit(None)
            
        
        #更新摄像头
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())