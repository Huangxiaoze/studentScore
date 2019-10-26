
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
        #self.mysql_connect()
        self.model = QSqlTableModel()
        self.student_table = studentTable.Student(self.model)
        self.class_table = classTable.Class(self.model)
        self.course_table = courseTable.Course(self.model)
        self.escore_table = escoreTable.EScore(self.model)
        self.exam_table = examTable.Exam(self.model)
        self.question_table = questionTable.Question(self.model)
        self.createTable()

    def mysql_connect(self):
        self.db = QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName('localhost')
        self.db.setDatabaseName('studentscore')
        self.db.setUserName('root')
        self.db.setPassword('0128huang')
        if not self.db.open():                           # 3
            QMessageBox.critical(self, 'Database Connection', self.db.lastError().text())

    def getCourseName(self):
        name = []
        name_to_id = {}
        all_course = self.course_table.find()
        for course in all_course:
            name.append(course[-1])
            name_to_id[course[-1]] = course[0]
        return name, name_to_id

    def getClassName(self,courseid = None):
        name = []
        name_to_id = {}
        if courseid==None:
            all_class = self.class_table.find()
        else:
            all_class = self.class_table.find(course_id = courseid)
        for class_ in all_class:
            name.append(class_[1])
            name_to_id[class_[1]] = class_[0]
        return name, name_to_id

    def getExamName(self,courseid = None, classid = None):
        name = []
        if courseid == None and classid == None:
            all_exam = self.exam_table.find()
        else:
            all_exam = self.exam_table.find(courseid = courseid,classid = classid)
        for exam in all_exam:
            name.append(exam[1])
        if courseid == None and classid == None:
            return name
        else:
            name_to_id = {}
            for exam in all_exam:
                name_to_id[exam[1]] = exam[0]
            return name, name_to_id

    def getQuestionName(self):
        name = []
        name_to_id = {}
        all_question = self.question_table.find()
        for question in all_question:
            name.append(question[-1])
            name_to_id[question[-1]] = question[0]
        return name, name_to_id       
        

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
