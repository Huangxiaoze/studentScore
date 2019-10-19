#coding:utf-8
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui  import *
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
import json
from db import DataBase
import processData 
import time
from collections import defaultdict
from decimal import Decimal
#仅仅windows支持
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myappid')
#

class loadQSS:
	@staticmethod
	def getStyleSheet(file):
		with open(file,'r') as f:
			return f.read()
class ScoreTable(QTableWidget):
	sortSignal = pyqtSignal(int)
	def __init__(self):
		super().__init__()
		self.horizontalHeader().connect(self.sortTable)

class studentScoreManage(QMainWindow):
	def __init__(self):
		splash = QSplashScreen(QPixmap("windowIcon.png"))
		splash.showMessage("加载中... ", Qt.AlignHCenter | Qt.AlignBottom, Qt.black)
		splash.show()  
		super().__init__()
		self.initDataBase()
		self.initWindow()
		#time.sleep(2)
		self.show()
		splash.finish(self)

	def initDataBase(self):
		self.database = DataBase()

	def initWindow(self):
		self.resize(1620,650)
		self.setWindowIcon(QIcon('./windowIcon.png'))
		self.setWindowTitle('成绩管理')
		with open('./setting.json','r') as f:
			content = f.read()
		self.setting = json.loads(content)#设置
		
		self.splitter = QSplitter(self) #视图布局
		self.leftwidget = QWidget() #左视图
		self.midwidget = QWidget()  #中视图
		self.rightwidget = QWidget() #右视图

		self.splitter.resize(self.width(),self.height()-50)
		self.splitter.move(0,50)
		self.splitter.addWidget(self.leftwidget)
		self.splitter.addWidget(self.midwidget)
		self.splitter.addWidget(self.rightwidget)
		self.splitter.setSizes([200,920,500])

		self.initleftwidget()
		self.initmidwidget()
		self.initrightwidget()
		self.initMenu()
		
	def initrightwidget(self):
		message = QLabel('考试信息',self.rightwidget)
		message.move(100,20)
		self.r_widget = None

	def initMenu(self):
		self.build_menu = self.menuBar().addMenu('新建')  # 菜单栏
		self.load_menu = self.menuBar().addMenu('导入')  #
		self.help_menu = self.menuBar().addMenu('帮助')  #

		self.new_toolbar = self.addToolBar('newExam')
		self.load_toolbar = self.addToolBar('File') # 工具栏
		self.edit_toolbar = self.addToolBar('Edit')

		self.status_bar = self.statusBar() # 状态显示

		self.load_action = QAction('导入成绩', self)				# 动作
		self.dump_action = QAction('导出成绩', self)				#
		self.setweight_action = QAction('设置权重', self)		#
		self.view_action = QAction('查看总成绩', self)			#
		self.save_action = QAction('保存修改', self)				#
		self.newExam_action = QAction('添加考试')				#
		self.newcourse_action = QAction('课程')
		self.newclass_action = QAction('班级')
		self.load_studentData_action = QAction('导入学生',self)
		self.newQuestion_action = QAction('题型',self)


		self.newExam_action.setIcon(QIcon(r'./images/exam1.ico')) #设置图标
		self.load_studentData_action.setIcon(QIcon(r'./images/s.ico'))
		self.load_action.setIcon(QIcon(r'./images/loadScore2.ico'))
		self.newcourse_action.setIcon(QIcon(r'./images/blackboard.ico'))
		self.newclass_action.setIcon(QIcon(r'./images/class.ico'))
		self.newQuestion_action.setIcon(QIcon(r'./images/question.ico'))
		self.dump_action.setIcon(QIcon(r'./images/dump.ico'))

		self.load_action.triggered.connect(self.loadData)		# 动作事件响应
		self.dump_action.triggered.connect(self.dumpData)		#
		self.newcourse_action.triggered.connect(self.createCourse)
		self.newclass_action.triggered.connect(self.createClass)
		self.load_studentData_action.triggered.connect(self.loadStudentData)
		self.newExam_action.triggered.connect(self.createNewExam)
		self.newQuestion_action.triggered.connect(self.addQuestion)


		self.new_toolbar.addAction(self.newExam_action)		# 将动作添加到工具栏
		self.new_toolbar.addAction(self.newcourse_action)
		self.new_toolbar.addAction(self.newclass_action)
		self.new_toolbar.addAction(self.newQuestion_action)

		self.load_toolbar.addAction(self.load_action)
		self.load_toolbar.addAction(self.dump_action)
		self.load_toolbar.addAction(self.load_studentData_action)

		self.edit_toolbar.addAction(self.setweight_action)
		self.edit_toolbar.addAction(self.view_action)


		self.build_menu.addAction(self.newcourse_action)			# 将动作添加到菜单栏
		self.build_menu.addAction(self.newclass_action)
		self.build_menu.addAction(self.newQuestion_action)
		self.load_menu.addAction(self.load_studentData_action)
		self.load_menu.addAction(self.load_action)


	def addQuestion(self):
		widget = QDialog(self)
		descLabel = QLabel('题型名称：')
		self.descLineEdit = QLineEdit()
		save_button = QPushButton('保存')
		save_button.clicked.connect(lambda:self.saveQuestion(widget))

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(descLabel)
		hlayout1.addWidget(self.descLineEdit)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addWidget(save_button)

		widget.setLayout(vlayout)
		widget.exec_()

	def saveQuestion(self,parent):
		self.database.question_table.insert(self.descLineEdit.text())
		QMessageBox.information(parent,'添加题型','成功')

	def addExam(self,parent): #添加一场考试
		x,courseName_to_id = self.database.getCourseName()
		y,className_to_id = self.database.getClassName()
		courseid = courseName_to_id[self.createexam_courseCombox.currentText()]
		classid = className_to_id[self.createexam_classCombox.currentText()]
		examName = self.examName_lineedit.text()
		examDate = str(self.examTime.date().toString("yyyy-MM-dd"))
		if self.database.exam_table.find(classid=classid, courseid = courseid,examName=examName) != []:
			QMessageBox.warning(parent,'错误','{0} {1} {2} 已存在，请更改考试名称。'.format(
				self.createexam_courseCombox.currentText(),
				self.createexam_classCombox.currentText(),
				examName
				),QMessageBox.Ok)
			return

		questionName = []
		weight = []
		headers_data = []

		for i,checkbox in enumerate(self.checkboxs):
			if checkbox.checkState() == Qt.Checked:
				questionName.append(checkbox.text())
				weight.append(self.weights[i].text())
				headers_data.append(checkbox.text())
		if questionName==[]:
			QMessageBox.warning(parent,'错误','请选择题型',QMessageBox.Ok)
			return

		question_name = "<|>".join(questionName)
		self.question_weight = "-".join(weight)

		
		self.database.exam_table.insert(
				examName,
				examDate,
				classid,
				courseid,
				question_name,
				self.question_weight,
				self.examweight_spinbox.value()
			)
		
		
		# headers,datas,weight_set = self.getTableData(
		# 	examName = examName,
		# 	examDate = examDate,
		# 	classid = classid,
		# 	courseid = courseid,
		# 	)
		# self.showScoreTable(headers,datas)
		select = QMessageBox.information(parent,'添加考试','成功添加，功能关闭',QMessageBox.Ok|QMessageBox.Cancel)
		if select == QMessageBox.Ok:
			print("hahahhaha")

	def getTableData(self, **args):#获取表数据
		exam = self.database.exam_table.find(
			examName= args['examName'],
			classid=int(args['classid']),
			courseid=int(args['courseid'])
			)

		if exam!=[]:
			examid = int(exam[0][0])
			question_name = exam[0][-2].split('<|>')
			weight_set = list(map(int,exam[0][-1].split('-')))


		headers = ['学号','姓名']
		headers.extend(question_name)

		students = self.database.student_table.find(
			classid=int(args['classid']),
			course_id=int(args['courseid'])
			)
		datas = []
		student_id = []
		for student in students:
			id_ = student[0]
			name = student[2]
			number = student[1]
			score = self.database.escore_table.find(
					examid=examid,
					studentid=int(student[0]),
					classid = int(args['classid']),
					courseid = int(args['courseid'])
				)

			if score!=[] and score[-1]!="":
				score_data = json.loads(score[0][-1]) #获取成绩
				res = [number,name]
				mark = 0     							#计算总成绩
				for i,qname in enumerate(question_name):
					res.append(score_data[qname])
					mark+=Decimal(str(score_data[qname]))*weight_set[i]/100
				res.append(str(mark))
				datas.append(res)
				student_id.append(id_)

		return headers,datas,weight_set, tuple(student_id)

	def setGetClass(self,parent,combox):
		courseid = self.createclass_name_to_id[parent.currentText()]
		all_class, x = self.database.getClassName(courseid)
		while combox.count() != 0:
			combox.removeItem(0)
		combox.addItems(all_class)

	def createNewExam(self):
		widget = QDialog(self)
		widget.setWindowTitle('添加考试')
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')
		self.examName_lineedit = QLineEdit()
		questiontype = QLabel('题型及权重：')

		examweight_label = QLabel("考试在总评中占比：")
		self.examweight_spinbox = QSpinBox()
		self.examweight_spinbox.setRange(0,100)
		self.examweight_spinbox.setValue(100)

		time_label = QLabel("考试日期：")
		self.examTime = QDateTimeEdit(QDateTime.currentDateTime())
		self.examTime.setCalendarPopup(True)

		subjectlist, self.createclass_name_to_id = self.database.getCourseName()
		question_list,x = self.database.getQuestionName()

		self.createexam_courseCombox = QComboBox()
		self.createexam_courseCombox.addItems(subjectlist)
		self.createexam_classCombox = QComboBox()

		self.createexam_courseCombox.currentIndexChanged.connect(lambda:self.setGetClass(self.createexam_courseCombox,self.createexam_classCombox))

		self.checkboxs = [ ]
		for question in question_list:
			question_checkbox = QCheckBox(question)
			self.checkboxs.append(question_checkbox)

		self.weights = []
		for i in range(len(question_list)):
			spinbox = QSpinBox()
			spinbox.setRange(0,100)
			spinbox.setValue(100)
			self.weights.append(spinbox)
		
		hlayouts = []

		for item in zip(self.checkboxs,self.weights):
			h = QHBoxLayout()
			h.addWidget(item[0])
			h.addWidget(item[1])
			hlayouts.append(h)

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(courselabel)
		hlayout1.addWidget(self.createexam_courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(self.createexam_classCombox)

		hlayout4 = QHBoxLayout()
		hlayout4.addWidget(time_label)
		hlayout4.addWidget(self.examTime)

		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(examName)
		hlayout3.addWidget(self.examName_lineedit)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addLayout(hlayout2)
		vlayout.addLayout(hlayout4)
		vlayout.addLayout(hlayout3)

		hlayoutt = QHBoxLayout()
		hlayoutt.addWidget(examweight_label)
		hlayoutt.addWidget(self.examweight_spinbox)

		vlayout.addLayout(hlayoutt)

		vlayout.addWidget(questiontype)
		for hlayout in hlayouts:
			vlayout.addLayout(hlayout)

		save_button = QPushButton('保存')
		save_button.clicked.connect(lambda:self.addExam(widget))
		vlayout.addWidget(save_button)

		widget.setLayout(vlayout)
		widget.exec_()


	def sayHello(self):
		print("hello")

	def loadStudentData(self):
		widget = QDialog(self)
		courselabel = QLabel('请选择课程')
		classlabel = QLabel('请选择班级')
		filepathlabel = QLabel("请输入文件路径")
		filepathbutton = QPushButton('点击选择文件')

		self.loadS_filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget,self.loadS_filepath))

		self.l_courseCombox = QComboBox()
		self.l_classCombox = QComboBox()
		subjectlist,  self.createclass_name_to_id= self.database.getCourseName()
		self.l_courseCombox.addItems(subjectlist)

		courseCombox_label = QLabel('请选择课程')
		self.l_courseCombox.currentIndexChanged.connect(lambda : self.setGetClass(self.l_courseCombox, self.l_classCombox))

		load = QPushButton('导入')
		load.clicked.connect(self.loadStudent)

		self.stunumber_spinbox = QSpinBox()
		self.stuname_spinbox = QSpinBox()
		self.stunumber_spinbox.setRange(1,100)
		self.stuname_spinbox.setRange(1,100)
		self.stunumber_spinbox.setValue(1)
		self.stuname_spinbox.setValue(2)


		#布局
		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(courselabel)
		hlayout1.addWidget(self.l_courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(self.l_classCombox)

		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(filepathlabel)
		hlayout3.addWidget(self.loadS_filepath)
		hlayout3.addWidget(filepathbutton)

		hlayout4 = QHBoxLayout()
		hlayout4.addWidget(QLabel("学号："))
		hlayout4.addWidget(self.stunumber_spinbox)

		hlayout5 = QHBoxLayout()
		hlayout5.addWidget(QLabel('姓名：'))
		hlayout5.addWidget(self.stuname_spinbox)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addLayout(hlayout2)
		vlayout.addLayout(hlayout3)
		vlayout.addWidget(QLabel('学生信息所在的列数：'))
		vlayout.addLayout(hlayout4)
		vlayout.addLayout(hlayout5)

		vlayout.addWidget(load)

		widget.setLayout(vlayout)
		widget.exec_()

	def selectFile(self,parent, lineEdit):
		dig=QFileDialog(parent)
		if dig.exec_():
			#接受选中文件的路径，默认为列表
			filenames=dig.selectedFiles()
			lineEdit.setText(filenames[0])
			#列表中的第一个元素即是文件路径，以只读的方式打开文件
			

	def loadStudent(self): #导入学生表，如果学生已经存在了，还要导入会造成数据重复，还没写这个逻辑
		courseName = self.l_courseCombox.currentText()
		className = self.l_classCombox.currentText()
		filepath = self.loadS_filepath.text()
		if courseName == '' or className == '' or filepath == '':
			QMessageBox.warning(self,'操作错误','请把信息填完整')
			return

		x, coursename_to_id = self.database.getCourseName()
		y, classname_to_id = self.database.getClassName()
		students = processData.loadStudent(filepath,self.stunumber_spinbox.value(),self.stuname_spinbox.value())

		courseid = coursename_to_id[courseName]
		classid = classname_to_id[className]

		for student in students:
			self.database.student_table.insert(student[0], student[1], classid, courseid)

		headers = ['学号','姓名']
		datas = []
		for student in self.database.student_table.find(classid = classid,course_id = courseid):
			datas.append((student[1],student[2]))
		self.showScoreTable(headers,datas,None)
		QApplication.processEvents()
		QMessageBox.information(self,'导入成功，功能关闭','!!!')

	def createClass(self):
		widget = QDialog(self)
		self.c_courseCombox = QComboBox()

		subjectlist, self.c_coursename_to_id = self.database.getCourseName()
		self.c_courseCombox.addItems(subjectlist)
		courseCombox_label = QLabel('请选择课程')

		self.class_name = QLineEdit()
		class_name_label = QLabel('请输入班级名称')
		save_pushbutton = QPushButton('保存')

		hlayout = QHBoxLayout()
		hlayout.addWidget(courseCombox_label)
		hlayout.addWidget(self.c_courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(class_name_label)
		hlayout2.addWidget(self.class_name)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout)
		vlayout.addLayout(hlayout2)
		vlayout.addWidget(save_pushbutton)

		save_pushbutton.clicked.connect(self.saveClass)
		widget.setLayout(vlayout)
		widget.exec_()

	def saveClass(self):
		courseid = self.c_coursename_to_id[self.c_courseCombox.currentText()]
		self.database.class_table.insert(self.class_name.text(),courseid)
		item = QTreeWidgetItem(self.class_Tree)
		item.setText(0,self.class_name.text())
		item.setCheckState(0, Qt.Unchecked)
		self.classItems.append(item)
		QApplication.processEvents()

		select = QMessageBox.information(self,"新建成功","是否立即导入学生？",QMessageBox.Ok|QMessageBox.Cancel)
		print(select)
		if select == QMessageBox.Ok:
			self.loadStudentData()

	def createCourse(self):
		widget = QDialog(self)
		self.courseNumber = QLineEdit(widget)
		courseNumber_label = QLabel('请输入课程编号',widget)
		self.courseName = QLineEdit(widget)
		courseName_label = QLabel('请输入课程名称',widget)
		hlayout = QHBoxLayout()
		hlayout.addWidget(courseNumber_label)
		hlayout.addWidget(self.courseNumber)

		h = QHBoxLayout()
		h.addWidget(courseName_label)
		h.addWidget(self.courseName)

		save_pushbutton = QPushButton('保存')
		save_pushbutton.clicked.connect(self.saveCourse)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout)
		vlayout.addLayout(h)
		vlayout.addWidget(save_pushbutton)

		widget.setLayout(vlayout)
		widget.show()
		widget.exec_()

	def saveCourse(self):
		self.database.course_table.insert(self.courseNumber.text(),self.courseName.text())
		item = QTreeWidgetItem(self.subjectTree)
		item.setText(0,self.courseName.text())
		item.setCheckState(0, Qt.Unchecked)
		self.subjectItems.append(item)
		QApplication.processEvents()


		select = QMessageBox.information(self,"新建成功","是否立即创建班级？",QMessageBox.Ok|QMessageBox.Cancel)
		if select == QMessageBox.Ok:
			self.createClass()

		

	def initleftwidget(self):
		label = QLabel("成绩管理",self.leftwidget)
		label.move(0,0)
		label.resize(200,80)
		label.setStyleSheet("border:2px solid red;padding:20px;color:red;width:100px;height:200px;")
		self.initLeftFunc()

	def sortTable(self):
		row = self.MyTable.currentRow()
		col = self.MyTable.currentColumn()
		print(self.MyTable.item(0,1).text())
		print(self.MyTable.currentRow())
		print(self.MyTable.currentItem())

	def modifyScore(self): #修改成绩 可以知道，在changeRow中记录为True的行必定发生了改变
		modify = defaultdict(list)
		add = defaultdict(list)
		cover_row = []

		print(self.record_colChange_inRow)
		#获取整行都被更改过的行
		for row, d in self.record_colChange_inRow.items():
			if len(d) == len(self.TABLE_HEADERS) -1:
				cover_row.append(row)
		# 获取修改的行的数据
		for row, record in self.changeRow.items():
			if record: # 行被修改
				data_record = [] 
				for i in range(len(self.TABLE_HEADERS)-1):
					new_data = self.MyTable.item(row,i).text()
					data_record.append(new_data)
				if row>=len(self.TABLE_DATA): # 增加行
					print('addData')
					add[row] = data_record
				else:                         # 修改行
					print('modify data')
					modify[row] = data_record
				
		print('modify:',modify)
		print('add:',add)

		# 检查数据是否正确, 正确数据定义为，学号为整数，名字不为空， 成绩是合法的数字：+-1.0 +-1
		# 根据self.TABLE_QUESTION_WEIGHT是否为None，可以判断此表是否是用于显示某一次成绩，如果是用于显示总成绩时不允许修改数据的。 
		data_correct = True
		del_row = []
		for row, modify_data in modify.items():
			if modify_data.count('') == len(self.TABLE_HEADERS)-1: # 没有数据代表此行是要被删除的行
				del_row.append(row)
				continue
			for col, col_data in enumerate(modify_data):
				if (col==0 and (not (processData.isInteger(col_data)))) or (col_data == '') or (2<=col<len(self.TABLE_DATA) and (not processData.isNum(col_data))):
					data_correct = False
					break
			if not data_correct:
				break

		print('modify checkout!')
		if data_correct:
			for row, add_data in add.items():
				for col, col_data in enumerate(add_data):
					if (col==0 and (not (processData.isInteger(col_data)))) or (col_data == '') or (2<=col<len(self.TABLE_DATA) and (not processData.isNum(col_data))):
						data_correct = False
						break
				if not data_correct:
					break
		print('add checkout')
		if not data_correct:
			QMessageBox.warning(self,'错误','请检查数据是否正确',QMessageBox.Ok)
			return
		else:
			select = QMessageBox.information(self,'注意','确定保存？',QMessageBox.Ok|QMessageBox.Cancel)
			if select == QMessageBox.Cancel: 
				return
			modify_result = ''
			#数据全部是正确的
				# 更改数据前提： 更改一条成绩记录，需要同时修改学生表和成绩表，先在学生表中添加记录，再在成绩表中添加记录
				# 1 学号姓名改变需要更改学生表
				# 2 成绩改变需要更改成绩表
				# 3 都改变同时更改学生表，成绩表
			# 如果是modify, 是否需要考虑用户修改的是不是学号？ 如果改变的是学号，是否会有重复？
				# modify，当用户是删除数据时，行为空，但是，是否存在，用户删除了该行后，又新加了行，或者觉得删错了，又重新输入原始的数据，该行不会被记录在删除行中，而是在另一个记录修改的集合中
			# modify 删除数据的话可以直接删除
			# modify 修改数据呢？ 是否可以认为，该行学号与原始数据不同则代表新添加，如果用户是修改了学号呢？解决方案：此种情况属于覆盖原数据，则删除掉原数据，再新增加此行
			
			# 如果modify中的行在cover_row中，而不在del_row中，则执行覆盖操作，即删除原来的数据，增加新的数据
			# 如果modify中的行同时存在于del_row和cover_row中，则执行删除操作
			# 如果都不在，则执行修改操作
			print('整行被修改：',cover_row)
			print('删除的行：', del_row)
			print(self.TABLE_DATA)
			print(self.STUDENT_ID)

			for row, modify_data in modify.items():
				if (row in cover_row) and (row not in del_row): # 覆盖操作定义为，将该名学生从该课程该班级中删除，并删除其成绩，然后根据数据，添加新的学生和新的成绩
					print('执行覆盖操作：',modify_data)  #覆盖操作包括 删除和新添加，
					#由于主外键的约束，需要将先将该学生的所有考试成绩记录删除，才可以在学生表删除该学生记录
					res = self.database.escore_table.delete(
							studentid= self.STUDENT_ID[row],
							classid=self.CLASSID,
							courseid=self.COURSEID
						)
					print('删除考试成绩操作结果：',res)
					res = self.database.student_table.delete(id=self.STUDENT_ID[row])

					# 添加新数据
					number = modify_data[0]
					name = modify_data[1]
					self.database.student_table.insert(
						number=number,
						name=name,
						classid=self.CLASSID,
						course_id = self.COURSEID
					)
					studentid = self.database.student_table.find(
							number = number,
							name = name,
							classid=self.CLASSID,
							course_id = self.COURSEID
						)[0][0]
					score = {}
					for i in range(2,len(self.TABLE_HEADERS)-1):
						score[self.TABLE_HEADERS[i]] = modify_data[i]
					self.database.escore_table.insert(
							examid = self.EXAMID,
							studentid = studentid,
							classid = self.CLASSID,
							courseid = self.COURSEID,
							score_json = json.dumps(score)
						)
					print(score)


				elif (row in cover_row) and (row in del_row): # 此处的删除操作仅仅是将该学生的成绩记录删除，并没有将其从该班级和该课程中删除
					print('执行删除操作：',modify_data)  #删除即可,注意，删除该学生成绩不应该删除该名学生？
					res = self.database.escore_table.delete(
							examid=self.EXAMID, 
							studentid= self.STUDENT_ID[row],
							classid=self.CLASSID,
							courseid=self.COURSEID
						)
					print('操作结果：',res)
				elif (row not in cover_row) and (row not in del_row):
					print('执行修改操作：',modify_data) # 修改即可

			#如果是add，需要考虑该名学生的成绩是否已经存在，如果是已经存在，却增加则会出现错误
			for row, addData in add.items():
				print('add new examScore:',addData)
		print("-"*100)

	def modifyTable(self):
		"""
		三种操作 增加、删除、修改
		"""
		if self.IS_USER_CHANGEITEM:
			print('user modify')
		if not self.IS_USER_CHANGEITEM:
			return
		self.IS_USER_CHANGEITEM = False
		#需要考虑 此处会再次引发itemChanged事件, 目前解决方案，使用 IS_USER_CHANGEITEM标记是否是用户改变表格
		row = self.MyTable.currentRow()     # 获取当前单元格所在的行
		col = self.MyTable.currentColumn()  # 获取当前单元格所在的列
		currentItem = self.MyTable.item(row,col) # 获取当前单元格
		if currentItem: #单元格对象QTableWidgetItem存在
			# 保存修改		是否需要？
			if row >= len(self.TABLE_DATA) : 
				self.addRow[row-len(self.TABLE_DATA)][col] = currentItem.text()
			else:
				self.TABLE_DATA_COPY[row][col] = currentItem.text()

			valid = False # 修改是否有效标记
			isDel = False # 当此次修改是已存在的数据时，用于判断此次操作是否是删除某一行
			
			if row >= len(self.TABLE_DATA):# 该新增行不为空,新增行 添加、修改 两种操作
				for i in range(len(self.TABLE_HEADERS)-1):
					if self.MyTable.item(row, i).text() != '': 
						valid = True
						break
			else: # 此次更改的行是已存在的行，对于已经存在的行，则分 修改、删除、覆盖 三种操作
				valid = True
				count = 0
				if col not in self.record_colChange_inRow[row]: #记录该行被修改的列,当某一行被修改的列数等于有效列数（非总成绩列）之和时，代表该行执行覆盖操作
					self.record_colChange_inRow[row].append(col)

				for i in range(len(self.TABLE_HEADERS)-1):
					if self.MyTable.item(row,i).text() == '':
						count+=1
				if count == len(self.TABLE_HEADERS)-1:
					isDel = True
				
			self.changeRow[row] = valid

			# 该行不记录, 恢复正常颜色提示
			if not valid: 
				for i in range(len(self.TABLE_HEADERS)): 
					self.MyTable.item(row,i).setText('')
					self.MyTable.item(row,i).setBackground(QBrush(QColor('#474646')))
				self.IS_USER_CHANGEITEM = True
				return

			# 该行被记录了
			if isDel: 
				# 如果是删除已存在的行，则将背景提示为删除,
				for i in range(len(self.TABLE_HEADERS)): 
					self.MyTable.item(row,len(self.TABLE_HEADERS)-1).setText('')
					self.MyTable.item(row,i).setBackground(QBrush(QColor(self.setting['table_delRow'])))
				self.IS_USER_CHANGEITEM = True
				return

			total = 0.0
			total_is_valid = False
			for col_ in range(0, len(self.TABLE_HEADERS)-1): #检查该行数据是否合法,并计算总成绩
				if 2<= col_ <len(self.TABLE_HEADERS) and self.TABLE_QUESTION_WEIGHT!=None: #修改成绩
					print('modify score')
					if not processData.isNum(self.MyTable.item(row,col_).text()):# 数据如果不正确,将单元格填充为红色
						self.MyTable.item(row,col_).setBackground(QBrush(QColor(self.setting['cell_data_error'])))
					else:														# 数据正确，计算总成绩
						total_is_valid = True
						total += Decimal(str(self.MyTable.item(row,col_).text()))*self.TABLE_QUESTION_WEIGHT[col_-2]/100
						self.MyTable.item(row,col_).setBackground(QBrush(QColor(self.setting['cell_data_modify'])))
				elif col_== 0:#修改学号
					print('modify stunumbr')
					if not (processData.isInteger(self.MyTable.item(row,0).text())):
						self.MyTable.item(row,0).setBackground(QBrush(QColor(self.setting['cell_data_error'])))
					else:
						self.MyTable.item(row,0).setBackground(QBrush(QColor(self.setting['cell_data_modify'])))
				elif col_== 1:#修改姓名
					print('modify name')
					if self.MyTable.item(row,1).text() == '':
						self.MyTable.item(row,1).setBackground(QBrush(QColor(self.setting['cell_data_error'])))
					else:
						self.MyTable.item(row,1).setBackground(QBrush(QColor(self.setting['cell_data_modify'])))
		
		self.MyTable.item(row,len(self.TABLE_HEADERS)-1).setText(str(total) if total_is_valid else '')
		self.IS_USER_CHANGEITEM = True


	def clickTableHeader(self):
		print("hahahaha")
		print(self.MyTable.currentColumn())
		horizontalHeader = self.MyTable.horizontalHeader()
		horizontalHeader.setSortIndicator(self.MyTable.currentColumn(), Qt.AscendingOrder)
		horizontalHeader.setSortIndicatorShown(True);
		self.MyTable.sortByColumn(self.MyTable.currentColumn(), Qt.AscendingOrder)

	def initmidwidget(self):
		self.stack_to_saveChange = [] #保存修改的索引，用于撤销
		# self.addRow = [None for i in range(self.setting['table_addRow'])] #
		topTooBar = QLabel(self.midwidget)
		topTooBar.move(0,0)
		topTooBar.resize(920,80)
		topTooBar.setStyleSheet("border:2px solid red;padding:20px;color:red;text-align:center;")

		addStudent = QPushButton("查看班级总成绩",self.midwidget)
		addStudent.move(10,15)
		addStudent.setStyleSheet('border-radius:6px;border:1px solid black;background:#6D6969;padding:6px;')
		addStudent.clicked.connect(self.watch_total_score)

		modify_score_button = QPushButton("更改成绩",self.midwidget)
		modify_score_button.move(10,55)
		modify_score_button.clicked.connect(self.modifyScore)

		searchLineedit = QLineEdit(self.midwidget)
		searchLineedit.setPlaceholderText('输入学号')
		searchLineedit.move(340,15)

		searchbutton = QPushButton('搜索',self.midwidget)
		searchbutton.move(550,15)
		searchbutton.clicked.connect(self.search)

		self.MyTable = QTableWidget(self.midwidget)
		self.MyTable.itemChanged.connect(self.modifyTable)
		self.MyTable.horizontalHeader().sectionClicked.connect(self.clickTableHeader)
		#self.MyTable.itemSelectionChanged.connect(self.sortTable)

		self.MyTable.move(10,90)
		#self.MyTable.setStyleSheet('text-align:center;background:{}'.format(self.setting['background-color']))
		headers = ['ID','学号','姓名','班级ID','课程ID']
		self.showScoreTable(headers,self.database.student_table.find(),None)#可删除， 无用代码

	def showScoreTable(self,headers:'表头数据 list', datas, student_id, weights=None):#显示成绩表
		if datas!=[] and len(headers)<len(datas[0]):
			headers.append('成绩')
		self.MyTable.clear()

		self.TABLE_QUESTION_WEIGHT = None  #题型所占的权重
		if weights:
			self.TABLE_QUESTION_WEIGHT = weights
		self.addRow = [["" for j in range(len(headers))] for i in range(self.setting['table_addRow'])]
		self.changeRow = {i:False for i in range(len(datas)+self.setting['table_addRow'])}
		self.record_colChange_inRow = {i:list() for i in range(len(datas))} #用于记录已存在数据改动的列
		self.IS_USER_CHANGEITEM = False
		self.TABLE_HEADERS = headers
		self.TABLE_DATA = datas
		self.STUDENT_ID = student_id
		self.TABLE_DATA_COPY = [list(d) for d in datas]#用于记录修改的成绩以及和一开始的成绩比较，查看数据是否有变动

		self.MyTable.setColumnCount(len(headers))
		self.MyTable.setRowCount(len(datas)+self.setting['table_addRow'])
		self.MyTable.setHorizontalHeaderLabels(headers)
		self.display_exam(datas)
		self.IS_USER_CHANGEITEM = True
		QApplication.processEvents()


	def display_exam(self,datas):
		for i, item in enumerate(datas):
			for j, data in enumerate(item):
				node = QTableWidgetItem(str(data))
				node.setTextAlignment(Qt.AlignCenter)
				self.MyTable.setItem(i,j,node)
				if self.TABLE_QUESTION_WEIGHT!=None and j==len(item)-1: #禁止修改总成绩
					node.setFlags(Qt.ItemIsEnabled)
		for i, item in enumerate(self.addRow):
			for j, data in enumerate(item):
				node = QTableWidgetItem(str(data))
				node.setTextAlignment(Qt.AlignCenter)
				self.MyTable.setItem(i+len(datas),j,node)
				if self.TABLE_QUESTION_WEIGHT!=None and j==len(item)-1:
					node.setFlags(Qt.ItemIsEnabled)

	def search(self):
		print('hello')

	def loadData_getExamId(self,combox):
		self.load_examid = self.examName_to_id[combox.currentText()]
		print(self.load_examid)

	def loadData_getClass(self):
		print('loadData_getClass')
		course, coursename_to_id = self.database.getCourseName()
		courseid = coursename_to_id[self.load_courseCombox.currentText()]
		self.courseid = courseid

		class_, self.className_to_id = self.database.getClassName(courseid)

		self.clearClass = True
		while self.load_classCombox.count()!=0:
			self.load_classCombox.removeItem(0)
		while self.load_examName_combox.count()!=0:
			self.load_classCombox.removeItem(0)
		self.clearClass = False

		self.load_classCombox.addItems(class_)
		QApplication.processEvents()

	def loadData_getExamName(self):
		print('loadData_getExamName')
		if self.clearClass==True:
			return
		self.classid = self.className_to_id[self.load_classCombox.currentText()]
		all_exam, self.examName_to_id = self.database.getExamName(classid = self.classid,courseid= self.courseid)
		print(all_exam, self.examName_to_id)
		self.clearExamName = True
		while self.load_examName_combox.count()!=0:
			self.load_examName_combox.removeItem(0)
		self.clearExamName = False

		self.load_examName_combox.addItems(all_exam)
		QApplication.processEvents()

	def loadData_getQuestion(self,parent):
		if self.clearExamName == True:
			return
		self.load_examid = self.examName_to_id[self.load_examName_combox.currentText()]
		exam = self.database.exam_table.find(id=self.load_examid)[0]

		self.question_name = exam[-2].split('<|>')
		self.question_weight = list(map(int,exam[-1].split('-')))

		for i, ql in enumerate(self.question_labels) :
			self.question_labels[i].setVisible(False)  #稳定吗？
			self.weights[i].setVisible(False)
			self.question_vlayout.removeWidget(self.question_labels[i])
			self.question_vlayout.removeWidget(self.weights[i])

		self.question_labels = [QLabel("学号"),QLabel("姓名")]
		self.question_labels.extend([QLabel(qname) for qname in self.question_name])

		self.weights = []
		for i in range(len(self.question_name)+2):
			spinbox = QSpinBox()
			spinbox.setRange(1,100)
			spinbox.setValue(i+1)
			self.weights.append(spinbox)

		vlayout = QVBoxLayout()
		for item in zip(self.question_labels,self.weights):
			h = QHBoxLayout()
			h.addWidget(item[0])
			h.addWidget(item[1])
			vlayout.addLayout(h)
		self.question_vlayout.insertLayout(5,vlayout)


	def loadScore(self): #导入成绩，接口函数
		cols = []
		for c in self.weights:
			cols.append(int(c.value()))

		filepath = self.loadscore_filepath.text()
		datas = processData.loadScore(filepath,cols)
		all_students = self.database.student_table.find(course_id = int(self.courseid),classid = int(self.classid))

		d_students = [(n[cols[0]-1],n[cols[1]-1]) for n in datas] #（学号， 姓名）
		s_students = [(n[1],n[2]) for n in all_students]

		#获取到excel表中的学生成绩记录和数据库中的学生成绩记录后检查，两者的学生人数是否一致，不一致的话，不在数据库中的学生需要添加到数据库，已经在数据库中的学生不在成绩表中需要将其成绩设置为0
		d_sub_s = list(set(d_students) - set(s_students))
		s_sub_d = list(set(s_students) - set(d_students))
		for student in d_sub_s:
			self.database.student_table.insert(student[0],student[1],int(self.classid),int(self.courseid))
		for student in s_sub_d:
			student = list(student)
			student.extend([0 for i in range(len(cols)-2)])
			datas.append(tuple(student))

		#更新学生表以获得id
		all_students = self.database.student_table.find(course_id = int(self.courseid),classid = int(self.classid))
		student_dict = {}
		for student in all_students:
			student_dict[student[1]] = student[0]
		scores = []

		for s_score in datas:
			score = {}
			s = 0
			for i, qname in enumerate(self.question_name):
				score[qname] = s_score[i+2] 
				s+=self.question_weight[i]*Decimal(str(s_score[i+2]))/100
			scores.append(s)

			#学生成绩如果已经存在的情况则变成修改
			print('here')
			exam_score = self.database.escore_table.find(examid = self.load_examid,studentid = int(student_dict[s_score[0]]),classid= int(self.classid),courseid = int(self.courseid))
			if exam_score!=[]:
				self.database.escore_table.update(exam_score[0][0],score_json = json.dumps(score))
			else:
				self.database.escore_table.insert(int(self.load_examid),int(student_dict[s_score[0]]),int(self.classid),int(self.courseid),json.dumps(score))
		
		#显示成绩
		examName = self.load_examName_combox.currentText()
		headers,s_datas,weight_set, student_id = self.getTableData(
					examName = examName,
					classid = self.classid,
					courseid = self.courseid,
			)
		self.showScoreTable(headers,s_datas,student_id,weight_set)
		QMessageBox.information(self,'操作结果','导入成功',QMessageBox.Ok)


	def loadData(self):  #导入学生成绩
		widget = QDialog(self)
		widget.setWindowTitle('导入到')
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')

		filepathlabel = QLabel("请输入文件路径")
		filepathbutton = QPushButton('点击选择文件')
		self.loadscore_filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget,self.loadscore_filepath))

		questiontype = QLabel('题型及导入表格中相应的列数：')

		subjectlist,x = self.database.getCourseName()
		question_list,x = self.database.getQuestionName()
		
		self.load_courseCombox = QComboBox()
		self.load_classCombox = QComboBox()
		self.load_examName_combox = QComboBox()

		self.load_courseCombox.addItems(subjectlist)

		self.load_courseCombox.currentIndexChanged.connect(self.loadData_getClass)
		self.load_classCombox.currentIndexChanged.connect(self.loadData_getExamName)	
		self.load_examName_combox.currentIndexChanged.connect(lambda:self.loadData_getQuestion(widget))

		self.question_labels = [ ]
		for question in question_list:
			question_checkbox = QLabel(question)
			self.question_labels.append(question_checkbox)

		self.weights = [] #学生信息和成绩在成绩表中的列数
		for i in range(len(question_list)):
			spinbox = QSpinBox()
			spinbox.setRange(0,100)
			spinbox.setValue(100)
			self.weights.append(spinbox)
		
		self.hlayouts = []

		for item in zip(self.question_labels,self.weights):
			h = QHBoxLayout()
			h.addWidget(item[0])
			h.addWidget(item[1])
			self.hlayouts.append(h)

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(courselabel)
		hlayout1.addWidget(self.load_courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(self.load_classCombox)

		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(examName)
		hlayout3.addWidget(self.load_examName_combox)

		hlayout4 = QHBoxLayout()
		hlayout4.addWidget(filepathlabel)
		hlayout4.addWidget(self.loadscore_filepath)
		hlayout4.addWidget(filepathbutton)

		self.question_vlayout = QVBoxLayout()
		self.question_vlayout.addLayout(hlayout1)
		self.question_vlayout.addLayout(hlayout2)
		self.question_vlayout.addLayout(hlayout3)
		self.question_vlayout.addLayout(hlayout4)


		self.question_vlayout.addWidget(questiontype)
		for hlayout in self.hlayouts:
			self.question_vlayout.addLayout(hlayout)

		save_button = QPushButton('导入成绩')
		save_button.clicked.connect(lambda:self.loadScore())

		self.question_vlayout.addWidget(save_button)
		widget.setLayout(self.question_vlayout)
		widget.exec_()

	# def showDumpData(self):  #选择需要导出的列数，暂时不需要，
	# 	widget = QDialog(self)
	# 	widget.setWindowTitle('导出成绩')
	# 	QLabel('请输入导出目录：')
	# 	self.dumpData_lineEdit = QLineEdit()
	# 	selectButton = QPushButton('点击选择')

	# 	QLabel('请选则需要导出的列数据：')

	# 	print(self.TABLE_DATA, self.TABLE_HEADERS)







	# 	widget.exec_()
	def dumpData(self):
		filepath, filetype = QFileDialog.getSaveFileName(self,
			'请选择导出的目录',
			"./dump",
			"""
			Microsoft Excel 文件(*.xlsx);;
			Microsoft Excel 97-2003 文件(*.xls)
			""")
		if filepath=='':
			return
		success, tip = processData.dumpData(filepath, self.TABLE_HEADERS,self.TABLE_DATA)
		if success:
			QMessageBox.information(self,'成功',tip,QMessageBox.Ok)
		else:
			QMessageBox.warning(self,'失败',tip,QMessageBox.Ok)

		# with open(filepath,'w+','utf-8') as f:
		# 	pass

	def createRightMenu(self):
		menu = QMenu(self)
		menu.exec_(QCursor.pos())

		new_action = QAction('新建',self)
		menu.addAction(new_action)

		delete_action = QAction('删除',self)
		menu.addAction(delete_action)

		menu.show()

	def Check(self):#设置左边查看成绩单的参数，成绩查询接口函数
		currentItem = self.tree.currentItem()
		if self.tree.currentItem() in [self.subjectTree,self.class_Tree,self.exam_Tree]:
			return
		parent = currentItem.parent()
		for i in range(parent.childCount()):
			parent.child(i).setCheckState(0,Qt.Unchecked)
		currentItem.setCheckState(0,Qt.Checked)
		if parent == self.subjectTree:
			self.COURSEID = self.database.getCourseName()[1][currentItem.text(0)]
			self.CLASSID = None
			self.EXAMID = None
			if self.r_widget!=None:
				self.r_widget.setVisible(False)
			class_, classname_to_Id = self.database.getClassName()
			while self.class_Tree.childCount()!=0:
				self.class_Tree.removeChild(self.class_Tree.child(0))
			while self.exam_Tree.childCount()!=0:
					self.exam_Tree.removeChild(self.exam_Tree.child(0))
			all_class, class_to_id = self.database.getClassName(self.COURSEID)
			for c in all_class:
				tem = QTreeWidgetItem(self.class_Tree)
				tem.setText(0, c)
				tem.setCheckState(0, Qt.Unchecked)
		elif parent == self.class_Tree:
			if self.COURSEID!=None:
				if self.r_widget!=None:
					self.r_widget.setVisible(False)
				self.CLASSID = self.database.getClassName(courseid = self.COURSEID)[1][currentItem.text(0)]
				exam, examName_to_id = self.database.getExamName(courseid = self.COURSEID, classid = self.CLASSID)
				while self.exam_Tree.childCount()!=0:
					self.exam_Tree.removeChild(self.exam_Tree.child(0))
				for e in exam:
					tem = QTreeWidgetItem(self.exam_Tree)
					tem.setText(0, e)
					tem.setCheckState(0, Qt.Unchecked)
		else:
			if self.COURSEID!=None and self.CLASSID !=None:
				self.EXAMNAME = currentItem.text(0)
				self.EXAMID = self.database.getExamName(courseid = self.COURSEID, classid = self.CLASSID)[1][currentItem.text(0)]
				
				headers,datas,weight_set,student_id = self.getTableData(
					examName = currentItem.text(0),
					classid = self.CLASSID,
					courseid = self.COURSEID,
					)
				self.QUESTION_TYPE = headers[2:]
				self.QUESTION_WEIGHT = weight_set
				self.showScoreTable(headers,datas,student_id,weight_set)
				self.setRightWidget()

	def changeweight(self,parent): #更改权重
		select = QMessageBox.information(parent,"更改题型权重",'确认更改？',QMessageBox.Ok|QMessageBox.Cancel)
		if select == QMessageBox.Cancel:
			return
		values = [str(w.value()) for w in self.r_weights]

		examweight = self.r_examweight.value()
		self.database.exam_table.update(self.EXAMID,weight_set = "-".join(values),exam_weight = examweight)
		
		#显示成绩
		headers,datas,weight_set,student_id = self.getTableData(
		examName = self.EXAMNAME,
		classid = self.CLASSID,
		courseid = self.COURSEID,
		)
		self.showScoreTable(headers,datas,student_id,weight_set)

	def setRightWidget(self):
		if self.r_widget != None:
			self.r_widget.setVisible(False)
		self.r_widget = QWidget(self.rightwidget)
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')
		questiontype = QLabel('题型及权重：')
		time_label = QLabel("考试日期：")
		examweight_label = QLabel("考试在总评中占比：")
		self.r_examweight = QSpinBox()
		self.r_examweight.setRange(0,100)

		exam = self.database.exam_table.find(id=self.EXAMID)[0]
		examName_label = QLabel(exam[1])
		examTime_label = QLabel(exam[2])
		self.r_examweight.setValue(exam[-3])

		courseName = self.database.course_table.find(id = self.COURSEID)[0][2]
		className = self.database.class_table.find(id=self.CLASSID)[0][1]
		courseName_label = QLabel(courseName)
		className_label = QLabel(className)

		self.r_question_labels = [QLabel(n+" :") for n in self.QUESTION_TYPE]
		self.r_weights = []
		for w in self.QUESTION_WEIGHT:
			spinbox = QSpinBox()
			spinbox.setRange(0,100)
			spinbox.setValue(w)
			self.r_weights.append(spinbox)
		
		hlayouts = []

		for item in zip(self.r_question_labels,self.r_weights):
			h = QHBoxLayout()
			h.addWidget(item[0])
			h.addWidget(item[1])
			hlayouts.append(h)

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(courselabel)
		hlayout1.addWidget(courseName_label)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(className_label)

		hlayout4 = QHBoxLayout()
		hlayout4.addWidget(time_label)
		hlayout4.addWidget(examTime_label)

		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(examName)
		hlayout3.addWidget(examName_label)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addLayout(hlayout2)
		vlayout.addLayout(hlayout4)
		vlayout.addLayout(hlayout3)
		
		hh = QHBoxLayout()
		hh.addWidget(examweight_label)
		hh.addWidget(self.r_examweight)

		vlayout.addLayout(hh)
		vlayout.addWidget(questiontype)

		for hlayout in hlayouts:
			vlayout.addLayout(hlayout)

		save_button = QPushButton('保存修改')
		save_button.clicked.connect(lambda:self.changeweight(self.r_widget))
		vlayout.addWidget(save_button)

		self.r_widget.setLayout(vlayout)
		self.r_widget.move(0,40)
		self.r_widget.show()



	def initLeftFunc(self):                      # 1
		self.tree = QTreeWidget(self.leftwidget)  
		self.tree.move(0,80) 
		self.tree.resize(200,520)                      # 2
		self.tree.setColumnCount(1)
		self.tree.setHeaderLabels(['成绩查询'])

		self.tree.currentItemChanged.connect(self.Check)

		self.COURSEID = None
		self.CLASSID = None
		self.EXAMID = None
		#self.tree.itemSelectionChanged.connect(self.Check)

		self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self.createRightMenu)

		self.subjectTree = QTreeWidgetItem(self.tree)               # 3
		self.subjectTree.setText(0, '课程')
		self.class_Tree = QTreeWidgetItem(self.tree)               # 3
		self.class_Tree.setText(0, '班级')
		self.exam_Tree = QTreeWidgetItem(self.tree)               # 3
		self.exam_Tree.setText(0, '考试类别')

		subjectlist, coursename_to_id = self.database.getCourseName() 
		self.subjectItems = []
		for i, c in enumerate(subjectlist):                     # 5
		    item = QTreeWidgetItem(self.subjectTree)
		    item.setText(0, c)
		    item.setCheckState(0, Qt.Unchecked)
		    self.subjectItems.append(item)
		self.classItems = []
		self.tree.expandAll() 
		self.tree.setStyleSheet('border:2px solid red;color:red;text-align:center;')  

	def watch_total_score(self):#查看所有成绩，禁止修改表格，可以修改考试所占比重
		if self.COURSEID == None or self.CLASSID == None:
			QMessageBox.warning(self,'错误操作','请先选择课程、班级',QMessageBox.Ok)
			return
		all_exam_name, examName_to_id = self.database.getExamName(courseid = self.COURSEID,classid = self.CLASSID)
		all_students = self.database.student_table.find(classid = self.CLASSID, course_id = self.COURSEID)
		all_exam_score = {}
		exam_weights = {}
		for student in all_students:
			all_score = []
			for exam in all_exam_name:
				result = {}
				exam_detail = self.database.exam_table.find(id=examName_to_id[exam])
				result['question_weights'] = exam_detail[0][-1]
				result['question_type'] = exam_detail[0][-2]
				exam_weights[exam] = exam_detail[0][-3]
				result['exam_weight'] = exam_detail[0][-3]
				score = self.database.escore_table.find(
					examid = examName_to_id[exam], 
					studentid = student[0],
					classid = self.CLASSID,
					courseid = self.COURSEID
					)
				if score != []:
					result['score_json'] = score[0][-1]
				else:
					result['score_json'] = ''
				all_score.append(result)

			all_exam_score[student] = all_score

		headers = ['学号','姓名']
		headers.extend(all_exam_name)
		datas = []
		print(all_exam_score)
		for student,exam_list in all_exam_score.items():
			scores = []
			total = 0
			for score in exam_list:
				question_weights = list(map(int, score['question_weights'].split('-')))
				question_name = score['question_type'].split('<|>')
				if score['score_json']!='':
					score_json = json.loads(score['score_json']) # 考试成绩存在的情况
				else:
					score_json = {qname:0 for qname in question_name}  # 成绩不存在的情况
				sum = 0
				for i,qname in enumerate(question_name):
					sum += Decimal(str(score_json[qname]))*question_weights[i]/100
				scores.append(sum)
				total+= sum*score['exam_weight']/100
			s_m = [student[1],student[2]]
			s_m.extend(scores)
			s_m.append(total)
			datas.append(s_m)

		self.showScoreTable(headers,datas,None)
		self.setRightWindow(all_exam_name,exam_weights)

	def setRightWindow(self,all_exam_name, exam_weights):
		print(all_exam_name,exam_weights)
		if self.r_widget != None:
			self.r_widget.setVisible(False)

		courseName = self.database.course_table.find(id=self.COURSEID)[0][-1]
		className = self.database.class_table.find(id = self.CLASSID)[0][1]
		self.r_widget = QWidget(self.rightwidget)

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(QLabel('课程:'))
		hlayout1.addWidget(QLabel(courseName))

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(QLabel('班级:'))
		hlayout2.addWidget(QLabel(className))

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addLayout(hlayout2)

		vlayout.addWidget(QLabel('考试类型及考试在总评中的比重：'))

		self.spinboxs = []

		for examName in all_exam_name:
			spinbox = QSpinBox()
			spinbox.setRange(0,100)
			spinbox.setValue(exam_weights[examName])
			self.spinboxs.append(spinbox)

			hlayout = QHBoxLayout()
			hlayout.addWidget(QLabel(examName))
			hlayout.addWidget(spinbox)
			vlayout.addLayout(hlayout)

		save_button = QPushButton('保存修改')
		save_button.clicked.connect(lambda:self.changeExam_weight(self.r_widget,all_exam_name))
		vlayout.addWidget(save_button)

		self.r_widget.setLayout(vlayout)
		self.r_widget.move(0,40)
		self.r_widget.show()

	def changeExam_weight(self,parent,all_exam_name):
		select = QMessageBox.information(parent,"更改考试权重",'确认更改？',QMessageBox.Ok|QMessageBox.Cancel)
		if select == QMessageBox.Cancel:
			return
		weights = [w.value() for w in self.spinboxs]
		x, examName_to_id = self.database.getExamName(self.COURSEID, self.CLASSID)
		for i,examName in enumerate(all_exam_name):
			self.database.exam_table.update(id = examName_to_id[examName], exam_weight=weights[i])
		self.watch_total_score()


	def closeEvent(self,event):
		print('close')
		self.database.closeDB()

	def resizeEvent(self,event):
		self.splitter.resize(self.width(),self.height()-50)
		self.MyTable.resize(900,self.height()-200)

	def keyPressEvent(self,event):
		pass
		# if event.key() == Qt.Key_Z:
		# 	print(QApplication.keyboardModifiers())
		# 	if QApplication.keyboardModifiers() == Qt.ControlModifier:
		# 		print('撤销')
		# 		if len(self.stack_to_saveChange)!=0:
		# 			row, col, data = self.stack_to_saveChange.pop(-1)
		# 			self.MyTable.item(row, col).setText(data)
		# 			if row>=len(self.TABLE_DATA):
		# 				self.addRow[row][col] = data;
		# 			else:
		# 				self.TABLE_DATA[row][col] = data;
		# 	else:
		# 		print('P')

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = studentScoreManage()
	qss = loadQSS.getStyleSheet('./style.qss')
	window.setStyleSheet(qss)
	sys.exit(app.exec())