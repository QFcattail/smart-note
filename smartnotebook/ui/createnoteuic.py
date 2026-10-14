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
from ui.createnoteui import Ui_MainWindow
from ui.inputuic import uic as inputuic
from services.WenxinNote import ee
from app import app
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据
    def __init__(self,noteui):
        super(uic, self).__init__()
        ee.on('new_introduction', self.new_content)
        self.setupUi(self)
        # 禁用文本选择
        self.resulttext.setTextInteractionFlags(Qt.NoTextInteraction)
        # 启用触摸滚动
        QScroller.grabGesture(self.resulttext.viewport(), QScroller.LeftMouseButtonGesture)
        self.returnbtn.clicked.connect(self.returnbtn_clicked)
        self.titlebtn.clicked.connect(self.titlebtn_clicked)
        self.createbtn.clicked.connect(self.createbtn_clicked)
        self.deletebtn.clicked.connect(self.deletebtn_clicked)
        self.noteui = noteui
        self.datas = {} #存当前笔记的标签与答案 图片数据
        self.note_current_num = -1 #添加笔记时为空 如果是修改时，这个变量里存着要修改的key
        self.isdelete = False #是否删除了本条笔记
        self.inputui = inputuic(self)
        self.listWidget.currentTextChanged.connect(self.lictwidget_itemchangedd)
        QScroller.grabGesture(self.listWidget.viewport(), QScroller.LeftMouseButtonGesture)
        self.imglb.mousePressEvent = self.labelmousePressEvent
        
    def new_content(self,new_content,note,keyword):
        print("new_c")
        self.current_keyword=keyword
        Ui_MainWindow.current_keyword = self.current_keyword
        Ui_MainWindow.note_current_num=self.note_current_num
        self.set_current_item(keyword)
        function.add_content(new_content,note,keyword)
        self.showdata()
        self.update_result(note,keyword)
    def labelmousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.listWidget.currentItem() is not None:
                self.current_keyword = self.listWidget.currentItem().text()
                
                self.imglb.setPixmap(QPixmap(""))
                self.resulttext.clear()
                
                Ui_MainWindow.current_keyword = self.current_keyword
                
                # print(self.current_keyword)
                Ui_MainWindow.note_current_num=self.note_current_num
                self.inputui.camrun.set()
                self.inputui.update_img()
    def set_current_item(self, keyword):
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).text() == keyword:
                self.listWidget.setCurrentItem(self.listWidget.item(i))
                break
    def lictwidget_itemchangedd(self):
        try:
            if self.listWidget.currentItem() is not None:
                #print("press lict")
                self.current_keyword=self.listWidget.currentItem().text()
                #print(self.note_current_num,self.current_keyword)
                self.resulttext.setHtml(function.get_content(self.note_current_num,self.current_keyword))
                self.imglb.setPixmap(QPixmap(function.get_img_path(self.note_current_num,self.current_keyword)))
        except Exception as e:
            print(e)
    def update_result(self,note,keyword):
        self.resulttext.setHtml(function.get_content(note,keyword))
        self.imglb.setPixmap(QPixmap(function.get_img_path(note,keyword)))
        app.processEvents() 

    # 显示传递过来的值
    def showdata(self):
        #print("showdata")
        self.listWidget.clear()
        if self.note_current_num:
            self.titlebtn.setText(function.get_title(self.note_current_num))
            
            #self.titlebtn.setText(self.note_current_num.split("||")[0])
            self.listWidget.addItems(function.get_keywords(self.note_current_num))
            #print(function.get_keywords(self.note_current_num))

    def show(self):
        super(uic, self).show()

    # 点击返回按钮
    def returnbtn_clicked(self):
        now = datetime.datetime.now()
        self.isdelete = False #初始化本界面
        self.note_current_num = -1
        self.imglb.setPixmap(QPixmap(""))
        self.resulttext.setHtml("")
        self.listWidget.clear()
        self.titlebtn.setText("笔记标题")
        self.noteui.updatelist() #更新笔记列表
        self.noteui.show()
        self.hide()

    # 删除数据
    def deletebtn_clicked(self):
        
        function.delete_note(self.note_current_num)
        self.isdelete = True
        self.returnbtn_clicked()

    def titlebtn_clicked(self):
        Ui_MainWindow.note_current_num=self.note_current_num
        self.inputui.camrun.set()
        self.inputui.set_title()
        
        self.hide()

    def createbtn_clicked(self):
        Ui_MainWindow.note_current_num=self.note_current_num
        self.inputui.camrun.set()
        self.inputui.set_keyword()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())