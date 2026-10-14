import datetime
import json
import os
import sys
import threading
import time

import pywifi
import qdarkstyle
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from qdarkstyle import LightPalette
from ui.courseuic import uic as courseuic  # Add this line
from app import app
from core import function
from ui.mainui import Ui_MainWindow
from ui.noteuic import uic as noteuic
from ui.qauic import uic as qauic
from services import wifiUtils
from ui.settinginputuic import uic as settinginputuic
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据
    def __init__(self):
        super(uic, self).__init__()
        self.setupUi(self)
        self.wifiimglb.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "wifi-close.png")))
        self.wifiimglb.setScaledContents(True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.datehandel)
        self.timer.start(1000)
        threading.Thread(target=self.wifihandel, daemon=True).start()
        self.conn.connect(self.connhandel)
        self.noteui = noteuic(self)
        self.qaui = qauic(self)
        self.stackedWidget.setCurrentIndex(0)
        self.menubtn1.clicked.connect(self.menubtn1_clicked)
        self.menubtn2.clicked.connect(self.menubtn2_clicked)
        self.menubtn4.clicked.connect(self.menubtn4_clicked)
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.savebtn.clicked.connect(self.savebtn_clicked)
        self.data = {}
        self.emailedit.setText(function.get_email_account())
        self.wifiaccedit.setText(function.get_ssid())
        self.wifipwdedit.setText(function.get_password())
        self.courseui = courseuic(self)
        self.menubtn3.clicked.connect(self.menubtn3_clicked)
        self.button.clicked.connect(self.button_clicked)
        self.button_2.clicked.connect(self.button_2_clicked)
        self.button_3.clicked.connect(self.button_3_clicked)
        self.settinginputui = settinginputuic(self)
        # ...

    def savebtn_clicked(self):
        function.change_email_account(self.emailedit.text())
        function.restore_ssid(self.wifiaccedit.text())
        function.restore_password(self.wifipwdedit.text())
        try:
            wifi = pywifi.PyWiFi()  # 获取wifi
            interface = wifi.interfaces()[0]  # 获取wifi信息列表
            profile = wifiUtils.set_profile(function.get_ssid(), function.get_password())  # 设置wifi属性
            con = wifiUtils.connet_wifi(interface, profile)  # 连接wifi
        except Exception as e:
            print(e)

    # 研学笔记
    def menubtn1_clicked(self):
        self.hide()
        self.noteui.email = function.get_email_account()
        self.noteui.show()

    # 实时问答
    def menubtn2_clicked(self):
        self.qaui.show()
        self.hide()
    def menubtn3_clicked(self):
        self.courseui.show()
        self.hide()
    # 设置
    def menubtn4_clicked(self):
        self.stackedWidget.setCurrentIndex(1)

    # 返回
    def returnbtn_clicked(self):
        self.stackedWidget.setCurrentIndex(0)

    # 修改图标
    def connhandel(self, wifi):
        if wifi:
            self.wifiimglb.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "wifi.png")))
        else:
            self.wifiimglb.setPixmap(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "wifi-close.png")))

    # 时间展示
    def datehandel(self):
        now = datetime.datetime.now()
        self.timelb.setText(now.strftime('%Y-%m-%d %H:%M:%S'))

    # 是否能连接到网络 现在以是否能连接到baidu为判断标准
    def wifihandel(self):
        while True:
            wifi = wifiUtils.get_webPage()
            self.conn.emit(wifi)
            time.sleep(2)
    def button_clicked(self):
    
        self.settinginputui.camrun.set()
        self.settinginputui.set_email()
        
        self.hide()
    def button_2_clicked(self):
        self.settinginputui.camrun.set()
        self.settinginputui.set_ssid()
        
        self.hide()
        
    def button_3_clicked(self):
        self.settinginputui.camrun.set()
        self.settinginputui.set_password()
        
        self.hide()
        

if __name__ == "__main__":
    # data/img/ 不入库，cv2.imwrite 遇到不存在的目录会静默失败
    os.makedirs("data/img", exist_ok=True)
    app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette, qt_api='pyqt5'))
    ui = uic()
    ui.show()
    sys.exit(app.exec_())