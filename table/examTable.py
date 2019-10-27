
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel,QSqlQuery
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
from datetime import datetime
 
class Exam(QTableView):
    def __init__(self,db):
        super(Exam, self).__init__()
        self.db = db

    def createTable(self):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        model.exec_(
            """
            create table exam(
                id integer not null primary key,
                examName varchar(50),
                examtime varchar(50),
                classid int,
                courseid int,
                exam_weight int,
                question_type text,
                weight_set text,
                constraint classid foreign key(classid) references class(id),
                constraint courseid foreign key(courseid) references course(id)
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
            if key not in ['id','classid','courseid','exam_weight']:  
                condition.append("{0}='{1}'".format(key,value))
            else:
                condition.append("{0}={1}".format(key,value))
        And = " and ".join(condition)
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        if condition!=[]:
            sql = 'select * from exam where {};'.format(And)
        else:
            sql = 'select * from exam'
        model.exec_(sql)
        res = []
        while model.next():
            #print((model.value(0),model.value(1),model.value(2)))
            res.append((
                model.value(0),
                model.value(1),
                model.value(2),
                model.value(3),
                model.value(4),
                model.value(5),
                model.value(6),
                model.value(7)
                ))
        return res

    def update(self,id,**args):
        if args == None:
            return
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        for key, value in args.items():
            sql = "update exam set {0}='{1}' where id={2}".format(key,value,id)
            model.exec_(sql)

    def delete(self,id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "delete from exam where id={}".format(id)
        model.exec_(sql)

    def insert(self, examName,examtime,classid,courseid,question_type,weight_set,exam_weight):
        try:
            print("hello")
            model = QSqlQuery()
            model.exec_('PRAGMA foreign_keys = ON;')
            # datetime.datetime.strptime(str,'%Y-%m-%d')
            sql = """
            insert into exam(examName,classid,courseid,question_type,weight_set,examtime,exam_weight) 
            values('{0}',{1},{2},'{3}','{4}','{5}',{6})
            """.format(examName,classid,courseid,question_type,weight_set,examtime,exam_weight)
            res = model.exec_(sql)
        except e:
            pass
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Exa = Exam()
    Exa.show()
    sys.exit(app.exec_())
