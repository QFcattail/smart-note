import datetime
import sys
import threading
import time
import json
from markdown import markdown
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView, \
    QScroller
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.qaresultui import Ui_MainWindow
from app import app
from services.WenxinQa import ee
from core.function import ee_question
from core import function
class uic(QMainWindow, Ui_MainWindow):
    conn = pyqtSignal(object)  # 处理动态数据    
    def __init__(self,mainui):
        super(uic, self).__init__()
        self.answer=""
        self.is_history=0
        # self.answerconn.connect(self.update_answer)
        ee.on('new_result', self.update_answer)
        ee_question.on("return_question",self.update_question)
        self.setupUi(self)
        self.mainui = mainui
        self.question=""
        self.answer_json=""
        self.returnbtn_2.clicked.connect(self.returnbtn_clicked)
        # 禁用文本选择
        self.textBrowser_2.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # 启用触摸滚动
        QScroller.grabGesture(self.textBrowser_2.viewport(), QScroller.LeftMouseButtonGesture)
        font = self.textBrowser_2.font()
        font.setPointSize(20)  # 设置字体大小为20
        self.textBrowser_2.setFont(font)
        self.continue_show=True
    def returnbtn_clicked(self):
        if self.is_history == 0:
            function.record_qa_history(self.question,self.QandA_html)
        self.mainui.show()
        self.hide()
        #self.continue_show=False
    def update_question(self,new_questhon):
        self.question=new_questhon
    def update_answer(self,new_answer):
        
        self.answer+=new_answer
        self.QandA_html=markdown('# '+self.question + '\n\n' +self.answer)
        self.textBrowser_2.setHtml(self.QandA_html)
        app.processEvents() 
        
    def open(self):
        self.continue_show=True
        self.show()
        # answer=""
        # for line in self.answer_json:
        #     if not self.continue_show:
        #         break
        #     line=line.decode('utf-8')
        #     line=line[6:]
            
        #     try:
        #         line=json.loads(line)
        #         answer+=line["result"]
        #         QandA_html=markdown('# '+self.question + '\n\n' + answer)
        #         #刷新显示
        #         self.textBrowser_2.setHtml(QandA_html)
        #         #text_browser.setHtml(QandA_html)
        #         app.processEvents()            
            
        #     except:
        #         pass
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = uic(None)
    ui.show()
    sys.exit(app.exec_())