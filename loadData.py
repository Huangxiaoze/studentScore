import xlrd

def loadStudent(filepath):
	workbook = xlrd.open_workbook(filepath)
	sheets = workbook.sheet_names()
	worksheet = workbook.sheet_by_name(sheets[0])
	data = []
	for x in range(0, worksheet.nrows):
		row = worksheet.row(x)
		data.append((str(row[0].value).replace('.',''),row[1].value))
	return data

def loadScore(filepath,args:list):
	workbook = xlrd.open_workbook(filepath)
	sheets = workbook.sheet_names()
	worksheet = workbook.sheet_by_name(sheets[0])
	datas = []
	for x in range(0, worksheet.nrows):
		row = worksheet.row(x)
		data = [str(row[0].value).replace('.',''),row[1].value]
		for i in args:
			data.append(str(row[int(i)-1].value))
		datas.append(tuple(data))
	return datas
if __name__ == '__main__':
	print(loadScore('./score.xls',[3,4,5]))