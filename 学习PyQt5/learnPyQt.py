import sys
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
 
 
class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.resize(600, 600)
 
        self.begin_point = QPoint()
        self.end_point = QPoint()
 
        self.pix = QPixmap(600, 600)
        self.pix.fill(Qt.white)
 
        self.print_btn = QPushButton(self)              # 1
        self.print_btn.setIcon(QIcon('printer.png'))
 
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.h_layout.addWidget(self.print_btn)
        self.h_layout.addStretch(1)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addStretch(1)
 
        self.setLayout(self.v_layout)
 
    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)                                
        painter.drawPixmap(0, 0, self.pix)
 
        if self.begin_point and self.end_point:                 
            rect = QRect(self.begin_point, self.end_point)
            painter.drawRect(rect)
 
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.begin_point = QMouseEvent.pos()
            self.end_point = self.begin_point
            self.update()
 
    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == Qt.LeftButton:
            self.end_point = QMouseEvent.pos()
            self.update()
 
    def mouseReleaseEvent(self, QMouseEvent):                   
        if QMouseEvent.button() == Qt.LeftButton:
            painter = QPainter(self.pix)
            rect = QRect(self.begin_point, self.end_point)
            painter.drawRect(rect)
            self.begin_point = self.end_point = QPoint()
            self.update()
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())