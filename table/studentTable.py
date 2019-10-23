
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel,QSqlQuery
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
 
 
class Student(QTableView):
    def __init__(self,db):
        super(Student, self).__init__()
        self.db = db

    def createTable(self):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        model.exec_(
            """
            create table student(
                id integer not null primary key,
                number varchar(20),
                name varchar(40),
                classid int,
                course_id int,
                constraint classid foreign key(classid) references class(id),
                constraint courseid foreign key(course_id) references course(id)
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
            if key in ['id', 'classid','course_id']: 
                condition.append("{0}={1}".format(key,value))
            else:
                condition.append("{0}='{1}'".format(key,value))
        And = " and ".join(condition)
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        if condition!=[]:
            sql = 'select * from student where {}'.format(And)
        else:
            sql = 'select * from student'
        model.exec_(sql)
        res = []
        while model.next():
            #print((model.value(0),model.value(1),model.value(2),model.value(3),model.value(4)))
            res.append((model.value(0),model.value(1),model.value(2),model.value(3),model.value(4)))
        return res

    def update(self,id,**args):
        if args == None:
            return
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        for key, value in args.items():
            sql = "update student set {0}='{1}' where id={2}".format(key,value,id)
            model.exec_(sql)

    def delete(self,id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "delete from student where id={}".format(id)
        res = model.exec_(sql)
        return res

    def insert(self, number,name,classid,course_id):
        try:
            model = QSqlQuery()
            model.exec_('PRAGMA foreign_keys = ON;')
            sql = """
            insert into student(number,name,classid,course_id) 
            values('{0}','{1}',{2},{3})
            """.format(number,name,classid,course_id)
            model.exec_(sql)
        except e:
            pass
            #print(e)
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Student()
    demo.show()
    sys.exit(app.exec_())
