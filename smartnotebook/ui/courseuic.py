import datetime
import sys
import threading
import time
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView, \
    QScroller
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.courseui import Ui_MainWindow
from ui.createcourseuic import uic as createui
import traceback
from services import mailUtils
from core import function
from app import app
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据
    def __init__(self,mainui):
        super(uic, self).__init__()
        self.setupUi(self)
        self.email = ""
        self.tableWidget.setSelectionBehavior(True)
        self.tableWidget.verticalHeader().setHidden(True)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(300)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.datas = {} #存所有笔记的所有数据 {"xxx||时间":[问题,答案,图片路径]}}
        self.createui = createui(self)
        self.createbtn.clicked.connect(self.create)
        self.mainui = mainui
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.sendtoemail = ""
        self.tableWidget.clicked.connect(self.itemDoubleClicked)
        QScroller.grabGesture(self.tableWidget.viewport(), QScroller.LeftMouseButtonGesture)
        self.updatelist()
  
    def itemDoubleClicked(self):

        row = self.tableWidget.currentRow()
        course_current_num = int(self.tableWidget.item(row,2).text())
        self.createui.course_current_num = course_current_num
        self.createui.showdata() #把数据填入界面
        self.createui.show()
        self.hide()

    # 更新表格内容
    def updatelist(self):
        try:
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)
            course_list = function.get_course_list()
            course_list = self.sort_data_by_date(course_list)
            row_pos=0
            for course_item in course_list:
                self.tableWidget.insertRow(0)
                self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(course_item["name"]))
                self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(course_item["date"]))
                self.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(course_item["num"])))
                self.tableWidget.setRowHeight(0, 60)
                
                row_pos+=1
        except Exception as e:
            traceback.print_exc()

    # 排序
    def sort_data_by_date(self,data_list):
        return sorted(data_list, key=lambda d: datetime.strptime(d['date'], '%Y-%m-%d'), reverse=True)
            

    def create(self):
        course_current_num=function.create_course()
        self.createui.course_current_num = course_current_num
        
         
        self.createui.show()
        self.hide()
        self.createui.showdata()

    def returnbtn_clicked(self):
        self.mainui.show()
        self.hide()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())