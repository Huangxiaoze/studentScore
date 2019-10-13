
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import *
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
from table import studentTable, classTable, courseTable, escoreTable, examTable, questionTable
import json
class DataBase(QTableView):
    def __init__(self):
        super(DataBase, self).__init__()
        self.db = None
        self.db_connect()

        self.model = QSqlTableModel()

        self.student_table = studentTable.Student(self.model)
        self.class_table = classTable.Class(self.model)
        self.course_table = courseTable.Course(self.model)
        self.escore_table = escoreTable.EScore(self.model)
        self.exam_table = examTable.Exam(self.model)
        self.question_table = questionTable.Question(self.model)
        self.createTable()
        print(self.student_table.find(course_id = 9,classid = 7))


        #print(self.escore_table.find())
        #self.student_table.insert('2017151024','黄小泽',1,1)
        #self.exam_table.insert('平时考试','2019-10-1',1,1,'0-1-2-3','2,2,2,4')
        #self.exam_table.delete(1)
        #self.student_table.find(id=1)
        #self.exam_table.update(3,classid=2)

        #self.question_table.delete(1)

        # questions = ['选择题','填空题','简答题','附加题']
        # for question in questions:
        #     self.question_table.insert(question)


        #self.class_table.insert('A班',1)
        #self.class_table.delete(id)
        #self.course_table.insert('10010','中国电信')
        #self.course_table.update(2,courseName="啥？",courseNumber="2019")
        #self.course_table.delete(1)
        #print(self.course_table.get_course_amount())

        

    def createTable(self):
        self.course_table.createTable()
        self.question_table.createTable()
        self.class_table.createTable()
        self.student_table.createTable()
        self.exam_table.createTable()
        self.escore_table.createTable()


    def db_connect(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')    # 1
        self.db.setDatabaseName('./学生成绩数据库.db')             # 2

        if not self.db.open():                           # 3
            QMessageBox.critical(self, 'Database Connection', self.db.lastError().text())

    def closeDB(self):
        self.db.close()
        
    def closeEvent(self, QCloseEvent):
        self.db.close()
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    DataBas = DataBase()
    DataBas.show()
    sys.exit(app.exec_())
