import xlrd
import xlwt
import re
def isInteger(word):#判断是否整数，用于判断学号
	word = str(word)
	num_pattern = r'^\d+$' #
	if re.match(num_pattern, word):
		return True
	else:
		return False

def isNum(word):#判断是否是数字
	word = str(word)
	num_pattern = r'^[+-]?\d+(\.\d+)?((e|E)[+-]?\d+)?$' #
	if re.match(num_pattern, word):
		return True
	else:
		return False

def loadStudent(filepath,numbcol, namecol):
	workbook = xlrd.open_workbook(filepath)
	sheets = workbook.sheet_names()
	worksheet = workbook.sheet_by_name(sheets[0])
	data = []
	for x in range(0, worksheet.nrows):
		row = worksheet.row(x)
		data.append((str(row[numbcol-1].value).replace('.',''),row[namecol-1].value))
	return data

def loadScore(filepath,args:list):
	workbook = xlrd.open_workbook(filepath)
	sheets = workbook.sheet_names()
	worksheet = workbook.sheet_by_name(sheets[0])
	datas = []
	for x in range(0, worksheet.nrows):
		row = worksheet.row(x)
		data = []
		for i in args:
			if i==args[0]: #学号确保为整数
				data.append(str(row[int(i)-1].value).replace('.',''))
			elif i==0:
				data.append(None)
			else:
				data.append(str(row[int(i)-1].value))
		datas.append(tuple(data))
	return datas

def set_style(font_name,height,bold=False):
  style = xlwt.XFStyle() # 初始化样式
  al = xlwt.Alignment()
  al.horz = 0x02
  al.vert = 0x01
  style.alignment = al
  font = xlwt.Font()
  font.name = font_name
  font.bold = bold
  font.color_index = 4
  font.height = height*11
  style.font = font
  return style

def get_wordSize(word): #获取单词大小
	word
	size = 0
	for ch in word:
		if '\u4e00' <= ch <= '\u9fff':
			size+=2
		else:
			size+=1
	return size

def dumpData(filePath, headers, datas,sheet_name="sheet1"):
	# 创建一个workbook 设置编码
	space = 2
	size = [get_wordSize(h)+space for h in headers]
	workbook = xlwt.Workbook(encoding = 'utf-8')
	worksheet = workbook.add_sheet(sheet_name,cell_overwrite_ok = True)

	# 保存表头
	for i,header in enumerate(headers):
		worksheet.write(0,i, header ,set_style('宋体',22,True))
		worksheet.col(i).width = size[i]*256

	#保存数据
	for i,data in enumerate(datas):
		for j,cell_data in enumerate(data):
			cell_data = str(cell_data)
			if isNum(cell_data):
				worksheet.write(i+1,j, float(cell_data), set_style('宋体',18))
			else:
				worksheet.write(i+1,j, cell_data, set_style('宋体',18))
			if get_wordSize(cell_data)+space > size[j]:
				size[j] = get_wordSize(cell_data)+space

	for i,s in enumerate(size):
		worksheet.col(i).width = 256*size[i]
			

	#保存数据
	try:
		workbook.save(filePath)
		return (True, '文件保存成功')
	except PermissionError as info:
		print("文件已在其它地方打开", info)
		return (False, '文件已在其它地方打开') 
	except FileNotFoundError as info:
		print("文件不存在，可能是文件名命名出错",info)
		return (False, '文件不存在')

if __name__ == '__main__':
	print(loadScore('./score.xls',[3,4,5]))