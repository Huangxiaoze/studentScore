# coding=utf-8
 
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
import sys
 
 
class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.resize(550, 300)
        self.setWindowTitle('动态删除增加控件测试')
        self.CreatUI()
 
    def CreatUI(self):
        self.lb1 = QPushButton("按键1", self)
        self.lb1.setGeometry(100, 200, 100, 50)
        self.lb2 = QPushButton("按键1", self)
        self.lb2.setGeometry(280, 200, 100, 50)
 
        self.bt1 = QPushButton('删除', self)
        self.bt2 = QPushButton('新建', self)
 
        self.bt1.move(100, 20)
        self.bt2.move(280, 20)
 
        self.bt1.clicked.connect(self.deleteWidget)
        self.bt2.clicked.connect(self.addWidget)
 
    def deleteWidget(self):
        self.lb1.deleteLater()
        self.lb2.deleteLater()
        self.bt1.deleteLater()
 
    def addWidget(self):
        self.CreatUI()
        self.showWidget()
 
    def closeWidget(self):
        # self.lb1.close()
        # self.lb2.close()
        # self.bt1.close()
        # 或者使用hide
        self.lb1.hide()
        self.lb2.hide()
        self.bt1.hide()
 
    def showWidget(self):
        self.lb1.show()
        self.lb2.show()
        self.bt1.show()
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())