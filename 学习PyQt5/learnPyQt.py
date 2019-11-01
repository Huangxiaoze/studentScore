import sys
from PyQt5.QtWidgets import *
 
 
class MainWindow(QMainWindow):
    def __init__(self,):
        super(QMainWindow,self).__init__()
        self.number = 0
 
        w = QFrame(self)
        w.resize(200,200)
        w.setStyleSheet('background:red;')
     
        # scroll_area = QScrollArea()
        # scroll_area.setWidget(w)
  
        # scroll_area.show()


        self.statusBar().showMessage("底部信息栏")
        self.resize(300, 500)
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())