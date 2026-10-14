import datetime
import sys
import threading
import time
import traceback
from core import function
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView, \
    QScroller
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.qahistoryui import Ui_MainWindow
from ui.qaresultuic import uic as qaresultuic
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据
    def __init__(self,mainui):
        super(uic, self).__init__()
        self.setupUi(self)
        self.mainui = mainui
        self.qaresultui = qaresultuic(self)
        self.tableWidget.setSelectionBehavior(True)
        self.tableWidget.verticalHeader().setHidden(True)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(300)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.tableWidget.clicked.connect(self.itemDoubleClicked)
        QScroller.grabGesture(self.tableWidget.viewport(), QScroller.LeftMouseButtonGesture)

        self.datas={}

    # 双击表格
    def itemDoubleClicked(self):
        row = self.tableWidget.currentRow()
        current_question = int(self.tableWidget.item(row, 2).text())
        QandA_html=function.get_qa_history_item(current_question)
        self.qaresultui.textBrowser_2.setHtml(QandA_html)
        self.qaresultui.is_history=1
        self.qaresultui.open()
        
        
        self.hide()

    def returnbtn_clicked(self):
        self.mainui.show()
        self.hide()

    # 更新表格内容
    def updatelist(self):
        try:
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)
            self.datas=function.get_qa_history_list()
            #print(self.datas)
            #print(type(self.datas))
            row_pos=0
            for k in self.datas:
                
                self.tableWidget.insertRow(0)
                self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(self.datas[row_pos]["question"]))
                self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.datas[row_pos]["date"]))
                self.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(str(self.datas[row_pos]["num"])))
                self.tableWidget.setRowHeight(0, 60)
                self.tableWidget.setColumnWidth(0, 500)
                self.tableWidget.setColumnWidth(1, 300)
                row_pos+=1
        except Exception as e:
            traceback.print_exc()

    # 排序
    def sort_data_by_date(self, data_list):
        return sorted(data_list, key=lambda x: x.split('||')[1], reverse=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())