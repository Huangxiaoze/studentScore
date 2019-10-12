
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel,QSqlQuery
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
 
 
class Course(QTableView):
    def __init__(self,model):
        super(Course, self).__init__()
        self.model = model

    def createTable(self):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        model.exec_(
            """
            create table course(
                id INTEGER not null primary key,
                courseNumber varchar(20) not null,
                courseName varchar(50) not null
            )

            """
            )  

    def get_all_course_data(self):
        return self.find()

    def get_course_amount(self):
        return len(self.find())

    def find(self,**args):
        condition = []
        for key, value in args.items():   
            condition.append("{0}='{1}'".format(key,value))
        And = " and ".join(condition)
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        if condition!=[]:
            sql = 'select * from course where {};'.format(And)
        else:
            sql = 'select * from course'
        model.exec_(sql)
        res = []
        while model.next():
            #print((model.value(0),model.value(1),model.value(2)))
            res.append((model.value(0),model.value(1),model.value(2)))
        return res

    def update(self,id,**args):
        if args == None:
            return
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        for key, value in args.items():
            sql = "update course set {0}='{1}' where id={2}".format(key,value,id)
            model.exec_(sql)

    def delete(self,id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "delete from course where id={}".format(id)
        model.exec_(sql)

    def insert(self, courseNumber, courseName):
        try:
            model = QSqlQuery()
            model.exec_('PRAGMA foreign_keys = ON;')
            sql = "insert into course(courseNumber,courseName) values('{0}','{1}')".format(courseNumber,courseName)
            model.exec_(sql)
        except e:
            pass
            #print(e)


 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Cours = Course()
    Cours.show()
    sys.exit(app.exec_())
