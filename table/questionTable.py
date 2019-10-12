
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel,QSqlQuery
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
 
 
class Question(QTableView):
    def __init__(self,db):
        super(Question, self).__init__()
        self.db = db

    def createTable(self):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        model.exec_(
            """
            create table questions(
                id integer not null primary key,
                questionName varchar(50)
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
            sql = 'select * from questions where {};'.format(And)
        else:
            sql = 'select * from questions'
        model.exec_(sql)
        res = []
        while model.next():
            #print((model.value(0),model.value(1)))
            res.append((model.value(0),model.value(1)))
        return res

    def update(self,id,**args):
        if args == None:
            return
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        for key, value in args.items():
            sql = "update questions set {0}='{1}' where id={2}".format(key,value,id)
            model.exec_(sql)

    def delete(self,id):
        model = QSqlQuery()
        model.exec_('PRAGMA foreign_keys = ON;')
        sql = "delete from questions where id={}".format(id)
        model.exec_(sql)

    def insert(self, questionName):
        try:
            model = QSqlQuery()
            model.exec_('PRAGMA foreign_keys = ON;')
            sql = "insert into questions(questionName) values('{0}');".format(questionName)
            model.exec_(sql)
        except:
            #print("helo")
            pass

 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Questio = Question()
    Questio.show()
    sys.exit(app.exec_())
