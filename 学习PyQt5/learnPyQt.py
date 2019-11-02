import sys
from PyQt5.QtWidgets import *
class MainWindow(QMainWindow):
    def __init__(self,):
        super(QMainWindow,self).__init__()
 
        w = QWidget(self)
        #self.setCentralWidget(w)
        w.resize(250,200)
        w.setLayout(QHBoxLayout())
        layout = w.layout()
        del layout
        w.setLayout(QVBoxLayout())
        self.resize(300, 500)
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())