#coding:utf-8
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui  import *
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
import json
from db import DataBase
import loadData as LD

class loadQSS:
	@staticmethod
	def getStyleSheet(file):
		with open(file,'r') as f:
			return f.read()

class studentScoreManage(QMainWindow):
	def __init__(self):
		super().__init__()
		self.initDataBase()
		self.initWindow()
		self.show()

	def initDataBase(self):
		self.database = DataBase()


	def initWindow(self):
		self.resize(1320,650)
		self.setWindowTitle('成绩管理')
		with open('./setting.json','r') as f:
			content = f.read()
		self.setting = json.loads(content)#设置
		
		self.splitter = QSplitter(self) #视图布局
		self.leftwidget = QWidget() #左视图
		self.midwidget = QWidget()  #中视图
		self.rightwidget = QWidget() #右视图


		self.splitter.resize(1320,1000)
		self.splitter.move(0,50)
		self.splitter.addWidget(self.leftwidget)
		self.splitter.addWidget(self.midwidget)
		self.splitter.addWidget(self.rightwidget)
		self.splitter.setSizes([200,920,200])

		self.initleftwidget()
		self.initmidwidget()
		self.initrightwidget()
		self.initMenu()
		
	def initrightwidget(self):
		message = QLabel('考试信息',self.rightwidget)
		message.move(100,20)

	def initMenu(self):
		self.build_menu = self.menuBar().addMenu('新建')  # 菜单栏
		self.load_menu = self.menuBar().addMenu('导入')  #
		self.help_menu = self.menuBar().addMenu('帮助')  #

		self.newExam_toolbar = self.addToolBar('newExam')
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



		self.load_action.triggered.connect(self.loadData)		# 动作事件响应
		self.dump_action.triggered.connect(self.dumpData)		#
		self.newcourse_action.triggered.connect(self.createCourse)
		self.newclass_action.triggered.connect(self.createClass)
		self.load_studentData_action.triggered.connect(self.loadStudentData)
		self.newExam_action.triggered.connect(self.createNewExam)
		self.newQuestion_action.triggered.connect(self.addQuestion)


		self.newExam_toolbar.addAction(self.newExam_action)		# 将动作添加到工具栏
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
		widget = QDialog()
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

	def setexamDate(self):
		self.examDate = str(self.examTime.date().toString("yyyy-MM-dd"))
		print(self.examDate)

	def setExamName(self):
		self.examName = self.examName_lineedit.text()
		print(self.examName)
	def addExam(self,parent): #添加一场考试
		question = []
		weight = []
		headers_data = []
		for i,checkbox in enumerate(self.checkboxs):
			if checkbox.checkState() == Qt.Checked:
				question.append(str(i+1))
				weight.append(self.weights[i].text())
				headers_data.append(checkbox.text())

		self.question_type = "-".join(question)
		self.question_weight = "-".join(weight)
		"""
		self.database.exam_table.insert(
				self.examName,
				self.examDate,
				int(self.classid),
				int(self.courseid),
				self.question_type,
				self.question_weight
			)
		"""
		headers,datas = self.getTableData(
			examName = self.examName,
			examDate = self.examDate,
			classid = self.classid,
			courseid = self.courseid,
			headers_data = headers_data
			)
		self.showScoreTable(headers,datas)
		select = QMessageBox.information(parent,'添加考试','成功添加',QMessageBox.Ok|QMessageBox.Cancel)
		if select == QMessageBox.Ok:
			print("hahahhaha")

	def getTableData(self, **args):#获取表头数据
		exam = self.database.exam_table.find(
			examName= args['examName'],
			classid=int(args['classid']),
			courseid=int(args['courseid'])
			)
		if exam!=[]:
			examid = int(exam[0][0])
			question_type = exam[0][5].split('-')
			weight_set = exam[0][-1].split('-')

		headers = ['姓名','学号']
		headers.extend(args['headers_data'])

		students = self.database.student_table.find(
			classid=int(args['classid']),
			course_id=int(args['courseid'])
			)
		datas = []
		for student in students:
			name = student[2]
			number = student[1]
			score = self.database.escore_table.find(
					examid=examid,
					studentid=int(student[0]),
					classid = int(args['classid']),
					courseid = int(args['courseid'])
				)
			if score!=[] and score[-1]!="":
				score_data = json.loads(score[0][-1])
				res = [number,name]
				mark = 0
				for i,keys in enumerate(question_type):
					res.append(score_data[keys])
					mark+=float(score_data[keys])*float(weight_set[i])/100
				res.append(str(mark))
				datas.append(res)
		return headers,datas


	def createNewExam(self):
		widget = QDialog()
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')
		self.examName_lineedit = QLineEdit()
		questiontype = QLabel('题型及权重：')
		time_label = QLabel("考试日期：")
		self.examTime = QDateTimeEdit(QDateTime.currentDateTime())
		self.examTime.setCalendarPopup(True)
		self.examTime.dateChanged.connect(self.setexamDate)
		self.examName_lineedit.textChanged.connect(self.setExamName)

		subjectlist = [item[-1] for item in self.database.course_table.find()]
		class_list = [item[1] for item in self.database.class_table.find()]
		question_list = [item[-1] for item in self.database.question_table.find()]

		courseCombox = QComboBox()
		courseCombox.addItems(subjectlist)
		courseCombox.currentIndexChanged.connect(lambda : self.setCourseId(courseCombox.currentIndex()+1))

		classCombox = QComboBox()
		classCombox.addItems(class_list)
		classCombox.currentIndexChanged.connect(lambda : self.setClassId(classCombox.currentIndex()+1))	
		
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
		hlayout1.addWidget(courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(classCombox)

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

		vlayout.addWidget(questiontype)
		for hlayout in hlayouts:
			vlayout.addLayout(hlayout)

		save_button = QPushButton('保存')
		save_button.clicked.connect(lambda:self.addExam(widget))
		vlayout.addWidget(save_button)

		widget.setLayout(vlayout)
		widget.exec_()

	def setClassId(self,id):
		self.classid = id
		print(self.classid)

	def loadStudentData(self):
		widget = QDialog()
		courselabel = QLabel('请选择课程')
		classlabel = QLabel('请选择班级')
		filepathlabel = QLabel("请输入文件路径")
		filepathbutton = QPushButton('点击选择文件')
		self.filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget))

		courseCombox = QComboBox()

		all_course = self.database.course_table.find()
		subjectlist = [item[-1] for item in all_course]
		courseCombox.addItems(subjectlist)
		courseCombox_label = QLabel('请选择课程')
		self.courseid = None
		courseCombox.currentIndexChanged.connect(lambda : self.setCourseId(courseCombox.currentIndex()+1))

		classCombox = QComboBox()
		all_class = self.database.class_table.find()
		class_list = [item[1] for item in all_class]
		classCombox.addItems(class_list)
		self.classid = None
		classCombox.currentIndexChanged.connect(lambda : self.setClassId(classCombox.currentIndex()+1))

		load = QPushButton('导入')
		load.clicked.connect(self.loadStudent)

		hlayout1 = QHBoxLayout()
		hlayout1.addWidget(courselabel)
		hlayout1.addWidget(courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(classCombox)

		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(filepathlabel)
		hlayout3.addWidget(self.filepath)
		hlayout3.addWidget(filepathbutton)

		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout1)
		vlayout.addLayout(hlayout2)
		vlayout.addLayout(hlayout3)
		vlayout.addWidget(load)

		widget.setLayout(vlayout)
		widget.exec_()

	def selectFile(self,parent):
		dig=QFileDialog(parent)
		if dig.exec_():
			#接受选中文件的路径，默认为列表
			filenames=dig.selectedFiles()
			self.FILEPATH = filenames[0]
			self.filepath.setText(self.FILEPATH)

			#列表中的第一个元素即是文件路径，以只读的方式打开文件
			

	def loadStudent(self):
		students = LD.loadStudent(self.FILEPATH)
		# for student in students:
		# 	self.database.student_table.insert(student[0],student[1],self.classid,self.courseid)
		headers = ['学号','姓名']
		datas = []
		for student in self.database.student_table.find(classid = int(self.classid),course_id = int(self.courseid)):
			datas.append((student[1],student[2]))
		self.showScoreTable(headers,datas)
		QApplication.processEvents()
		QMessageBox.information(self,'导入成功','!!!')

	def setCourseId(self,id):
		self.courseid = id
		print(self.courseid)

	def createClass(self):
		widget = QDialog()
		courseCombox = QComboBox()
		all_course = self.database.course_table.find()
		subjectlist = [item[-1] for item in all_course]
		courseCombox.addItems(subjectlist)
		courseCombox_label = QLabel('请选择课程')
		self.courseid = None
		courseCombox.currentIndexChanged.connect(lambda : self.setCourseId(courseCombox.currentIndex()+1))
		


		self.class_name = QLineEdit()
		class_name_label = QLabel('请输入班级名称')

		save_pushbutton = QPushButton('保存')

		hlayout = QHBoxLayout()
		hlayout.addWidget(courseCombox_label)
		hlayout.addWidget(courseCombox)

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
		self.database.class_table.insert(self.class_name.text(),self.courseid)

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
		widget = QDialog()
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

	def initmidwidget(self):

		topTooBar = QLabel(self.midwidget)
		topTooBar.move(0,0)
		topTooBar.resize(920,80)
		topTooBar.setStyleSheet("border:2px solid red;padding:20px;color:red;text-align:center;")

		addStudent = QPushButton("增加学生成绩",self.midwidget)
		addStudent.move(10,10)
		addStudent.setStyleSheet('border-radius:6px;border:1px solid black;background:#6D6969;padding:6px;')
		addStudent.clicked.connect(self.search)

		searchLineedit = QLineEdit(self.midwidget)
		searchLineedit.setPlaceholderText('输入学号')
		searchLineedit.move(340,10)

		searchbutton = QPushButton('搜索',self.midwidget)
		searchbutton.move(550,10)
		searchbutton.clicked.connect(self.search)

		self.MyTable = QTableWidget(self.midwidget)
		self.MyTable.move(10,90)
		self.MyTable.resize(900,340)
		self.MyTable.setStyleSheet('text-align:center;background:{}'.format(self.setting['background-color']))
		headers = ['学号','姓名','选择题','主观题','客观题','附加题','总成绩']
		self.showScoreTable(headers,self.database.student_table.find())


		bottomtoobar = QLabel(self.midwidget)
		bottomtoobar.move(0,520)
		bottomtoobar.resize(920,80)
		bottomtoobar.setStyleSheet("border:2px solid red;padding:20px;color:red;text-align:center;")
		save = QPushButton('保存修改',self.midwidget)
		save.move(450,530)

	def showScoreTable(self,headers:'表头数据 list', datas):#显示成绩表
		if len(headers)<len(datas[0]):
			headers.append('成绩')
		self.MyTable.setColumnCount(len(headers))
		self.MyTable.setRowCount(len(datas))
		self.MyTable.setHorizontalHeaderLabels(headers)
		self.display_exam(datas)
		QApplication.processEvents()


	def display_exam(self,datas):
		for i, item in enumerate(datas):
			for j, data in enumerate(item):
				self.MyTable.setItem(i,j,QTableWidgetItem(str(data)))

	def search(self):
		print('hello')

	def loadData_getExamId(self,combox):
		self.load_examid = self.examName_to_id[combox.currentText()]

	def loadData_getClass(self,courseid,combobox):
		self.courseid = courseid
		self.classData = self.database.class_table.find(course_id=courseid)
		while combobox.count()!=0:
			combobox.removeItem(0)
		class_ = [item[1] for item in self.classData]
		self.className_to_Id = {}
		for item in self.classData:
			self.className_to_Id[item[1]] = item[0]
		combobox.addItems(class_)
		QApplication.processEvents()

	def loadData_getExamName(self,classid,combox,class_combox):
		self.classid = self.className_to_Id[class_combox.currentText()]
		examData = self.database.exam_table.find(classid = self.classid,courseid= int(self.courseid))
		self.exam_weight = list(map(float,examData[0][-1].split('-')))
		print(self.exam_weight)
		while combox.count()!=0:
			combox.removeItem(0)
		examName = [item[1] for item in examData]
		self.examName_to_questionType = {}
		self.examName_to_id = {}
		print(examData,self.classid,self.courseid)
		for item in examData:
			self.examName_to_id[item[1]] = item[0]
			self.examName_to_questionType[item[1]] = item[-2]
		print(self.examName_to_id)
		combox.addItems(examName)
		QApplication.processEvents()

	def loadData_getQuestion(self,parent,this):
		self.load_examid = self.examName_to_id[this.currentText()]
		self.question_id = list(map(int,self.examName_to_questionType[self.examName_combox.currentText()].split('-')))
		self.question = []
		self.question_type_to_id = {}
		for id_ in self.question_id:
			res = self.database.question_table.find(id=id_)[0]
			self.question.append(res[-1])
			self.question_type_to_id[res[-1]] = res[0]
		for i, ql in enumerate(self.question_labels) :
			self.question_labels[i].setVisible(False)  #稳定吗？
			self.weights[i].setVisible(False)
			self.question_vlayout.removeWidget(self.question_labels[i])
			self.question_vlayout.removeWidget(self.weights[i])

		self.question_labels = [QLabel("学号"),QLabel("姓名")]
		self.question_labels.extend([QLabel(q) for q in self.question])
		self.col = []
		for i in range(len(self.question)+2):
			spinbox = QSpinBox()
			spinbox.setRange(1,100)
			spinbox.setValue(i+1)
			self.col.append(spinbox)
		vlayout = QVBoxLayout()
		for item in zip(self.question_labels,self.col):
			h = QHBoxLayout()
			h.addWidget(item[0])
			h.addWidget(item[1])
			vlayout.addLayout(h)
		self.question_vlayout.insertLayout(5,vlayout)


	def loadScore(self):
		cols = []
		for c in self.col:
			cols.append(int(c.value()))
		datas = LD.loadScore(self.FILEPATH,cols)
		all_students = self.database.student_table.find(course_id = int(self.courseid),classid = int(self.classid))

		d_students = [(n[cols[0]-1],n[cols[1]-1]) for n in datas]
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
			for i,id_ in enumerate(self.question_id):
				score[str(id_)] = s_score[i+2] 
				print(type(s_score[i+2]),s_score[i+2])
				s+=self.exam_weight[i]*float(s_score[i+2])/100
			scores.append(s)
			#还需要学生成绩如果已经存在的情况则变成修改
			exist = self.database.escore_table.find(examid = self.load_examid,studentid = int(student_dict[s_score[0]]),classid= int(self.classid),courseid = int(self.courseid))
			if exist!=[]:
				self.database.escore_table.update(exist[0][0],score_json = json.dumps(score))
			else:
				self.database.escore_table.insert(int(self.load_examid),int(student_dict[s_score[0]]),int(self.classid),int(self.courseid),json.dumps(score))
		headers = ['学号','姓名']
		headers.extend(self.question)

		s_datas = []
		for i, data in enumerate(datas):
			data = list(data)
			data.append(scores[i])
			s_datas.append(data)
		self.showScoreTable(headers,s_datas)


	def loadData(self):
		widget = QDialog()
		widget.setWindowTitle('导入到')
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')
		self.examName_combox = QComboBox()

		filepathlabel = QLabel("请输入文件路径")
		filepathbutton = QPushButton('点击选择文件')
		self.filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget))

		questiontype = QLabel('题型及导入表格中相应地列数：')


		subjectlist = [item[-1] for item in self.database.course_table.find()]
		question_list = [item[-1] for item in self.database.question_table.find()]
		classCombox = QComboBox()
		courseCombox = QComboBox()
		courseCombox.addItems(subjectlist)

		courseCombox.currentIndexChanged.connect(lambda : self.loadData_getClass(courseCombox.currentIndex()+1,classCombox))
		classCombox.currentIndexChanged.connect(lambda : self.loadData_getExamName(classCombox.currentIndex()+1,self.examName_combox,classCombox))	
		self.examName_combox.currentIndexChanged.connect(lambda:self.loadData_getQuestion(widget,self.examName_combox))

		self.question_labels = [ ]
		for question in question_list:
			question_checkbox = QLabel(question)
			self.question_labels.append(question_checkbox)

		self.weights = []
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
		hlayout1.addWidget(courseCombox)

		hlayout2 = QHBoxLayout()
		hlayout2.addWidget(classlabel)
		hlayout2.addWidget(classCombox)


		hlayout3 = QHBoxLayout()
		hlayout3.addWidget(examName)
		hlayout3.addWidget(self.examName_combox)


		hlayout4 = QHBoxLayout()
		hlayout4.addWidget(filepathlabel)
		hlayout4.addWidget(self.filepath)
		hlayout4.addWidget(filepathbutton)

		self.question_vlayout = QVBoxLayout()
		self.question_vlayout.addLayout(hlayout1)
		self.question_vlayout.addLayout(hlayout2)
		self.question_vlayout.addLayout(hlayout3)
		self.question_vlayout.addLayout(hlayout4)


		self.question_vlayout.addWidget(questiontype)
		for hlayout in self.hlayouts:
			self.question_vlayout.addLayout(hlayout)

		save_button = QPushButton('导入')
		save_button.clicked.connect(lambda:self.loadScore())

		self.question_vlayout.addWidget(save_button)
		widget.setLayout(self.question_vlayout)
		widget.exec_()

	def dumpData(self):
		dirselect = QFileDialog(self,'请选择导出的目录')
		dirselect.exec_()

	def createRightMenu(self):
		menu = QMenu(self)
		menu.exec_(QCursor.pos())

		new_action = QAction('新建',self)
		menu.addAction(new_action)

		delete_action = QAction('删除',self)
		menu.addAction(delete_action)

		menu.show()

	def initLeftFunc(self):                      # 1
		self.tree = QTreeWidget(self.leftwidget)  
		self.tree.move(0,80) 
		self.tree.resize(200,520)                      # 2
		self.tree.setColumnCount(1)
		self.tree.setHeaderLabels(['成绩查询'])
		#self.tree.itemClicked.connect(self.change_func)
		self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self.createRightMenu)

		self.subjectTree = QTreeWidgetItem(self.tree)               # 3
		self.subjectTree.setText(0, '课程')
		self.class_Tree = QTreeWidgetItem(self.tree)               # 3
		self.class_Tree.setText(0, '班级')
		self.exam_Tree = QTreeWidgetItem(self.tree)               # 3
		self.exam_Tree.setText(0, '考试类别')

		


		all_course = self.database.course_table.find()
		subjectlist = [item[-1] for item in all_course]
		self.subjectItems = []
		for i, c in enumerate(subjectlist):                     # 5
		    item = QTreeWidgetItem(self.subjectTree)
		    item.setText(0, c)
		    item.setCheckState(0, Qt.Unchecked)
		    self.subjectItems.append(item)


		
		all_class = self.database.class_table.find()
		class_list = [item[1] for item in all_class]
		self.classItems = []
		for i, c in enumerate(class_list):                     # 5
		    tem = QTreeWidgetItem(self.class_Tree)
		    tem.setText(0, c)
		    tem.setCheckState(0, Qt.Unchecked)
		    self.classItems.append(tem)

		
		all_exam = self.database.exam_table.find()
		exam_list = [item[1] for item in all_exam]
		self.examItems = []
		for i, c in enumerate(exam_list):                     # 5
		    tem = QTreeWidgetItem(self.exam_Tree)
		    tem.setText(0, c)
		    tem.setCheckState(0, Qt.Unchecked)
		    self.examItems.append(tem)

		self.tree.expandAll() 
		self.tree.setStyleSheet('border:2px solid red;color:red;text-align:center;')  
	def refreshLeftFunc(self):
		pass
	def change_func(self, item, column):
		self.label.setText(item.text(column))                   # 8
		if item == self.subjectTree:                                 # 9
		    if self.subjectTree.checkState(0) == Qt.Checked:
		        [x.setCheckState(0, Qt.Checked) for x in self.item_list]
		    else:
		        [x.setCheckState(0, Qt.Unchecked) for x in self.item_list]
		else:                                                   # 10
		    check_count = 0
		    for x in self.item_list:
		        if x.checkState(0) == Qt.Checked:
		            check_count += 1

	def closeEvent(self,event):
		print('close')
		self.database.closeDB()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = studentScoreManage()
	qss = loadQSS.getStyleSheet('./style.qss')
	window.setStyleSheet(qss)
	sys.exit(app.exec())