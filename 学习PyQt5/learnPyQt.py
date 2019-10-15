#-*- coding:utf-8 -*-
'''
defined Signal
'''
__author__ = 'Tony Zhu'
import sys
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot
from PyQt5.QtWidgets import *


class SignalEmit(QWidget):
    sayHello = pyqtSignal(str)
    def __init__(self):
        super().__init__()        
        QPushButton('hello',self).clicked.connect(self.emitSayHello)
        self.sayHello.connect(self.sayHelloTo)
        self.show()
    def sayHelloTo(self,name):
        QMessageBox.information(self,'hh','hhh{}'.format(name))
    def emitSayHello(self):
        self.sayHello.emit("黄小泽")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    dispatch = SignalEmit()
    sys.exit(app.exec_())
