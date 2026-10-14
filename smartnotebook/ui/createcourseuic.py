import datetime
import sys
import threading
import time
from core import function
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView, \
    QScroller
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.createcourseui import Ui_MainWindow
from ui.courseinputuic import uic as inputuic
from services.WenxinCourse import ee
from app import app
from markdown import markdown
from core.function import ee_course_question
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据
    def __init__(self,courseui):
        super(uic, self).__init__()
        self.question=""
        self.content=""
        ee_course_question.on("return_course_question",self.get_question)
        ee.on('new_course_result', self.new_content)
        self.setupUi(self)
        # 禁用文本选择
        self.resulttext.setTextInteractionFlags(Qt.NoTextInteraction)
        # 启用触摸滚动
        QScroller.grabGesture(self.resulttext.viewport(), QScroller.LeftMouseButtonGesture)
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.titlebtn.clicked.connect(self.titlebtn_clicked)
        self.askbtn.clicked.connect(self.askbtn_clicked)
        self.deletebtn.clicked.connect(self.deletebtn_clicked)
        self.courseui = courseui
        self.datas = {} #存当前课程的标签与答案 图片数据
        self.course_current_num = -1 #添加课程时为空 如果是修改时，这个变量里存着要修改的key
        self.isdelete = False #是否删除了本条课程
        self.inputui = inputuic(self)
        
        
    def new_content(self,new_content):
        print("new_c")
        self.content+=new_content
        html=markdown("#"+self.question+"\n\n"+self.content)
        self.resulttext.setHtml(html)
        app.processEvents()

    def get_question(self,question):
        self.question=question
    # 显示传递过来的值
    def showdata(self):
        if self.course_current_num:
            self.content=""
            self.question=""
            self.titlebtn.setText(function.get_course_title(self.course_current_num))
            self.playVideo(function.get_course_url(self.course_current_num))
            if function.get_course_url(self.course_current_num)=="":
                print("new")
                self.inputui.camrun.set()
                self.inputui.set_QRcode()
                self.hide()
            else:
                print("edit")
    def show(self):
        super(uic, self).show()

    # 点击返回按钮
    def returnbtn_clicked(self):
        now = datetime.datetime.now()
        self.isdelete = False #初始化本界面
        self.course_current_num = -1
        
        self.resulttext.setHtml("")
        self.titlebtn.setText("课程标题")
        self.courseui.updatelist() #更新课程列表
        self.courseui.show()
        self.hide()

    # 删除数据
    def deletebtn_clicked(self):
        
        function.delete_course(self.course_current_num)
        self.isdelete = True
        self.returnbtn_clicked()

    def titlebtn_clicked(self):
        Ui_MainWindow.course_current_num=self.course_current_num
        self.inputui.camrun.set()
        self.inputui.set_title()
        
        self.hide()

    def askbtn_clicked(self):
        self.content=""
        self.question=""
        if function.is_task_running(self.course_current_num):
            self.askbtn.setText("正在转写")
        else:
            self.askbtn.setText("提问")
            Ui_MainWindow.course_current_num=self.course_current_num
            self.inputui.camrun.set()
            self.inputui.set_question()
            self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())