#coding:utf-8
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui  import *
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog 
import json
from db import DataBase
import processData 
import time
from collections import defaultdict
from decimal import Decimal
import os
import images
#仅仅windows支持
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('myappid')
####

class loadQSS:
	@staticmethod
	def getStyleSheet(file):
		with open(file,'r') as f:
			return f.read()

class studentScoreManage(QMainWindow):
	def __init__(self):
		splash = QSplashScreen(QPixmap(":./images/start.ico"))
		splash.showMessage("加载中... ", Qt.AlignHCenter | Qt.AlignBottom, Qt.black)
		splash.show()  
		super().__init__()
		self.initDataBase()
		self.initWindow()
		self.show()
		splash.finish(self)

	def initDataBase(self):
		"""
		初始化数据库
		"""
		self.database = DataBase()

	def initWindow(self):
		"""
		初始化窗口
		"""
		window_pale = QPalette() 
		pixmap = QPixmap(":./images/2.jpg")
		window_pale.setBrush(self.backgroundRole(),QBrush(pixmap)) 
		#self.setAttribute(Qt.WA_TranslucentBackground)
		# desktop = QApplication.desktop()
		# screenRect = desktop.screenGeometry()
		# height = screenRect.height()
		# width = screenRect.width()
		# print(height, width)

		self.setPalette(window_pale)
		self.resize(1620,650)
		self.setWindowIcon(QIcon(':./images/wico.ico'))
		self.setWindowTitle('成绩管理')

		self.h_splitter = QSplitter()  # 视图布局
		self.leftview = QFrame()       # 左视图
		self.rightwidget = QWidget()   # 右视图
		self.scoreTree = QTreeWidget() # 成绩查看
		self.scoreDetail = QTreeWidget() # 查看总成绩时，用于在总成绩末尾添加各们考试的题型成绩。
		self.Table = QTableWidget()    # 成绩表

		self.scoreDetail.itemClicked.connect(self.addColumn)
		self.scoreDetail_child = []

		self.setCentralWidget(self.h_splitter) # 先添加到QMainWindow, 再初始化，不然h_splitter会覆盖掉搜索界面
		self.initSetting()
		self.initLeftView()
		self.initScoreTree()
		self.initScoreTable()
		self.initExamMessage()
		self.initMenu()
		self.initSearchWindow()

		self.setStyleSheet(loadQSS.getStyleSheet('./qss/style.qss'))

		self.h_splitter.addWidget(self.leftview)
		self.h_splitter.addWidget(self.Table)
		self.h_splitter.addWidget(self.rightwidget)
		self.h_splitter.setSizes([200,940,400])

	def initSetting(self):
		with open('./setting.json','r') as f:
			content = f.read()
		self.setting = json.loads(content)#设置

	def initExamMessage(self):
		"""
		初始化右侧考试信息窗口
		"""
		message = QLabel('考试信息',self.rightwidget)
		message.move(80,20)
		self.r_widget = None

	def initMenu(self):
		"""
		初始化主窗口菜单
		"""
		self.build_menu = self.menuBar().addMenu('新建')  # 菜单栏
		self.load_menu = self.menuBar().addMenu('导入')  #
		self.help_menu = self.menuBar().addMenu('帮助')  #

		self.new_toolbar = self.addToolBar('newExam')
		self.load_toolbar = self.addToolBar('File') # 工具栏
		self.func_toolbar = self.addToolBar('Edit')

		self.status_bar = self.statusBar() # 状态显示
		#self.status_bar.showMessage("hello word")
		self.load_action = QAction('导入成绩', self)				# 动作
		self.dump_action = QAction('导出成绩', self)				#
		self.save_action = QAction('保存修改', self)				#
		self.newExam_action = QAction('添加考试')				#
		self.newcourse_action = QAction('课程')
		self.newclass_action = QAction('班级')
		self.load_studentData_action = QAction('导入学生',self)
		self.newQuestion_action = QAction('题型',self)
		self.print_action = QAction('打印',self)
		self.find_action = QAction('查找',self)
		self.del_question = QAction('删除题型',self)
		self.about_action = QAction('关于{}'.format(self.windowTitle()))
		self.checkTotalScore_action = QAction('总成绩',self)

		self.newExam_action.setIcon(QIcon(r':./images/exam1.ico')) #设置图标
		self.load_studentData_action.setIcon(QIcon(r':./images/s.ico'))
		self.load_action.setIcon(QIcon(r':./images/loadScore2.ico'))
		self.newcourse_action.setIcon(QIcon(r':./images/blackboard.ico'))
		self.newclass_action.setIcon(QIcon(r':./images/class2.ico'))
		self.newQuestion_action.setIcon(QIcon(r':./images/question.ico'))
		self.dump_action.setIcon(QIcon(r':./images/dump.ico'))
		self.find_action.setIcon(QIcon(r':./images/search96px.ico'))
		self.print_action.setIcon(QIcon(r':./images/printer.ico'))
		self.del_question.setIcon(QIcon(r':./images/del_q.ico'))
		self.checkTotalScore_action.setIcon(QIcon(r':./images/totalScore.ico'))

		self.load_action.triggered.connect(lambda:self.loadData())		# 动作事件响应
		self.dump_action.triggered.connect(self.dumpData)		#
		self.newcourse_action.triggered.connect(self.createCourse)
		self.newclass_action.triggered.connect(lambda:self.createClass())
		self.load_studentData_action.triggered.connect(lambda:self.loadStudentData())
		self.newExam_action.triggered.connect(lambda:self.createNewExam())
		self.newQuestion_action.triggered.connect(self.createQuestion)
		self.print_action.triggered.connect(self.printScoreTable)
		self.find_action.triggered.connect(self.showSearch)
		self.del_question.triggered.connect(self.delQuestion)
		self.about_action.triggered.connect(self.showSoftwareMessage)
		self.checkTotalScore_action.triggered.connect(self.show_total_score)

		self.new_toolbar.addAction(self.newExam_action)		# 将动作添加到工具栏
		self.new_toolbar.addAction(self.newcourse_action)
		self.new_toolbar.addAction(self.newclass_action)
		self.new_toolbar.addAction(self.newQuestion_action)
		self.new_toolbar.addAction(self.del_question)

		self.load_toolbar.addAction(self.load_action)
		self.load_toolbar.addAction(self.dump_action)
		self.load_toolbar.addAction(self.load_studentData_action)
		
		#self.func_toolbar.addAction(self.print_action)
		self.func_toolbar.addAction(self.find_action)
		self.func_toolbar.addAction(self.checkTotalScore_action)
		


		self.build_menu.addAction(self.newcourse_action)			# 将动作添加到菜单栏
		self.build_menu.addAction(self.newclass_action)
		self.build_menu.addAction(self.newQuestion_action)
		self.build_menu.addSeparator()
		self.build_menu.addAction(self.del_question)

		self.load_menu.addAction(self.load_studentData_action)
		self.load_menu.addAction(self.load_action)

		self.help_menu.addAction(self.about_action)
	def showSoftwareMessage(self):
		widget = QDialog()
		widget.setWindowTitle('关于')
		w = QWidget()
		w.resize(200,2000)
		scroll_area = QScrollArea()
		scroll_area.setWidget(w)
		vlayout = QVBoxLayout()
		vlayout.addWidget(scroll_area)
		widget.setLayout(vlayout)


		widget.exec_()

	def delQuestion(self):
		self.status_bar.showMessage('删除题型')
		widget = QDialog(self)
		widget.setWindowTitle("删除题型")
		self.checkboxs_q = []
		questionName, self.questionName_to_id = self.database.getQuestionName()
		vlayout = QVBoxLayout()
		vlayout.addWidget(QLabel("请勾选需要删除的题型：      "))
		for question in questionName:
			c = QCheckBox(question)
			c.setCheckState(Qt.Unchecked)
			self.checkboxs_q.append(c)
			vlayout.addWidget(c)
		button = QPushButton('删除')
		button.clicked.connect(lambda:self.deleteQ(widget))
		vlayout.addWidget(button)
		widget.setLayout(vlayout)
		widget.exec_()
		self.status_bar.showMessage('')

	def deleteQ(self,parent):
		del_qid = [self.questionName_to_id[checkbox.text()] for checkbox in self.checkboxs_q if checkbox.checkState()==Qt.Checked]
		if del_qid == []:
			self.showMessageBox(QMessageBox.Information,'删除','请选择题型')
			return
		for qid in del_qid:
			self.database.question_table.delete(id = qid)
		parent.close()
		self.showMessageBox(QMessageBox.Information,'删除','删除成功')


	def printScoreTable(self):
		"""
		打印信号接口函数
		"""
		print('haha')
		self.printer = QPrinter(QPrinter.HighResolution)
		preview = QPrintPreviewDialog(self.printer, self)
		preview.paintRequested.connect(self.PlotPic)
		preview.resize(1000,800)
		preview.exec_()
	def PlotPic(self):
		painter = QPainter(self.printer)
		image = self.Table.grab(QRect(QPoint(0, 0),QSize(self.Table.width(),self.Table.height()) ) )  # /* 绘制窗口至画布 */
		rect = painter.viewport()
		size = image.size();
		size.scale(rect.size(), Qt.KeepAspectRatio)  # //此处保证图片显示完整
		painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
		painter.setWindow(image.rect())
		painter.drawPixmap(0, 0, image); 

	def createQuestion(self):
		"""
		添加题型窗口
		"""
		self.status_bar.showMessage('添加题型')
		widget = QDialog(self)
		widget.setWindowTitle('添加题型')
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
		self.status_bar.showMessage('')

	def saveQuestion(self,parent):
		"""
		添加题型事件
		"""
		questionName = self.descLineEdit.text().strip()#去掉前后空白字符
		if questionName == '':
			self.showMessageBox(QMessageBox.Information,'添加失败','题型名称不能为空')
			return
		res = self.database.question_table.find(questionName=questionName)
		if res!=[]:
			self.showMessageBox(QMessageBox.Information,'添加失败','该题型已存在')
			return		
		self.database.question_table.insert(questionName)
		self.showMessageBox(QMessageBox.Information,'添加题型','添加成功')

	def addExam(self,parent): 
		"""
		#添加一场考试事件
		"""
		examName = self.examName_lineedit.text().strip()
		courseName = self.createexam_courseCombox.currentText()
		className = self.createexam_classCombox.currentText()
		if courseName == '':
			self.showMessageBox(QMessageBox.Warning,'添加失败','请选择课程')
			return		
		elif className == '':
			self.showMessageBox(QMessageBox.Warning,'添加失败','请选择班级')
			return		
		elif examName == '':
			self.showMessageBox(QMessageBox.Warning,'添加失败','考试名称不能为空')
			return

		courseid = self.database.course_table.find(courseName=courseName)[0][0]
		classid = self.database.class_table.find(course_id = courseid, className=className)[0][0]
		
		examDate = str(self.examTime.date().toString("yyyy-MM-dd"))
		if self.database.exam_table.find(classid=classid, courseid = courseid,examName=examName) != []:
			self.showMessageBox(
				QMessageBox.Warning,
				'添加失败',
				'{0} {1} {2} 已存在，请更改考试名称。'.format(
						courseName,
						className,
						examName
					)
			)
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
			self.showMessageBox(QMessageBox.Warning,'添加失败','请选择题型')
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
		
		
		item = QTreeWidgetItem(self.exam_Tree)
		item.setText(0,examName)
		item.setCheckState(0, Qt.Unchecked)
		self.exam_Tree.setExpanded(True)

		self.checkCourse(courseName)
		self.checkClass(className)
		self.checkExam(examName)



		QApplication.processEvents()
		self.showMessageBox(QMessageBox.Information,'添加考试','添加成功')

	def getStudentData(self, **args): #班级确定 学号唯一

		all_students = self.database.student_table.find(classid = args['classid'], course_id = args['courseid'])
		student_id = {}
		datas = []
		headers = ['学号','姓名']
		for student in all_students:
			studentid = student[0]
			number = student[1]
			name = student[2]
			datas.append((number, name))
			student_id[number] = studentid

		if 'sort_col' not in args.keys():
			args['sort_col'] = 0
		if 'reverse' not in args.keys():
			args['reverse'] = False
		if args['sort_col'] == 0:
			datas = sorted(datas,key = lambda record:int(record[args['sort_col']]),reverse= args['reverse'])
		elif args['sort_col']==1:
			datas = sorted(datas,key = lambda record:record[args['sort_col']],reverse= args['reverse'])
		
		return headers, datas, student_id

	def get_single_score(self, **args):#获取表数据
		exam = self.database.exam_table.find(
			examName= args['examName'],
			classid=int(args['classid']),
			courseid=int(args['courseid'])
			)
		question_weights = {}
		if exam!=[]:
			examid = exam[0][0]
			question_name = exam[0][-2].split('<|>')
			weight_set = list(map(int,exam[0][-1].split('-')))
		for i, qname in enumerate(question_name):
			question_weights[qname] = weight_set[i]
		headers = ['学号','姓名']
		headers.extend(question_name)

		students = self.database.student_table.find(
			classid=int(args['classid']),
			course_id=int(args['courseid'])
			)
		datas = []
		student_id = {}
		for student in students:
			id_ = student[0]
			name = student[2]
			number = student[1]
			student_id[number] = id_
			score = self.database.escore_table.find(
					examid=examid,
					studentid=int(student[0]),
					classid = int(args['classid']),
					courseid = int(args['courseid'])
				)
			res = [number,name]
			if score!=[] and score[-1]!="":  #成绩记录存在
				score_data = json.loads(score[0][-1]) #获取成绩
				mark = 0     							#计算总成绩
				mark_isValid = False
				for i,qname in enumerate(question_name):
					if score_data[qname]!=None:   # 成绩存在的话，计算到总和
						res.append(score_data[qname])
						mark+=Decimal(str(score_data[qname]))*weight_set[i]/100
						mark_isValid = True
					else:   # 成绩不存在的话，直接在后面加''以用于显示
						res.append('')
				if mark_isValid:
					res.append(str(mark))
				else:
					res.append('')
			else: #成绩记录不存在
				res.extend(['' for i in range(len(question_name)+1)])
			datas.append(res)

		if 'sort_col' not in args.keys():
			args['sort_col'] = 0
		if 'reverse' not in args.keys():
			args['reverse'] = False

		if args['sort_col'] == 0:
			datas = sorted(datas,key = lambda record:int(record[args['sort_col']]),reverse= args['reverse'])
		elif args['sort_col']==1:
			datas = sorted(datas,key = lambda record:record[args['sort_col']],reverse= args['reverse'])
		else:
			print(datas)
			datas = sorted(datas,key = lambda record:(float(record[args['sort_col']]) if record[args['sort_col']]!='' else 0.0),reverse= args['reverse'])
		
		return headers,datas,question_weights, student_id

	def setGetClass(self,parent,combox):
		"""
		添加考试、导入成绩功能中，用户点击课程选择框后初始化班级下拉框
		"""
		#课程下拉选择框为空时，直接返回
		if parent.currentText() == '':
			return
		courseid = self.createclass_name_to_id[parent.currentText()]
		all_class, x = self.database.getClassName(courseid)
		while combox.count() != 0:
			combox.removeItem(0)
		combox.addItems(all_class)

	def createNewExam(self, courseName=None, className=None):
		"""
		添加考试窗口
		"""
		self.status_bar.showMessage('添加考试')
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
		self.createexam_classCombox = QComboBox()
		self.checkboxs = []
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

		#界面初始化完成后，再添加课程下拉选择框的内容，这样就可以触发事件初始化其它数据
		if courseName==None and className==None:
			self.createexam_courseCombox.currentIndexChanged.connect(lambda:self.setGetClass(self.createexam_courseCombox,self.createexam_classCombox))
			self.createexam_courseCombox.addItems(subjectlist)
		else:
			self.createexam_courseCombox.addItem(courseName)
			self.createexam_classCombox.addItem(className)
		widget.setLayout(vlayout)
		widget.exec_()
		self.status_bar.showMessage('')


	def sayHello(self):
		print("hello")

	def loadStudentData(self, courseName=None, className=None):
		self.status_bar.showMessage('导入学生')
		widget = QDialog(self)
		widget.setWindowTitle('导入学生')
		courselabel = QLabel('请选择课程')
		classlabel = QLabel('请选择班级')
		filepathlabel = QLabel("请输入文件路径")
		filepathbutton = QPushButton('点击选择文件')
		courseCombox_label = QLabel('请选择课程')

		self.loadS_filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget,self.loadS_filepath))
		
		subjectlist,  self.createclass_name_to_id= self.database.getCourseName()
		self.l_courseCombox = QComboBox()
		self.l_classCombox = QComboBox()
		
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
		#界面初始化完成后，再添加课程下拉框的内容
		if courseName==None and className==None:
			self.l_courseCombox.currentIndexChanged.connect(lambda : self.setGetClass(self.l_courseCombox, self.l_classCombox))
			self.l_courseCombox.addItems(subjectlist)
		else:
			self.l_courseCombox.addItem(courseName)
			self.l_classCombox.addItem(className)
		widget.exec_()
		self.status_bar.showMessage('')

	def selectFile(self,parent, lineEdit):
		dig=QFileDialog(parent)
		if dig.exec_():
			#接受选中文件的路径，默认为列表
			filenames=dig.selectedFiles()
			lineEdit.setText(filenames[0])
			#列表中的第一个元素即是文件路径，以只读的方式打开文件
	def showMessageBox(self, icon, title, content,button_text='确定', button_role = QMessageBox.YesRole):
		box = QMessageBox(icon,title, content,parent = self)
		box.addButton(button_text, button_role)
		box.exec_()	
	def showSelectBox(self,icon,title, content,yes_content, no_content):
		box = QMessageBox(QMessageBox.Question,title,content,parent = self)
		yes= box.addButton(yes_content,QMessageBox.YesRole)
		no = box.addButton(no_content,QMessageBox.NoRole)
		box.exec_()
		if box.clickedButton() == yes:
			return QMessageBox.Yes
		elif box.clickedButton() == no:
			return QMessageBox.No
		else:
			return None

	def loadStudent(self): #导入学生表，如果学生已经存在了，还要导入会造成数据重复，还没写这个逻辑
		courseName = self.l_courseCombox.currentText()
		className = self.l_classCombox.currentText()
		filepath = self.loadS_filepath.text()
		if courseName == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择课程')
			return
		elif className == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择班级')
			return
		elif filepath == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择文件')
			return
		if not os.path.isfile(filepath):
			self.showMessageBox(QMessageBox.Warning,'导入失败','文件不存在')
			return

		try:
			students = processData.loadStudent(filepath,self.stunumber_spinbox.value(),self.stuname_spinbox.value())
		except:
			self.showMessageBox(QMessageBox.Warning,'导入失败','请检查文件类型是否正确')
			return
		
		courseid = self.database.course_table.find(courseName = courseName)[0][0]
		classid = self.database.class_table.find(className = className, course_id = courseid)[0][0]

		for student in students:
			# 该学生记录如果不存在则记录到数据库
			if self.database.student_table.find(classid = classid, course_id = courseid, number = student[0]) == []:
				self.database.student_table.insert(student[0], student[1], classid, courseid)
			else:
				print('exist')

		headers, datas, student_id = self.getStudentData(courseid = courseid, classid = classid)
		self.showStudentTable(headers,datas, student_id)
		QApplication.processEvents()
		self.showMessageBox(QMessageBox.Information,'操作结果','导入成功')

	def createClass(self, specific_course=None):
		self.status_bar.showMessage('添加班级')
		widget = QDialog(self)
		widget.setWindowTitle('添加班级')
		self.c_courseCombox = QComboBox()
		if specific_course == None:
			subjectlist, x = self.database.getCourseName()
			self.c_courseCombox.addItems(subjectlist)
		else:
			self.c_courseCombox.addItem(specific_course)
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

		save_pushbutton.clicked.connect(lambda:self.saveClass(widget))
		widget.setLayout(vlayout)
		widget.exec_()
		self.status_bar.showMessage('')

	def saveClass(self,parent):
		courseName = self.c_courseCombox.currentText().strip()
		className = self.class_name.text().strip()
		if className == '':
			self.showMessageBox(QMessageBox.Warning,'添加失败','班级名不能为空')
			return
		courseid = self.database.course_table.find(courseName = courseName)[0][0]

		res = self.database.class_table.find(className=className,course_id=courseid)
		if res!=[]:
			self.showMessageBox(QMessageBox.Warning,'添加失败','该班级已存在')
			return

		self.database.class_table.insert(className,courseid)
		item = QTreeWidgetItem(self.class_Tree)
		item.setText(0,self.class_name.text())
		item.setCheckState(0, Qt.Unchecked)

		self.checkCourse(courseName)
		self.checkClass(className)

		QApplication.processEvents()
		self.class_Tree.setExpanded(True)
		select = self.showSelectBox(QMessageBox.Question,"新建成功","是否立即导入学生？",'导入','取消')
		if select ==  QMessageBox.Yes:
			parent.close()
			self.loadStudentData(courseName, className)
	def createCourse(self):
		self.status_bar.showMessage('添加课程')
		widget = QDialog(self)
		widget.setWindowTitle('添加课程')
		self.courseNumber = QLineEdit(widget)
		self.courseName = QLineEdit(widget)
		hlayout = QHBoxLayout()
		hlayout.addWidget(QLabel('请输入课程编号'))
		hlayout.addWidget(self.courseNumber)

		h = QHBoxLayout()
		h.addWidget(QLabel('请输入课程名称'))
		h.addWidget(self.courseName)

		save_pushbutton = QPushButton('保存')
		save_pushbutton.clicked.connect(lambda:self.saveCourse(widget))
		vlayout = QVBoxLayout()
		vlayout.addLayout(hlayout)
		vlayout.addLayout(h)
		vlayout.addWidget(save_pushbutton)

		widget.setLayout(vlayout)
		widget.show()
		widget.exec_()
		self.status_bar.showMessage('')
		
	def saveCourse(self,parent):
		courseNumber, courseName = self.courseNumber.text().strip(), self.courseName.text().strip()
		if courseNumber == '' or courseName == '':
			self.showMessageBox(QMessageBox.Warning,'添加失败','课程编号和课程名不能为空。')
			return
		res = self.database.course_table.find(courseName=courseName)
		if res != []:
			self.showMessageBox(QMessageBox.Information,'添加失败','课程名已存在。')
			return

		self.database.course_table.insert(courseNumber,courseName)

		# 将课程插入到成绩查询课程树下
		currentItem = QTreeWidgetItem(self.course_Tree)
		currentItem.setText(0,self.courseName.text())
		self.course_Tree.setExpanded(True)
		# 恢复颜色
		for i in range(self.course_Tree.childCount()):
			self.course_Tree.child(i).setCheckState(0,Qt.Unchecked)
			self.course_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['background'])))
		#修改颜色
		currentItem.setCheckState(0,Qt.Checked)
		currentItem.setBackground(0,QBrush(QColor(self.setting['tree']['selected_color'])))

		self.checkCourse(courseName)

		QApplication.processEvents()
		select = self.showSelectBox(QMessageBox.Information, "新建成功","是否立即创建班级？", '确定','取消')
		if select == QMessageBox.Yes:
			parent.close()
			self.createClass(courseName)

	def modifyScore(self): #修改成绩 可以知道，在changeRow中记录为True的行必定发生了改变
		if self.TABLE_CONTENT == 2:
			self.showMessageBox(QMessageBox.Warning,'更改失败','不允许修改总成绩')
			return
		self.IS_USER_CHANGEITEM = False
		modify = []
		add = []
		del_row = []
		all_row = []
		# 获取修改的行的数据
		for row, record in self.changeRow.items():
			if record: # 行被修改
				all_row.append(row)
				if row>=len(self.TABLE_DATA): # 增加行
					add.append(row)
				else:
					count = 0
					for i in range(len(self.TABLE_HEADERS)-1):
						if self.Table.item(row, i).text() == '':
							count+=1
						else:
							break
					if count == len(self.TABLE_HEADERS)-1:
						del_row.append(row)
					else:
						modify.append(row)
		
		# 检查数据是否正确, 正确数据定义为，学号为整数，名字不为空， 成绩是合法的数字：+-1.0 +-1 ,或者为空
		# 根据self.TABLE_QUESTION_WEIGHT是否为None，可以判断此表是否是用于显示某一次成绩，如果是用于显示总成绩时不允许修改数据的。 
		data_correct = True
		for row in all_row:
			if row in del_row:
				continue
			if not processData.isInteger(self.Table.item(row,0).text().strip()):
				self.Table.item(row,0).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
				data_correct = False
				break
			elif self.Table.item(row,1).text().strip() == '':
				self.Table.item(row,1).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
				data_correct = False
				break
			else:
				for i in range(2, len(self.TABLE_HEADERS)-1):
					if self.Table.item(row,i).text().strip() == '':
						continue
					if not processData.isNum(self.Table.item(row,i).text().strip()):
						self.Table.item(row,i).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
						data_correct = False
						break
				if not data_correct:
					break
		if not data_correct:
			self.IS_USER_CHANGEITEM = True	
			self.showMessageBox(QMessageBox.Warning,'更新失败','请检查数据是否正确')
			return
		elif all_row == []:
			self.IS_USER_CHANGEITEM = True
			self.showMessageBox(QMessageBox.Information,'更新结果','数据没有发生改变')
			return
		else:
			check_number_index = [i for i in range(len(self.TABLE_DATA))]
			check_number_index.extend(add)
			student_numbers = []
			for row in check_number_index:
				number = self.Table.item(row, 0).text().strip()
				if number not in student_numbers:
					student_numbers.append(number)
				else:
					items = self.Table.findItems(number, Qt.MatchExactly)#遍历表查找对应的item
					repeat_rows = list(set([item.row() for item in items]))
					for r in repeat_rows:
						self.Table.item(r,0).setBackground(QBrush(QColor(self.setting['table']['cell_data_repeat'])))
					self.IS_USER_CHANGEITEM = True
					self.showMessageBox(QMessageBox.Warning,'更改失败','学号不能重复')
					return
			# 学号不重复， 数据也是正确的
			for row in add:
				number = self.Table.item(row,0).text().strip()
				name = self.Table.item(row,1).text().strip()
				score_json = {}
				for i in range(2,len(self.TABLE_HEADERS)-1):
					if self.Table.item(row, i).text().strip()!='':
						score_json[self.TABLE_HEADERS[i]] = self.Table.item(row, i).text().strip()
					else:
						score_json[self.TABLE_HEADERS[i]] = None
				self.database.student_table.insert(number, name ,self.CLASSID, self.COURSEID)
				studentid = self.database.student_table.find(
						number = number,
						name = name, 
						classid = self.CLASSID,
						course_id = self.COURSEID
					)[0][0]
				self.database.escore_table.insert(self.EXAMID, studentid, self.CLASSID, self.COURSEID, json.dumps(score_json))
			
			for row in del_row:
				self.database.escore_table.delete(
						examid = self.EXAMID,
						studentid = self.STUDENT_ID[self.TABLE_DATA[row][0]],
						classid = self.CLASSID,
						courseid = self.COURSEID
					)
			#修改成绩
			for row in modify:
				number = self.Table.item(row,0).text().strip()
				name = self.Table.item(row,1).text().strip()
				studentid = self.STUDENT_ID[self.TABLE_DATA[row][0]]
				self.database.student_table.update(id = studentid, number = number, name=name)
				score_json = {}
				for i in range(2,len(self.TABLE_HEADERS)-1):
					if self.Table.item(row, i).text().strip() != '':
						score_json[self.TABLE_HEADERS[i]] = self.Table.item(row, i).text().strip()
					else:
						score_json[self.TABLE_HEADERS[i]] = None
				escore = self.database.escore_table.find(
						examid = self.EXAMID,
						studentid = studentid,
						classid = self.CLASSID,
						courseid = self.COURSEID
					)
				if escore!=[]: #成绩记录存在则更新
					self.database.escore_table.update(id = escore[0][0], score_json = json.dumps(score_json))
				else:  #成绩记录不存在则添加
					self.database.escore_table.insert(self.EXAMID,studentid, self.CLASSID,self.COURSEID,json.dumps(score_json))


			headers,datas,weight_set,student_id = self.get_single_score(
				examName = self.EXAMNAME,
				classid = self.CLASSID,
				courseid = self.COURSEID
			)
			self.show_single_score(headers,datas,student_id,weight_set)
			self.showMessageBox(QMessageBox.Information,'更改结果','更改成功')

		self.IS_USER_CHANGEITEM = True		
		return

	def modifyStudent(self):
		if self.TABLE_CONTENT == 2:
			self.showMessageBox(QMessageBox.Information,'更改失败','不允许修改总成绩')
			return
		modify = []
		add = []
		del_row = []
		all_row = []
		self.IS_USER_CHANGEITEM = False
		for row, isModify in self.changeRow.items():
			if isModify:
				all_row.append(row)
				if row>=len(self.TABLE_DATA):
					add.append(row)
				else:
					if self.Table.item(row,0).text()=='' and self.Table.item(row,1).text()=='':
						del_row.append(row)
					else:
						modify.append(row)
		data_correct = True
		# 检查数据是否符合定义
		for row in all_row:
			if row in del_row:
				continue
			if not processData.isInteger(self.Table.item(row,0).text().strip()):
				self.Table.item(row,0).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
				data_correct = False
				break
			elif self.Table.item(row,1).text().strip() == '':
				self.Table.item(row,1).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
				data_correct = False
				break
		if not data_correct:
			self.IS_USER_CHANGEITEM = True
			self.showMessageBox(QMessageBox.Warning,'更改失败','请检查数据是否正确')
			return
		elif modify == [] and add == [] and del_row == []:
			self.IS_USER_CHANGEITEM = True
			self.showMessageBox(QMessageBox.Information,'更改操作','数据没有发生改变')
			return
		else:
			check_number_index = [i for i in range(len(self.TABLE_DATA))]
			check_number_index.extend(add)
			student_numbers = []
			for row in check_number_index:
				number = self.Table.item(row, 0).text().strip()
				if number not in student_numbers:
					student_numbers.append(number)
				else:
					items = self.Table.findItems(number, Qt.MatchExactly)#遍历表查找对应的item
					repeat_rows = list(set([item.row() for item in items]))
					for r in repeat_rows:
						self.Table.item(r,0).setBackground(QBrush(QColor(self.setting['table']['cell_data_repeat'])))
						self.Table.item(r,1).setBackground(QBrush(QColor(self.setting['table']['cell_data_repeat'])))
					self.IS_USER_CHANGEITEM = True
					self.showMessageBox(QMessageBox.Warning,'更改失败','学号不能重复')
					return
			# 学号不是重复的,数据也是正确的 do something
			for r in add:
				number = self.Table.item(r,0).text().strip()
				name = self.Table.item(r,1).text().strip()
				self.database.student_table.insert(number,name,self.CLASSID, self.COURSEID)
			for r in modify:
				number = self.Table.item(r,0).text().strip()
				name = self.Table.item(r,1).text().strip()
				studentid = self.STUDENT_ID[self.TABLE_DATA[r][0]]
				self.database.student_table.update(id = studentid, number = number, name=name)
			
			all_exam = self.database.exam_table.find(classid = self.CLASSID, courseid = self.COURSEID)
			examids = [exam[0] for exam in all_exam]
			for r in del_row:
				studentid = self.STUDENT_ID[self.TABLE_DATA[r][0]]
				for examid in examids:
					self.database.escore_table.delete(
							examid = examid,
							courseid = self.COURSEID,
							classid = self.CLASSID,
							studentid = studentid
						)
				self.database.student_table.delete(id = studentid)
			headers, datas, studentid = self.getStudentData(classid = self.CLASSID, courseid = self.COURSEID)
			self.showStudentTable(headers, datas, studentid)
			self.IS_USER_CHANGEITEM = True
			self.showMessageBox(QMessageBox.Information,'更改结果','更改成功')

	def modifyTable(self):
		"""
		三种操作 增加、删除、修改
		"""
		if self.CLASSID == None:
			return
		if not self.IS_USER_CHANGEITEM:
			return
		self.TABLE_CHANGE = True
		self.IS_USER_CHANGEITEM = False

		#需要考虑 此处会再次引发itemChanged事件, 目前解决方案，使用 IS_USER_CHANGEITEM标记是否是用户改变表格
		row = self.Table.currentRow()     # 获取当前单元格所在的行
		col = self.Table.currentColumn()  # 获取当前单元格所在的列
		currentItem = self.Table.item(row,col) # 获取当前单元格
		
		if currentItem: #单元格对象QTableWidgetItem存在
			currentItem.setBackground(QBrush(QColor(self.setting['table']["cell_data_modify"])))
			valid = False # 修改是否有效标记
			isDel = False # 当此次修改是已存在的数据时，用于判断此次操作是否是删除某一行
			
			if row >= len(self.TABLE_DATA):# 该新增行不为空,新增行 添加、修改 两种操作
				if self.TABLE_CONTENT == 1:
					for i in range(len(self.TABLE_HEADERS)-1):
						if self.Table.item(row, i).text() != '': 
							valid = True
							break
				else:
					for i in range(len(self.TABLE_HEADERS)):
						if self.Table.item(row, i).text() != '': 
							valid = True
							break
			else: # 此次更改的行是已存在的行，对于已经存在的行，则分 修改、删除、覆盖 三种操作
				valid = True
				count = 0
				if self.TABLE_CONTENT == 1:
					for i in range(len(self.TABLE_HEADERS)-1):
						if self.Table.item(row,i).text() == '':
							count+=1
					if count == len(self.TABLE_HEADERS)-1:
						isDel = True
				else:
					for i in range(len(self.TABLE_HEADERS)):
						if self.Table.item(row,i).text() == '':
							count+=1
					if count == len(self.TABLE_HEADERS):
						isDel = True
				
			self.changeRow[row] = valid

			# 该行不记录, 恢复正常颜色提示
			if not valid: 
				for i in range(len(self.TABLE_HEADERS)): 
					self.Table.item(row,i).setText('')
					self.Table.item(row,i).setBackground(QBrush(QColor(self.setting['table']["cell_backgroundcolor"])))
				self.IS_USER_CHANGEITEM = True
				return

			# 该行被记录了
			if isDel: 
				# 如果是删除已存在的行，则将背景提示为删除,
				for i in range(len(self.TABLE_HEADERS)): 
					self.Table.item(row,i).setText('')
					self.Table.item(row,i).setBackground(QBrush(QColor(self.setting['table']['table_delRow'])))
				self.IS_USER_CHANGEITEM = True
				return

			if self.TABLE_CONTENT == 0: #处于修改学生信息状态
				print('modify sutdent message')
				if col == 0:
					if not (processData.isInteger(currentItem.text())):
						currentItem.setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
					else:
						currentItem.setBackground(QBrush(QColor(self.setting['table']['cell_data_modify'])))
				else:
					if currentItem.text() == '':
						currentItem.setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
					else:
						currentItem.setBackground(QBrush(QColor(self.setting['table']['cell_data_modify'])))

			else:# 处于修改成绩表格状态
				print('modify score')				
				if self.TABLE_CONTENT==1 and col>=2:  # 修改成绩
					total = 0.0
					total_is_valid = False
					for i in range(2,len(self.TABLE_HEADERS)-1): #计算总成绩
						if self.Table.item(row,i).text().strip() == '':
							continue
						elif not processData.isNum(self.Table.item(row,i).text().strip()):# 数据如果不正确,将单元格填充为红色
							self.Table.item(row,i).setBackground(QBrush(QColor(self.setting['table']['cell_data_error'])))
						else:														# 数据正确，计算总成绩
							total_is_valid = True
							total = Decimal(str(total)) + Decimal(str(self.Table.item(row,i).text()))*self.TABLE_QUESTION_WEIGHT[self.TABLE_HEADERS[i]]/100
					self.Table.item(row,len(self.TABLE_HEADERS)-1).setText(str(total) if total_is_valid else '')
		self.IS_USER_CHANGEITEM = True


	def clickTableHeader(self): # 目前只是简单实现了排序，假设如下：1 用户选择了课程、班级、考试  2 用户处于非查看总成绩状态
		if self.CLASSID == None:
			return
		currentColumn = self.Table.currentColumn()
		if currentColumn != self.CURRENTCOL:
			self.CURRENTCOL = currentColumn
			self.REVERSE = False
		else:
			self.REVERSE = not self.REVERSE
		horizontalHeader = self.Table.horizontalHeader()
		horizontalHeader.setSortIndicator(self.CURRENTCOL,Qt.DescendingOrder if self.REVERSE else Qt.AscendingOrder)
		horizontalHeader.setSortIndicatorShown(True);
		r = self.REVERSE
		if self.TABLE_CONTENT == 0: # 此时表格显示的是学生信息
			headers, datas, student_id = self.getStudentData(
				classid = self.CLASSID,
				courseid = self.COURSEID,
				sort_col = self.CURRENTCOL,
				reverse = self.REVERSE
				)
			self.showStudentTable(headers, datas, student_id)
		elif self.TABLE_CONTENT == 1:# 此时表格显示的是成绩信息
			headers,datas,weight_set,student_id = self.get_single_score(
				examName = self.EXAMNAME,
				classid = self.CLASSID,
				courseid = self.COURSEID,
				sort_col = self.CURRENTCOL,
				reverse = self.REVERSE
			)
			self.show_single_score(headers,datas,student_id,weight_set)
		elif self.TABLE_CONTENT == 2: # 此时表格显示的是总成绩
			headers, datas, all_exam_name, exam_weights, studentid = self.get_total_score(
			self.COURSEID,
			self.CLASSID,
			self.CURRENTCOL,
			self.REVERSE,
			self.addColumn_Dict
			)
			self.display_table(headers, datas, studentid, exam_weights)

		self.CURRENTCOL = currentColumn
		self.REVERSE = r

	def initScoreTable(self):

		horizontalHeader = self.Table.horizontalHeader()
		verticalHeader = self.Table.verticalHeader()
		verticalHeader.setDefaultSectionSize(24)
		#self.Table.setFocusPolicy(Qt.NoFocus)
		self.Table.horizontalHeader().sectionClicked.connect(self.clickTableHeader)
		self.Table.itemChanged.connect(self.modifyTable)   # 处于显示成绩状态

		self.Table.setContextMenuPolicy(Qt.CustomContextMenu)
		self.Table.customContextMenuRequested.connect(self.createRightMenu_for_table)
		
		self.Table.setColumnCount(20)
		self.Table.setRowCount(40)
		self.TABLE_HEADERS=[]
		self.TABLE_DATA = []
		self.TABLE_QUESTION_WEIGHT =None
		self.TABLE_CHANGE = False

	def show_single_score(self,headers:'表头数据 list', datas, student_id, weights=None):#显示成绩表
		self.modify_score_button.setVisible(True)
		self.modify_student_button.setVisible(False)
		self.scoreDetail.setVisible(False)
		self.TABLE_CONTENT = 1
		if self.Table.receivers(self.Table.itemClicked)>0:
			self.Table.itemClicked.disconnect(self.score_detail)
		headers.append('成绩')
		self.display_table(headers, datas, student_id, weights)
		QApplication.processEvents()

	def showStudentTable(self, headers, datas, student_id):
		self.TABLE_CONTENT = 0
		self.scoreDetail.setVisible(False)
		self.modify_score_button.setVisible(False)
		self.modify_student_button.setVisible(True)
		self.display_table(headers, datas, student_id)

	def display_table(self,headers, datas , student_id, weights=None):
		if weights:
			self.TABLE_QUESTION_WEIGHT = weights
			ItemIsEnabled = True
		else:
			self.TABLE_QUESTION_WEIGHT = None  #题型所占的权重
			ItemIsEnabled = False

		self.TABLE_CHANGE = False
		self.IS_USER_CHANGEITEM = False  # 标记是否是用户改变表格 
		self.addRow = [["" for j in range(len(headers))] for i in range(self.setting['table']['table_addRow'])] # 用于保存新增行中的数据
		self.changeRow = {i:False for i in range(len(datas)+self.setting['table']['table_addRow'])} 			# 用于记录被修改过的行
		self.record_colChange_inRow = {i:list() for i in range(len(datas))} 									# 用于记录某行被修改的列
		self.STUDENT_ID = student_id                    # 学生ID  
		self.TABLE_HEADERS = headers 					# 表头数据
		self.TABLE_DATA = datas  						# 表格原始数据
		self.TABLE_DATA_COPY = [list(d) for d in datas]	# 用于记录修改的成绩以及和一开始的成绩比较，查看数据是否有变动
		self.CURRENTCOL = 0                				# 记录当前排序的列
		self.REVERSE = False               				# 记录当前顺序
		self.Table.clear()							# 清空表格数据
		self.Table.setColumnCount(len(headers))
		self.Table.setRowCount(len(datas)+self.setting['table']['table_addRow'])
		self.Table.setHorizontalHeaderLabels(headers)

		for i, item in enumerate(datas):
			for j, data in enumerate(item):
				node = QTableWidgetItem(str(data))
				node.setTextAlignment(Qt.AlignCenter)
				self.Table.setItem(i,j,node)
				if (self.TABLE_CONTENT==1 and j==len(item)-1) or self.TABLE_CONTENT == 2: #禁止修改总成绩
					node.setFlags(Qt.ItemIsEnabled)
		for i, item in enumerate(self.addRow):
			for j, data in enumerate(item):
				node = QTableWidgetItem(str(data))
				node.setTextAlignment(Qt.AlignCenter)
				self.Table.setItem(i+len(datas),j,node)
				if (self.TABLE_CONTENT==1 and j==len(item)-1) or self.TABLE_CONTENT == 2:
					node.setFlags(Qt.ItemIsEnabled)
		self.IS_USER_CHANGEITEM = True

	def loadData_getClass(self):
		if self.load_courseCombox.currentText() == '': # 不存在任何课程
			return
		print('loadData_getClass',self.load_courseCombox.currentText())
		course, coursename_to_id = self.database.getCourseName()
		courseid = coursename_to_id[self.load_courseCombox.currentText()]
		self.courseid = courseid
		class_, self.className_to_id = self.database.getClassName(courseid)

		self.clearClass = True
		while self.load_classCombox.count()!=0:
			self.load_classCombox.removeItem(0)
		while self.load_examName_combox.count()!=0:
			self.load_examName_combox.removeItem(0)
		self.clearClass = False

		self.load_classCombox.addItems(class_)
		QApplication.processEvents()

	def loadData_getExamName(self):
		print('loadData_getExamName')
		if self.clearClass==True:
			return
		self.clearExamName = True
		while self.load_examName_combox.count()!=0:
			self.load_examName_combox.removeItem(0)
		self.clearExamName = False	
		
		if self.load_classCombox.currentText()=='':
			return

		self.classid = self.className_to_id[self.load_classCombox.currentText()]
		all_exam, self.examName_to_id = self.database.getExamName(classid = self.classid,courseid= self.courseid)

		self.load_examName_combox.addItems(all_exam)
		QApplication.processEvents()

	def loadData_getQuestion(self,parent, examid = None):
		if self.clearExamName == True or self.load_examName_combox.currentText()=='':
			return
		if examid == None:
			self.load_examid = self.examName_to_id[self.load_examName_combox.currentText()]
		else:
			self.load_examid = examid
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
			if i<2:
				spinbox.setRange(1,100)
			else:
				spinbox.setRange(0,100)
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
		courseName = self.load_courseCombox.currentText()
		className = self.load_classCombox.currentText()
		examName = self.load_examName_combox.currentText()

		# 检查课程班级考试信息是否完整
		if courseName == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择课程')
			return		
		elif className == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择班级')
			return		
		elif examName == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择考试')
			return

		# 检查文件路径是否为空，或者文件是否存在
		filepath = self.loadscore_filepath.text()
		if filepath == '':
			self.showMessageBox(QMessageBox.Warning,'导入失败','请选择文件')
			return
		elif not os.path.isfile(filepath):
			self.showMessageBox(QMessageBox.Warning,'导入失败','文件不存在')
			return

		# 判断是否能正确获取文件数据，文件类型是否正确
		cols = []
		for c in self.weights:
			cols.append(int(c.value()))

		try:
			datas = processData.loadScore(filepath,cols)
		except:
			self.showMessageBox(QMessageBox.Information,'导入失败','请检查文件类型是否正确')
			return

		# 数据都没有问题
		self.courseid = self.database.course_table.find(courseName = courseName)[0][0]
		self.classid = self.database.class_table.find(className=className, course_id = self.courseid)[0][0]
		self.load_examid = self.database.exam_table.find(examName = examName, courseid = self.courseid, classid = self.classid)[0][0]
		all_students = self.database.student_table.find(course_id = self.courseid,classid = self.classid)

		d_students = {n[cols[0]-1]:n[cols[1]-1] for n in datas} #（学号， 姓名）
		s_students = {n[1]:n[2] for n in all_students}

		# 获取到excel表中的学生成绩记录和数据库中的学生成绩记录后检查，两者的学生人数是否一致，不一致的话，不在数据库中的学生需要添加到数据库，已经在数据库中的学生不在成绩表中需要将其成绩设置为0
		# 仅以学号即可区分
		d_sub_s = list(set(d_students.keys()) - set(s_students.keys()))
		s_sub_d = list(set(s_students.keys()) - set(d_students.keys()))
		for number in d_sub_s: # 数据表减去学生表中剩下的学生即是没有被登记在学生表中的学生，需要添加到学生表中。
			self.database.student_table.insert(number, d_students[number],self.classid,self.courseid)
		# for number in s_sub_d: # 学生表减去成绩表中的学生剩下的即是没有考试成绩记录的学生，需要在末尾添加成绩。
		# 	student = [number,s_students[number]] #[学号， 姓名]
		# 	student.extend([None for i in range(len(cols)-2)]) # 各个成绩
		# 	datas.append(tuple(student))

		#更新学生id
		all_students = self.database.student_table.find(course_id = self.courseid,classid = self.classid)
		
		student_dict = {}  # 学号对应ID
		for student in all_students:
			student_dict[student[1]] = student[0]

		for s_score in datas:
			# if s_score[0] in s_sub_d: # 没有成绩记录的学生不存其成绩
			# 	break
			score = {}
			for i, qname in enumerate(self.question_name):
				score[qname] = s_score[i+2] 

			#学生成绩如果已经存在的情况则变成修改
			exam_score = self.database.escore_table.find(examid = self.load_examid,studentid = int(student_dict[s_score[0]]),classid= int(self.classid),courseid = int(self.courseid))
			if exam_score!=[]:
				self.database.escore_table.update(exam_score[0][0],score_json = json.dumps(score))
			else:
				self.database.escore_table.insert(self.load_examid,student_dict[s_score[0]],self.classid,self.courseid,json.dumps(score))

		#显示成绩
		headers,s_datas,weight_set, student_id = self.get_single_score(
					examName = examName,
					classid = self.classid,
					courseid = self.courseid,
			)
		self.show_single_score(headers,s_datas,student_id,weight_set)
		self.showMessageBox(QMessageBox.Information,'操作结果','导入成功')


	def loadData(self, courseName_=None, className_=None, examName_=None, examid = None):  #导入学生成绩
		self.status_bar.showMessage('导入成绩')
		widget = QDialog(self)
		widget.setWindowTitle('导入到')
		courselabel = QLabel('课程')
		classlabel = QLabel('班级')
		examName = QLabel('考试类型')

		filepathlabel = QLabel("文件路径")
		filepathbutton = QPushButton('点击选择文件')
		self.loadscore_filepath = QLineEdit()
		filepathbutton.clicked.connect(lambda:self.selectFile(widget,self.loadscore_filepath))

		questiontype = QLabel('题型及导入表格中相应的列数(注意：0代表不导入该列成绩)：')

		subjectlist,x = self.database.getCourseName()
		question_list,x = self.database.getQuestionName()
		
		self.load_courseCombox = QComboBox()
		self.load_classCombox = QComboBox()
		self.load_examName_combox = QComboBox()

		self.question_labels = []
		self.weights = [] #学生信息和成绩在成绩表中的列数
		self.hlayouts = []

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

		save_button = QPushButton('导入成绩')
		save_button.clicked.connect(self.loadScore)

		self.question_vlayout.addWidget(save_button)

		#界面初始化完成后，把课程添加到课程下拉框以触发事件
		if courseName_ == None and className_ == None and examName_ ==None:
			self.load_courseCombox.currentIndexChanged.connect(self.loadData_getClass)
			self.load_classCombox.currentIndexChanged.connect(self.loadData_getExamName)	
			self.load_examName_combox.currentIndexChanged.connect(lambda:self.loadData_getQuestion(widget,examid))
			self.load_courseCombox.addItems(subjectlist)
		else:
			self.clearExamName = False
			self.load_courseCombox.addItem(courseName_)
			self.load_classCombox.addItem(className_)
			self.load_examName_combox.currentIndexChanged.connect(lambda:self.loadData_getQuestion(widget,examid))
			self.load_examName_combox.addItem(examName_)

		widget.setLayout(self.question_vlayout)
		widget.exec_()
		self.status_bar.showMessage('')

	def dumpData(self):
		filepath, filetype = QFileDialog.getSaveFileName(self,
			'请选择导出的目录',
			".",
			"""
			Microsoft Excel 文件(*.xlsx);;
			Microsoft Excel 97-2003 文件(*.xls)
			""")
		if filepath=='':
			return

		success, tip = processData.dumpData(filepath, self.TABLE_HEADERS, self.TABLE_DATA, self.TABLE_QUESTION_WEIGHT)

		if success:
			self.showMessageBox(QMessageBox.Information,'成功',tip)
		else:
			self.showMessageBox(QMessageBox.Warning,'失败',tip)

	def addNew_from_tree(self, funcType): 
		"""
		funcType: {0:课程孩子节点，1:班级孩子节点，2:考试类型孩子节点，3:课程节点，4:班级节点，5:考试类型节点}
		"""
		if funcType == 0:
			print(self.COURSEID)
			courseName = self.database.course_table.find(id=self.COURSEID)[0][2]
			self.createClass(courseName)
		elif funcType == 1:
			print(self.COURSEID, self.CLASSID)
			courseName = self.database.course_table.find(id=self.COURSEID)[0][2]
			className = self.database.class_table.find(id = self.CLASSID)[0][1]
			self.createNewExam(courseName, className)

	def del_or_clear(self, funcType, isDel):
		"""
		funcType: {0:课程孩子节点，1:班级孩子节点，2:考试类型孩子节点，3:课程节点，4:班级节点，5:考试类型节点}
		"""
		currentItem = self.scoreTree.currentItem()
		if funcType == 0: # 删除课程 或者 清空课程下的班级
			select = self.showSelectBox(
				QMessageBox.Question,
				'删除' if isDel else '清空',
				'将删除该课程所有的数据，确定继续？' if isDel else '将清空该课程下的所有班级数据，确定继续？',
				'确定',
				'取消')
			if select == QMessageBox.No:
				return

			# 删除课程需要删除该课程下的班级、学生、考试、考试成绩 和该课程， 清空该课程，不需要删除该门课程即可
			self.del_one_course(self.COURSEID)

			while self.exam_Tree.childCount()!=0:
				self.exam_Tree.removeChild(self.exam_Tree.child(0))
			while self.class_Tree.childCount()!=0:
				self.class_Tree.removeChild(self.class_Tree.child(0))
			self.class_Tree.setExpanded(False)
			self.exam_Tree.setExpanded(False)

			self.CLASSID = None
			self.EXAMID = None
			self.modify_student_button.setVisible(False)
			self.display_table([],[],None,None)
			self.Table.setColumnCount(20)
			self.Table.setRowCount(40)
			self.TABLE_HEADERS=[]
			self.TABLE_DATA = []
			self.TABLE_QUESTION_WEIGHT =None
			self.TABLE_CHANGE = False
			# 删除模式下，删除该课程
			if isDel:
				self.database.course_table.delete(id = self.COURSEID)
				self.course_Tree.removeChild(currentItem)
				if self.course_Tree.childCount() == 0:
					self.course_Tree.setExpanded(False)
					self.COURSEID = None
				
			QApplication.processEvents()
			self.showMessageBox(QMessageBox.Information,'操作结果','{}成功'.format('删除' if isDel else '清空'))
		elif funcType == 1: # 删除班级 或 清空班级考试
			select = self.showSelectBox(
				QMessageBox.Question,
				'删除' if isDel else '清空',
				'将删除该班级所有的数据，确定继续？' if isDel else '将清空该班级所有考试成绩，确定继续？',
				'确定',
				'取消'
				)
			if select == QMessageBox.No:
				return
			#isDel: true: 删除班级考试和学生，false:仅仅删除班级考试
			self.del_one_class(self.COURSEID, self.CLASSID, isDel)
			
			# 先清空折叠树的所有考试节点，顺序很重要
			while self.exam_Tree.childCount()!=0:
				self.exam_Tree.removeChild(self.exam_Tree.child(0))
			self.exam_Tree.setExpanded(False)			
			self.EXAMID = None	

			#isDel: true: 删除该班级
			if isDel:
				self.database.class_table.delete(id = self.CLASSID)
				self.class_Tree.removeChild(currentItem)# 将班级从班级树中删除
				if self.class_Tree.childCount() == 0:
					self.class_Tree.setExpanded(False)
					self.CLASSID = None
					self.modify_student_button.setVisible(False)
					self.display_table([],[],None,None)
					self.Table.setColumnCount(20)
					self.Table.setRowCount(40)
					self.TABLE_HEADERS=[]
					self.TABLE_DATA = []
					self.TABLE_QUESTION_WEIGHT =None
					self.TABLE_CHANGE = False

				
			QApplication.processEvents()
			self.showMessageBox(QMessageBox.Information,'操作结果','{}成功'.format('删除' if isDel else '清空'))

		elif funcType == 2:
			print(self.COURSEID, self.CLASSID, self.EXAMID)
			select = self.showSelectBox(
				QMessageBox.Question,
				'删除' if isDel else '清空',
				'将清空该场考试所有的成绩，确定继续？' if not isDel else '将删除该场考试所有的数据，确定继续？',
				'确定',
				'取消'
				)
			if select == QMessageBox.No:
				return
			#删除考试成绩
			self.del_one_exam_score(self.EXAMID, self.COURSEID, self.CLASSID)
			headers,datas,weight_set,student_id = self.get_single_score(
				examName = self.EXAMNAME,
				classid = self.CLASSID,
				courseid = self.COURSEID,
			)
			self.show_single_score(headers,datas,student_id,weight_set)
			#删除该场考试
			if isDel:
				self.database.exam_table.delete(id = self.EXAMID)
				self.exam_Tree.removeChild(self.scoreTree.currentItem())
				if self.exam_Tree.childCount() == 0:
					self.exam_Tree.setExpanded(False)
					self.EXAMID = None
					if self.r_widget != None:
						self.r_widget.setVisible(False)
					headers, datas, studentid = self.getStudentData(courseid = self.COURSEID, classid = self.CLASSID)
					self.showStudentTable(headers, datas, studentid)

			QApplication.processEvents()
			self.showMessageBox(QMessageBox.Information,'操作结果','{}成功'.format('删除' if isDel else '清空'))
		
		elif funcType == 3:
			select = self.showSelectBox(
				QMessageBox.Question,
				'清空',
				'将清空所有课程，确定继续？',
				'确定',
				'取消'
				)
			if select == QMessageBox.No:
				return
			self.modify_student_button.setVisible(False)
			self.display_table([],[],None,None)
			self.Table.setColumnCount(20)
			self.Table.setRowCount(40)
			self.TABLE_HEADERS=[]
			self.TABLE_DATA = []
			self.TABLE_QUESTION_WEIGHT =None
			self.TABLE_CHANGE = False
			all_courses = self.database.course_table.find()
			for course in all_courses:
				self.del_one_course(course[0])
				self.database.course_table.delete(id = course[0])

			while self.exam_Tree.childCount()!=0:
				self.exam_Tree.removeChild(self.exam_Tree.child(0))
			while self.class_Tree.childCount() != 0:
				self.class_Tree.removeChild(self.class_Tree.child(0))
			while self.course_Tree.childCount()!=0:
				self.course_Tree.removeChild(self.course_Tree.child(0))
			self.exam_Tree.setExpanded(False)
			self.class_Tree.setExpanded(False)
			self.course_Tree.setExpanded(False)

			self.COURSEID = None
			self.CLASSID = None
			self.EXAMID = None

			QApplication.processEvents()
			self.showMessageBox(QMessageBox.Information,'操作结果','成功清空')

	def del_one_course(self,courseid):
		all_class = self.database.class_table.find(course_id = courseid)
		# 删除改课程下的所有班级
		for class_ in all_class:
			self.del_one_class(courseid, class_[0], True)
			self.database.class_table.delete(id = class_[0])

	def del_one_class(self, courseid, classid, isDel):
		all_exam = self.database.exam_table.find(classid = classid , courseid = courseid)
		all_examid = [exam[0] for exam in all_exam]
		#删除考试成绩
		for examid in all_examid:
			self.del_one_exam_score(examid, courseid, classid)
			self.database.exam_table.delete(id = examid)

		#删除学生
		if isDel:
			all_students = self.database.student_table.find(classid = classid, course_id = courseid)
			for student in all_students:
				self.database.student_table.delete(id = student[0])

	def del_one_exam_score(self, examid, courseid, classid):
		all_students = self.database.student_table.find(classid = classid, course_id = courseid)
		for student in all_students:
			studentid = student[0]
			self.database.escore_table.delete(
					examid = examid,
					studentid = studentid,
					classid = classid,
					courseid = courseid
				)
	def loadSignal_from_tree(self, funcType):
		courseName = self.database.course_table.find(id = self.COURSEID)[0][-1]
		className = self.database.class_table.find(id = self.CLASSID)[0][1]
		if funcType == 1:
			print('导入学生')
			self.loadStudentData(courseName, className)
		else:
			print('导入成绩')
			examName = self.database.exam_table.find(id = self.EXAMID)[0][1]
			self.loadData(courseName, className, examName, self.EXAMID)
	def createRightMenu_for_table(self):
		print("hello")
		menu = QMenu(self.Table)
		del_action = QAction('删除',self.Table)
		menu.addAction(del_action)
		menu.exec_(QCursor.pos())

	def createRightMenu_for_tree(self):
		# 考试节点----导入成绩
		currentItem = self.scoreTree.currentItem()
		parent = currentItem.parent()
		if parent == self.course_Tree:
			new_tip = '班级'
			load_tip = ''
			clear_tip = '班级'
			funcType = 0
		elif parent == self.class_Tree:
			new_tip = '考试'
			load_tip = '学生'
			clear_tip = '考试'
			funcType = 1
		elif parent == self.exam_Tree:
			new_tip = ''
			load_tip = '成绩'
			clear_tip = '成绩'
			funcType = 2
		elif currentItem == self.course_Tree:
			new_tip = ''
			load_tip = ''
			clear_tip = ''
			funcType = 3
		else:
			return

		menu = QMenu(self.scoreTree)
		new_action = QAction('新建{}'.format(new_tip),self.scoreTree)
		load_action = QAction('导入{}'.format(load_tip),self.scoreTree)
		clear_action = QAction('清空{}'.format(clear_tip),self.scoreTree)
		delete_action = QAction('删除',self.scoreTree)

		new_action.triggered.connect(lambda:self.addNew_from_tree(funcType)) # 为动作添加事件
		load_action.triggered.connect(lambda:self.loadSignal_from_tree(funcType))
		delete_action.triggered.connect(lambda:self.del_or_clear(funcType, True))
		clear_action.triggered.connect(lambda:self.del_or_clear(funcType, False))

		if new_tip != '': # 非考试节点     # 将动作添加到右键菜单
			menu.addAction(new_action)
		if load_tip != '':
			menu.addAction(load_action)
		menu.addAction(clear_action)
		if clear_tip != '':
			menu.addAction(delete_action)

		new_action.setIcon(QIcon(':./images/add1.ico'))  # 为动作添加图标
		clear_action.setIcon(QIcon(':./images/clear.ico'))
		delete_action.setIcon(QIcon(':./images/del3.ico'))
		load_action.setIcon(QIcon(':./images/{}.ico'.format('loadScore2' if load_tip=='成绩' else 's')))
		menu.exec_(QCursor.pos())

	def checkCourse(self,courseName):

		for i in range(self.course_Tree.childCount()):
				# 恢复颜色
			if self.course_Tree.child(i).text(0)!=courseName:
				self.course_Tree.child(i).setCheckState(0,Qt.Unchecked)
				self.course_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['background'])))
			else:
				#修改颜色
				self.course_Tree.child(i).setCheckState(0,Qt.Checked)
				self.course_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['selected_color'])))

		# 恢复到用户点击课程的状态
		self.modify_score_button.setVisible(False)
		self.modify_student_button.setVisible(False)
		self.COURSEID = self.database.course_table.find(courseName=courseName)[0][0]
		self.CLASSID = None
		self.EXAMID = None
		if self.r_widget!=None:
			self.r_widget.setVisible(False)
		
		# 清空班级和考试
		while self.class_Tree.childCount()!=0:
			self.class_Tree.removeChild(self.class_Tree.child(0))
		while self.exam_Tree.childCount()!=0:
				self.exam_Tree.removeChild(self.exam_Tree.child(0))
		
		# 获取该班级下的所有考试
		all_class, class_to_id = self.database.getClassName(self.COURSEID)
		for c in all_class:
			tem = QTreeWidgetItem(self.class_Tree)
			tem.setText(0, c)
			tem.setCheckState(0, Qt.Unchecked)

		self.exam_Tree.setExpanded(False)	
		if self.class_Tree.childCount()!=0:
			self.class_Tree.setExpanded(True)
		else:
			self.class_Tree.setExpanded(False)

	def checkClass(self, className):
		for i in range(self.class_Tree.childCount()):
				# 恢复颜色
			if self.class_Tree.child(i).text(0)!= className:
				self.class_Tree.child(i).setCheckState(0,Qt.Unchecked)
				self.class_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['background'])))
			else:
				#修改颜色
				self.class_Tree.child(i).setCheckState(0,Qt.Checked)
				self.class_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['selected_color'])))

		if self.COURSEID!=None:
			if self.r_widget!=None:
				self.r_widget.setVisible(False)
			self.CLASSID = self.database.class_table.find(course_id = self.COURSEID,className = className)[0][0]
			exam, examName_to_id = self.database.getExamName(courseid = self.COURSEID, classid = self.CLASSID)
			while self.exam_Tree.childCount()!=0:
				self.exam_Tree.removeChild(self.exam_Tree.child(0))
			for e in exam:
				tem = QTreeWidgetItem(self.exam_Tree)
				tem.setText(0, e)
				tem.setCheckState(0, Qt.Unchecked)
			if self.exam_Tree.childCount()!=0:
				self.exam_Tree.setExpanded(True)
			else:
				self.exam_Tree.setExpanded(False)
			headers, datas, studentid = self.getStudentData(courseid = self.COURSEID, classid = self.CLASSID)
			self.showStudentTable(headers, datas, studentid)

	def checkExam(self, examName):
		for i in range(self.exam_Tree.childCount()):
			if self.exam_Tree.child(i).text(0)!=examName:
				self.exam_Tree.child(i).setCheckState(0,Qt.Unchecked)
				self.exam_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['background'])))
			else:
				self.exam_Tree.child(i).setCheckState(0,Qt.Checked)
				self.exam_Tree.child(i).setBackground(0,QBrush(QColor(self.setting['tree']['selected_color'])))
		if self.COURSEID!=None and self.CLASSID !=None:
			self.EXAMNAME = examName
			self.EXAMID = self.database.getExamName(courseid = self.COURSEID, classid = self.CLASSID)[1][examName]
			
			headers,datas,weight_set,student_id = self.get_single_score(
				examName = examName,
				classid = self.CLASSID,
				courseid = self.COURSEID,
				)
			
			self.QUESTION_TYPE = headers[2:]
			self.QUESTION_WEIGHT = weight_set
			self.show_single_score(headers,datas,student_id,weight_set)
			self.setRightWidget()	

	def Check(self):#设置左边查看成绩单的参数，成绩查询接口函数
		currentItem = self.scoreTree.currentItem()
		if self.scoreTree.currentItem() == self.course_Tree:
			if self.course_Tree.childCount() == 0:
				self.COURSEID = None
				self.CLASSID = None
				self.EXAMID = None
			return
		elif self.scoreTree.currentItem() == self.class_Tree:
			if self.class_Tree.childCount() == 0:
				self.CLASSID = None
				self.EXAMID = None
			return
		elif self.scoreTree.currentItem() == self.exam_Tree:
			if  self.exam_Tree.childCount() == 0:
				self.EXAMID = None
			return

		parent = currentItem.parent()
		if parent == self.course_Tree:
			self.checkCourse(currentItem.text(0))	

		elif parent == self.class_Tree:
			self.checkClass(currentItem.text(0))

		else:
			self.checkExam(currentItem.text(0))

	def changeweight(self,parent): #更改权重
		select = self.showSelectBox(
			QMessageBox.Question,
			"更改题型权重",
			'确认更改？',
			'确定',
			'取消'
			)
		if select == QMessageBox.No:
			return
		values = [str(w.value()) for w in self.r_weights]

		examweight = self.r_examweight.value()
		self.database.exam_table.update(self.EXAMID,weight_set = "-".join(values),exam_weight = examweight)
		
		#显示成绩
		headers,datas,weight_set,student_id = self.get_single_score(
		examName = self.EXAMNAME,
		classid = self.CLASSID,
		courseid = self.COURSEID,
		)
		self.show_single_score(headers,datas,student_id,weight_set)

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
		for qname in self.QUESTION_TYPE:
			spinbox = QSpinBox()
			spinbox.setRange(0,100)
			spinbox.setValue(self.QUESTION_WEIGHT[qname])
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
		vlayout.addStretch(1)
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
		vlayout.addStretch(1)
		self.r_widget.setLayout(vlayout)
		self.r_widget.move(0,40)
		self.r_widget.show()

	def initLeftView(self):
		button_widget = QFrame()
		checkScore_button = QPushButton(" 总成绩 ",button_widget)
		checkScore_button.move(10,10)
		checkScore_button.setStyleSheet('border-radius:6px;border:1px solid black;background:black;padding:6px;')
		checkScore_button.clicked.connect(self.show_total_score)

		self.modify_score_button = QPushButton("更改成绩",button_widget)
		self.modify_score_button.move(100,10)
		self.modify_score_button.clicked.connect(self.modifyScore) # 
		self.modify_score_button.setVisible(False)

		self.modify_student_button = QPushButton('更改学生',button_widget)
		self.modify_student_button.move(100, 10)
		self.modify_student_button.clicked.connect(self.modifyStudent)
		self.modify_student_button.setVisible(False)

		self.scoreDetail.setColumnCount(1)
		self.scoreDetail.setHeaderLabels(['考试详情'])
		self.scoreDetail.setVisible(False)

		button_widget.setMinimumHeight(45)
		vlayout = QVBoxLayout()
		vlayout.addWidget(button_widget)
		vlayout.addWidget(self.scoreTree)
		vlayout.addWidget(self.scoreDetail)
		vlayout.setContentsMargins(0,0,0,00)
		self.leftview.setLayout(vlayout)

	def initScoreTree(self):    
                  
		self.scoreTree.setColumnCount(1)
		self.scoreTree.setHeaderLabels(['成绩查询'])

		self.scoreTree.currentItemChanged.connect(self.Check)

		self.COURSEID = None
		self.CLASSID = None
		self.EXAMID = None

		self.scoreTree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.scoreTree.customContextMenuRequested.connect(self.createRightMenu_for_tree)

		self.course_Tree = QTreeWidgetItem(self.scoreTree)               # 3
		self.course_Tree.setText(0, '课程')
		self.class_Tree = QTreeWidgetItem(self.scoreTree)               # 3
		self.class_Tree.setText(0, '班级')
		self.exam_Tree = QTreeWidgetItem(self.scoreTree)               # 3
		self.exam_Tree.setText(0, '考试类别')

		self.course_Tree.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
		self.class_Tree.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
		self.exam_Tree.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)

		subjectlist, coursename_to_id = self.database.getCourseName() 
		for i, c in enumerate(subjectlist):                     # 5
		    item = QTreeWidgetItem(self.course_Tree)
		    item.setText(0, c)
		    item.setCheckState(0, Qt.Unchecked)

		if self.course_Tree.childCount()!=0:
			self.course_Tree.setExpanded(True)
		else:
			self.course_Tree.setExpanded(False)


	def score_detail(self):
		row = self.Table.currentRow()
		col = self.Table.currentColumn()
		if col<2 or col>= self.initial_length:
			return
		self.status_bar.showMessage('成绩详情')
		widget = QDialog(self)
		widget.setWindowTitle('成绩详情')
		studentid = self.STUDENT_ID[self.Table.item(row,0).text().strip()]
		exam = self.database.exam_table.find(classid = self.CLASSID, courseid = self.COURSEID,examName=self.TABLE_HEADERS[col])[0]
		question_type = exam[-2].split('<|>')
		question_weights = exam[-1].split('-')
		examid = exam[0]
		score = self.database.escore_table.find(studentid = studentid, examid = examid, classid = self.CLASSID, courseid = self.COURSEID)

		vlayout = QVBoxLayout()
		if score!=[]:
			score_json = json.loads(score[0][-1])
			for i,qname in enumerate(question_type):
				h = QHBoxLayout()
				h.addWidget(QLabel(qname+'({}%): '.format(question_weights[i])))
				h.addStretch(0.5)
				h.addWidget(QLabel("" if score_json[qname]==None else score_json[qname]))
				vlayout.addLayout(h)
		else:
			for i,qname in enumerate(question_type):
				h = QHBoxLayout()
				h.addWidget(QLabel(qname+'({}%): '.format(question_weights[i])))
				h.addWidget(QLabel(""))
				vlayout.addLayout(h)
		widget.setMinimumWidth(225)
		widget.move(QCursor.pos())
		widget.setLayout(vlayout)
		widget.exec_()
		self.status_bar.showMessage('')


		
	def show_total_score(self):
		if self.COURSEID == None or self.CLASSID == None:
			self.showMessageBox(QMessageBox.Warning,'查看失败','请选择课程、班级')
			return
		self.scoreDetail.setVisible(True)
		if self.Table.receivers(self.Table.itemClicked)==0:
			self.Table.itemClicked.connect(self.score_detail)

		headers, datas, all_exam_name, exam_weights, studentid = self.get_total_score(
			self.COURSEID,
			self.CLASSID,
			self.CURRENTCOL,
			self.REVERSE
		)

		self.scoreDetail.clear()
		self.scoreDetail_child.clear()
		self.addColumn_Dict = {}

		self.TABLE_CONTENT = 2
		self.initial_length = 2+len(all_exam_name)
		self.modify_student_button.setVisible(False)
		self.modify_score_button.setVisible(False)
		self.display_table(headers, datas, studentid, exam_weights)
		self.showExamMessage(all_exam_name,exam_weights)
		QApplication.processEvents()
	
	def get_total_score(self, courseid, classid ,sort_col= 0, reverse = False, addColumn_Dict = None):#查看所有成绩，禁止修改表格，可以修改考试所占比重
		all_exam_name, examName_to_id = self.database.getExamName(courseid = courseid, classid = classid)
		all_students = self.database.student_table.find(classid = classid, course_id = courseid)
		all_exam_score = {}
		exam_weights = {}
		student_id = {}
		if all_students == []: # 学生为空也要初始化考试信息
			for exam in all_exam_name:
				exam_detail = self.database.exam_table.find(id=examName_to_id[exam]) # 获取该场考试详情
				exam_weights[exam] = exam_detail[0][-3]   			# 考试比重 用于显示成绩信息
		else:
			for student in all_students: #对于该班级所有的学生
				student_id[student[1]] = student[0]
				all_score = []
				examScore = {}
				for exam in all_exam_name: # 每个学生的每场考试成绩
					result = {}
					exam_detail = self.database.exam_table.find(id=examName_to_id[exam]) # 获取该场考试详情
					result['question_weights'] = exam_detail[0][-1]		# 考试题型比重
					result['question_type'] = exam_detail[0][-2]		# 考试题型名称
					result['exam_weight'] = exam_detail[0][-3]          # 考试比重 用于计算成绩
					exam_weights[exam] = exam_detail[0][-3]   			# 考试比重 用于显示成绩信息
					score = self.database.escore_table.find(
						examid = examName_to_id[exam], 
						studentid = student[0],
						classid = classid,
						courseid = courseid
						)
					if score != []: # 学生成绩存在
						result['score_json'] = score[0][-1]
						examScore[exam] = score[0][-1]
					else:			# 学生成绩不存在
						result['score_json'] = None
						examScore[exam] = None
					all_score.append(result)
				all_score.append(examScore)
				all_exam_score[student] = all_score
		headers = ['学号','姓名']
		headers.extend(all_exam_name)
		headers.append('总成绩')
		if addColumn_Dict != None:
			addheader = []
			for examName in all_exam_name:
				if addColumn_Dict[examName] != []:
					for qname in addColumn_Dict[examName]:
						addheader.append(examName+'.'+qname)
			headers.extend(addheader)
		datas = []
		# 计算学生考试总成绩
		for student,exam_list in all_exam_score.items():
			scores = []
			total = 0
			for i,exam in enumerate(exam_list): #计算一场考试的成绩
				if i == len(exam_list) -1:
					continue
				question_weights = list(map(int, exam['question_weights'].split('-')))
				question_name = exam['question_type'].split('<|>')
				if exam['score_json'] != None:
					score_json = json.loads(exam['score_json']) # 考试成绩存在的情况
					sum = 0.0
					for i,qname in enumerate(question_name):
						if score_json[qname]!=None:
							sum = Decimal(str(sum)) + Decimal(str(score_json[qname]))*question_weights[i]/100
				else: #学生成绩不存在
					sum = 0.0
				scores.append(sum)
				total = Decimal(str(total)) +  Decimal(str(sum*exam['exam_weight']/100))
			s_m = [student[1],student[2]]
			s_m.extend(scores)
			s_m.append(total)

			examScoreDetail = exam_list[-1]
			if addColumn_Dict != None:
				addscore = []
				for examName in all_exam_name:
					if examScoreDetail[examName] != None:
						score_json = json.loads(examScoreDetail[examName])
					else:
						score_json = None
					if addColumn_Dict[examName]!=[]:
						for qname in addColumn_Dict[examName]:
							addscore.append((score_json[qname] if score_json[qname] != None else '' ) if score_json!=None else '')
				s_m.extend(addscore)

			datas.append(s_m)
		print(datas,sort_col)
		if sort_col == 0:
			datas = sorted(datas,key = lambda record:int(record[0]), reverse= reverse)
		elif sort_col == 1:
			datas = sorted(datas, key = lambda record:record[1], reverse = reverse)
		else:
			datas = sorted(datas, key = lambda record:float(record[sort_col]) if record[sort_col]!='' else 0.0,reverse = reverse)
		return headers, datas, all_exam_name,exam_weights,student_id

	def showExamMessage(self,all_exam_name, exam_weights):
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

		for examName in all_exam_name:
			self.addColumn_Dict[examName] = []
			item = QTreeWidgetItem(self.scoreDetail)
			item.setText(0, examName)
			item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
			exam = self.database.exam_table.find(classid = self.CLASSID, courseid = self.COURSEID, examName = examName)
			question = exam[0][-2].split('<|>')
			for qname in question:
				item_child = QTreeWidgetItem(item)
				item_child.setText(0, qname)
				item_child.setCheckState(0,Qt.Unchecked)
			self.scoreDetail_child.append(item)

		self.r_widget.show()

	def addColumn(self):
		currentItem = self.scoreDetail.currentItem()
		parent = currentItem.parent()
		if currentItem in self.scoreDetail_child:
			return
		currentItem.setCheckState(0,Qt.Checked if currentItem.checkState(0)== Qt.Unchecked else Qt.Unchecked)
		currentItem.setBackground(0,QBrush(QColor(self.setting['tree']['selected_color'] if currentItem.checkState(0)== Qt.Checked else self.setting['tree']['background'])))
		if currentItem.text(0) not in self.addColumn_Dict[parent.text(0)]:
			self.addColumn_Dict[parent.text(0)].append(currentItem.text(0))
			print(self.addColumn_Dict)
		if currentItem.checkState(0) == Qt.Unchecked and (currentItem.text(0) in self.addColumn_Dict[parent.text(0)]):
			del self.addColumn_Dict[parent.text(0)][self.addColumn_Dict[parent.text(0)].index(currentItem.text(0))]
		headers, datas, all_exam_name, exam_weights, studentid = self.get_total_score(
			self.COURSEID,
			self.CLASSID,
			self.CURRENTCOL,
			self.REVERSE,
			self.addColumn_Dict
		)
		self.display_table(headers, datas, studentid, exam_weights)


	def changeExam_weight(self,parent,all_exam_name):
		select = self.showSelectBox(
			QMessageBox.Question,
			"更改考试权重",
			'确认更改？',
			'确定',
			'取消'
			)
		if select == QMessageBox.No:
			return
		weights = [w.value() for w in self.spinboxs]
		x, examName_to_id = self.database.getExamName(self.COURSEID, self.CLASSID)
		for i,examName in enumerate(all_exam_name):
			self.database.exam_table.update(id = examName_to_id[examName], exam_weight=weights[i])
		headers, datas, all_exam_name, exam_weights, studentid = self.get_total_score(
			self.COURSEID,
			self.CLASSID,
			self.CURRENTCOL,
			self.REVERSE,
			self.addColumn_Dict
		)
		self.display_table(headers, datas, studentid, exam_weights)

	def searchPre(self):
		if self.showAll == True:
			for row in self.search_rows:
				self.setColumnColor(row,self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色
			self.showAll = False
		if self.res_is_null:
			self.showMessageBox(QMessageBox,Information,'搜索结果','内容没找到！')
			return
		if self.scrollIndex<=0:
			self.showMessageBox(QMessageBox.Information,'搜索结果','已到达第一个搜索结果')
			return
		else:
			self.setColumnColor(self.search_rows[self.scrollIndex],self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色
			self.scrollIndex -= 1                                         #获取其行号
			self.setColumnColor(self.search_rows[self.scrollIndex],self.setting['table']['search_select_color'])
			self.Table.verticalScrollBar().setSliderPosition(self.search_rows[self.scrollIndex]-2)  #滚轮定位过去
	
	def setColumnColor(self, row, backgroundcolor=''):
		temp = self.IS_USER_CHANGEITEM
		self.IS_USER_CHANGEITEM = False
		for i in range(len(self.TABLE_HEADERS)):
			self.Table.item(row,i).setBackground(QBrush(QColor(backgroundcolor)))
		self.IS_USER_CHANGEITEM = temp

	def total_search_Res(self):
		self.showAll = True
		for row in self.search_rows:
			self.setColumnColor(row,self.setting['table']['search_select_color'])#恢复表格正常的颜色

	def search(self):
		if self.showAll == True:
			for row in self.search_rows:
				self.setColumnColor(row,self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色
			self.showAll = False

		if self.search_rows==[]:
			self.showMessageBox(QMessageBox.Information,'搜索结果','内容没找到！')
			return  
		elif self.scrollIndex == len(self.search_rows)-1:
			self.showMessageBox(QMessageBox.Information,'搜索结果','已到达最后一个搜索结果')
			return 

		if self.scrollIndex!= -1:	
			self.setColumnColor(self.search_rows[self.scrollIndex],self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色
		
		self.scrollIndex+=1
		self.setColumnColor(self.search_rows[self.scrollIndex],self.setting['table']['search_select_color'])
		self.Table.verticalScrollBar().setSliderPosition(self.search_rows[self.scrollIndex]-2)  #滚轮定位过去

	def showSearch(self):
		self.searchFrame.setVisible(True)
		self.search_lineEdit.setText('')
		self.search_lineEdit.setFocus(True)

	def hideSearch(self):
		self.searchFrame.setVisible(False)
		for row in self.search_rows:
			self.setColumnColor(row,self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色

	def findRes(self):
		search_content = self.search_lineEdit.text().strip()
		items = self.Table.findItems(search_content, Qt.MatchExactly)#遍历表查找对应的item
		if self.search_rows!=[]:
			for row in self.search_rows:
				self.setColumnColor(row,self.setting['table']["cell_backgroundcolor"])#恢复表格正常的颜色
		self.search_rows = list(set([item.row() for item in items]))
		self.search_rows.sort()

		if self.search_rows!=[]:
			self.res_is_null = False
			self.scrollIndex = -1
			self.showAll = False
		else:
			self.res_is_null = True
			self.showAll = False

	def initSearchWindow(self):
		self.res_is_null = True
		self.scrollIndex = None
		self.search_rows = []
		self.searchFrame = QFrame(self)
		self.searchFrame.resize(self.width(), self.setting['search']["height"])
		self.searchFrame.move(0, self.height()-self.setting['search']["height"])
		self.searchFrame.setStyleSheet('background:#edcd9e;border:2px red solid;')
		self.search_lineEdit = QLineEdit(self.searchFrame)
		self.search_lineEdit.setPlaceholderText('请输入搜索内容')
		self.search_lineEdit.setStyleSheet('background:white;')
		self.search_lineEdit.editingFinished.connect(self.findRes)
		self.search_lineEdit.setMinimumHeight(self.setting['search']["height"]-20)
		self.search_lineEdit.setAlignment(Qt.AlignCenter)
		self.search_lineEdit.setFont(QFont('宋体',12))
		quit_button = QPushButton("退出")
		quit_button.setStyleSheet('background:black;')
		quit_button.clicked.connect(self.hideSearch)

		searchbutton = QPushButton('搜索')
		searchbutton.setStyleSheet('background:black;')
		searchbutton.clicked.connect(self.search)

		findPrev = QPushButton('上一个')
		findPrev.setStyleSheet('background:black;')
		findPrev.clicked.connect(self.searchPre)

		findNext = QPushButton('全部')
		findNext.setStyleSheet('background:black;')
		findNext.clicked.connect(self.total_search_Res)


		hlayout = QHBoxLayout()
		hlayout.addWidget(QLabel('               '))
		hlayout.addWidget(self.search_lineEdit)
		hlayout.addWidget(searchbutton)
		hlayout.addWidget(findPrev)
		hlayout.addWidget(findNext)
		hlayout.addWidget(quit_button)
		hlayout.addWidget(QLabel('               '))
		
		self.searchFrame.setLayout(hlayout)
		self.searchFrame.show()
		self.searchFrame.setVisible(False)

	def closeEvent(self,event):
		
		if self.TABLE_CHANGE:
			select = self.showSelectBox(
				QMessageBox.Question,
				'关闭',
				'数据改动尚未保存,是否退出？',
				'确定',
				'取消'
				)
			if select == QMessageBox.No:
				event.ignore()
				return
		print('close')
		self.database.closeDB()

	def resizeEvent(self,event):
		self.searchFrame.resize(self.width(), self.setting['search']["height"])
		self.searchFrame.move(0, self.height()-self.setting["search"]["height"])

	def keyPressEvent(self,event):
		"""
		键盘事件，设置快捷键
		"""
		if QApplication.keyboardModifiers() == Qt.ControlModifier:
			if event.key() == Qt.Key_F:
				self.showSearch()
			if event.key() == Qt.Key_S:
				if self.TABLE_CONTENT == 0:
					self.modifyStudent()
				elif self.TABLE_CONTENT == 1:
					self.modifyScore()
		elif event.key() == Qt.Key_Escape:
			self.hideSearch()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = studentScoreManage()
	sys.exit(app.exec())