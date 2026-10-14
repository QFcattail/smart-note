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
from ui.courseinputui import Ui_MainWindow
import pyaudio
import wave
from app import app
from pyzbar.pyzbar import decode
from PIL import Image

def decode_qr_code(frame):
    # 将OpenCV的图像转换为PIL图像
    image = Image.fromarray(frame)
    # 使用pyzbar解码二维码
    decoded_objects = decode(image)
    if len(decoded_objects)==0:
        return ""
    for obj in decoded_objects:
        return obj.data.decode('utf-8')

class uic(QMainWindow, Ui_MainWindow):
    vedioconn = pyqtSignal(object)  # 处理动态数据
    voiceconn = pyqtSignal(object)

    def __init__(self,createcourseui):
        super(uic, self).__init__()
        self.try_again_flag=0
        function.ee_return_create_course.on('return_create_course', self.returnbtn_clicked)
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
        
        self.createcourseui = createcourseui
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
        self.createcourseui.show()
        self.vediorun = False
        self.hide()

    def set_title(self):
        self.inputtype = 1
        self.course_current_num=self.createcourseui.course_current_num

        self.voicebtn.setVisible(True)
        self.show()

    def set_question(self):
        self.inputtype = 2
        self.course_current_num=self.createcourseui.course_current_num

        self.voicebtn.setVisible(True)
        self.show()

    def set_QRcode(self):
        self.try_again_flag=0
        self.inputtype = 3
        self.course_current_num=self.createcourseui.course_current_num

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
                    function.change_course_title_speech(self.course_current_num)
                    
                else:
                    function.change_course_title_ocr(self.course_current_num,self.frame)
                self.createcourseui.titlebtn.setText(function.get_course_title(self.course_current_num))
                function.ee_return_create_course.emit("return_create_course")
            elif self.inputtype == 2: #set question
                if voice : # 如果是音频
                    function.course_question_speech(self.course_current_num)

                else:
                    function.course_question_ocr(self.course_current_num,self.frame)
                
            else: #输入url
                url=decode_qr_code(self.frame)
                print(url)
                if url=="":
                    self.try_again_flag=1
                else:
                    function.set_url(self.course_current_num,url)
                    self.createcourseui.playVideo(url)
                    function.ee_return_create_course.emit("return_create_course")
                
            self.vediorun = False
        except Exception as e:
            traceback.print_exc()
            pass
        app.processEvents() 
        if self.try_again_flag==1:
            self.set_QRcode()
        

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