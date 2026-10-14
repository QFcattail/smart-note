import os
import datetime
import sys
import threading
import time
import traceback
from shutil import copy
from core import function
import cv2
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.inputui import Ui_MainWindow
import pyaudio
import wave
from app import app

class uic(QMainWindow, Ui_MainWindow):
    vedioconn = pyqtSignal(object)  # 处理动态数据
    voiceconn = pyqtSignal(object)

    def __init__(self,createnoteui):
        super(uic, self).__init__()
        function.ee_return_create.on('return_create', self.returnbtn_clicked)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setupUi(self)
        self.btn_block=0
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.sendtoemail = ""
        self.inputtype = 0 #0 为默认值  1为输入标题 2为输入关键词
        self.result = "" #识别结果
        self.currentkey =""
        self.voicebtn.clicked.connect(self.voicebtn_clicked)
        self.photobtn.clicked.connect(self.photobtn_clicked)
        self.vedioconn.connect(self.handelframe)
        self.voiceconn.connect(self.voiceconnhandel)
        self.voicerun = False
        self.vediorun = False
        self.camrun = threading.Event()
        self.camrun.set()
        
        self.createnoteui = createnoteui
        self.current_keyword="2"
    # 录音信号的处理
    def voiceconnhandel(self, o):
        self.result = "测试录音识别结果"
        #self.returnbtn_clicked()
        self.callback(True)
        

    def create(self):
        self.createui.show()
        self.hide()

    def returnbtn_clicked(self):
        self.createnoteui.show()
        self.vediorun = False
        self.hide()

    def set_title(self):
        self.inputtype = 1
        self.note_current_num=self.createnoteui.note_current_num

        self.voicebtn.setVisible(True)
        self.show()

    def set_keyword(self):
        self.inputtype = 2
        self.note_current_num=self.createnoteui.note_current_num

        self.voicebtn.setVisible(True)
        self.show()

    def update_img(self):
        self.inputtype = 3
        self.current_keyword=self.createnoteui.current_keyword
        self.note_current_num=self.createnoteui.note_current_num
        print(self.createnoteui.current_keyword)

        self.voicebtn.setVisible(False)
        self.show()
    def show(self):
        self.btn_block=0
        self.vediorun = True
        # th = threading.Thread(target=self.handelvedio)
        # th.setDaemon(True)
        # th.start()
        # 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = cv2.VideoCapture(0)
        self.timer.start(1000//30)
        
        super(uic, self).show()
    def voicebtn_clicked(self):
        if self.btn_block == 1:
            return
        if self.voicebtn.text() == "开\n始\n录\n音":
            self.voicebtn.setText("结\n束\n录\n音")
            self.voicerun = True
            th = threading.Thread(target=self.voicehandel)
            th.start()
        else:
            self.voicebtn.setText("开\n始\n录\n音")
            self.voicerun = False


    def photobtn_clicked(self):
        if self.btn_block == 1:
            print("block")
            return
        while self.cap.isOpened():
            self.camrun.wait()
            # 获取画面
            success, frame = self.cap.read()
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not success:
                self.cap = cv2.VideoCapture(0)
                continue
            else:
                break
        self.frame=frame
        #self.camrun.clear()
        self.result = "测试拍照识别结果"
        #self.returnbtn_clicked()
        self.callback()
        

    # 执行完检测的回调函数 这个函数里新建了关键词 并保存在了字典里
    def callback(self,voice=False):
        self.btn_block=1
        loading_img=cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "loading_img.png"))
        self.vedioconn.emit(loading_img)
        self.vediorun = False
        app.processEvents()   
        try:
            
            self.vediorun = False
            if self.inputtype == 1:#set title
                if voice:
                    function.change_title_speech(self.note_current_num)
                    
                else:
                    function.change_title_ocr(self.note_current_num,self.frame)
                self.createnoteui.titlebtn.setText(function.get_title(self.note_current_num))
                function.ee_return_create.emit("return_create")
            elif self.inputtype == 2: #set keyword
                if voice : # 如果是音频
                    function.create_keyword_speech(self.note_current_num)

                else:
                    function.create_keyword_ocr(self.note_current_num,self.frame)
                
            else: #修改照片
                self.img_path="data/img/"+str(time.time())+".png"
                
                cv2.imwrite(self.img_path,self.frame)
                function.change_img(self.note_current_num,self.current_keyword,self.img_path)
                # self.createnoteui.imglb.setPixmap(QPixmap(function.get_img_path(self.note_current_num,self.current_keyword)))
                self.createnoteui.lictwidget_itemchangedd()
                function.ee_return_create.emit("return_create")
            self.vediorun = False
        except Exception as e:
            traceback.print_exc()
            pass
        app.processEvents() 
        

    def handelframe(self,f):
        if f is not None:
            self.displayImage(f,self.imglb)
        else:
            self.imglb.setPixmap(QPixmap(""))

    # 显示图片
    def displayImage(self, img, qlabel):
        # BGR -> RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # default：The image is stored using 8-bit indexes into a colormap， for example：a gray image
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:  # rows[0], cols[1], channels[2]
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        qlabel.setPixmap(QPixmap.fromImage(outImage))

    # 录音线程的具体执行
    def voicehandel(self):
        # 录音参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 8000
        CHUNK = 1024
        RECORD_SECONDS = 5
        now = datetime.datetime.now()
        WAVE_OUTPUT_FILENAME = f"wave.wav"
        # 创建录音对象
        audio = pyaudio.PyAudio()

        # 打开录音流
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        print("开始录音")

        frames = []

        # 开始录音
        while True:
            if not self.voicerun:
                break
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束")

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
    # 执行具体的摄像头播放
    def handelvedio(self):
        pass
        # try:
        #     self.cap = cv2.VideoCapture(0)
        #     while self.cap.isOpened():
        #         self.camrun.wait()
        #         # 获取画面
        #         success, frame = self.cap.read()
        #         if not success:
        #             self.cap = cv2.VideoCapture(0)
        #             continue
        #         if not self.vediorun:
        #             break
        #         self.vedioconn.emit(frame)

        #     self.cap.release()
        # except Exception as e:
        #     print(e)
        # self.vedioconn.emit(None)
    def update_frame(self):
        self.camrun.wait()
                # 获取画面
        success, frame = self.cap.read()
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.vedioconn.emit(frame)
        if not self.vediorun:
            self.cap.release()
            self.timer.stop()
            self.vedioconn.emit(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())