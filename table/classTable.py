
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel,QSqlQuery
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
 
 
class Class(QTableView):
    def __init__(self, db):
        super(Class, self).__init__()
        self.db = db
    
    def get_all_course_data(self):
        return self.find()

    def get_course_amount(self):
        return len(self.find())

    def createTable(self):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        model.exec_(
            """
            create table class(
                id integer not null primary key,
                className varchar(50) not null,
                course_id int,
                constraint courseid foreign key(course_id) references course(id)
            )

            """
            )
    def find(self,**args):
        condition = []
        for key, value in args.items(): 
            if key == 'className':  
                condition.append("{0}='{1}'".format(key,value))
            else:
                condition.append("{0}={1}".format(key,value))
        And = " and ".join(condition)
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        if condition!=[]:
            sql = 'select * from class where {};'.format(And)
        else:
            sql = 'select * from class'
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
            sql = "update class set {0}='{1}' where id={2}".format(key,value,id)
            model.exec_(sql)

    def delete(self,id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "delete from class where id={}".format(id)
        res = model.exec_(sql)
        return res

    def insert(self,className,course_id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "insert into class(className, course_id) values('{0}',{1})".format(className,course_id)
        
        exec_result = model.exec_(sql)
        return exec_result
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    s = Class()
    s.show()
    sys.exit(app.exec_())
