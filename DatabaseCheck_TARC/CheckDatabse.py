from os import listdir
import pandas as pd
import math
import pdfplumber

with open('path.txt', 'r') as filehandle:
	forms_path = filehandle.read()

no_error = True
results = {'unmatched':[], 'matched':[], 'errors':[]}
#forms_path = './forms'
section_labels = ['Headlamps', 'Handlebar', 'Throttle Condition', 'Fuel Tank', 'Prepared']
labels = ['Case_ID', 'Headlamp_Type', 'Headlamp_Bulb_Type', 'Width', 'Rise', 
'Sweep', 'Handlebar_Material', 'Handlebar_Type', 'Drum_Condition', 'Cable_Condition', 
'Throttle_Plates_Condition', 'Return_Spring_Condition', 'Fuel_Tank_Material', 'Fuel_Tank_Type', 
'Fuel_Tank_Retention', 'Tank_Deformation', 'Deformation_Source', 'Fuel_Cap_Type', 'Fuel_Cap_Retention', 
'Fuel_Spills_or_Leak', 'Fuel_Spills_Source', 'Fire_Occurred', 'M4_Comments_Description']

# Methods
def strTrim(sample):
	res = []
	for i in sample:
		if i != " ":
			res.append(i)
	return "".join(res)

def getFormId(fileName):
	return fileName[:12]

def getForms(my_path):
	return [form for form in listdir(my_path)]

def getSection(page, start, stop):
	index_s = page.find(start) + len(start)
	index_e = page.find(stop)
	return page[index_s:index_e]

def getValue(section, label, endString, special=False):
	label_len = len(label)
	index_s = section.find(label)
	if special:
		section = section[index_s+label_len:]
		index_s = 0
		label_len = 0

	index_e = section.find(endString)
	res = section[(index_s + label_len):index_e]
	return res.strip()

def extractFormData(page, section_labels, labels):
	res_dict = {}
	sections = []

	# Dividing into sections
	for i in range(len(section_labels) - 1):
		res = getSection(page, section_labels[i], section_labels[i+1])
		sections.append(res)

	res_dict[labels[0]] = strTrim(getValue(page, 'Case ID', 'H', special=True))
	# Extracting data from section 0
	l1 = getValue(sections[0], 'Headlamp Type', 'H', special=True)
	res_dict[labels[1]] = 'U' if (l1=='U' or l1=='') else int(l1)
	l2 = getValue(sections[0], 'Headlamp Bulb Type', '(1', special=True)
	res_dict[labels[2]] = l2 if (l2=='U' or l2=='') else int(l2)

	# Extracting data from section 1
	l3 = getValue(sections[1], 'A', 'mm', special=True)
	res_dict[labels[3]] = 'U' if (l3 == '-' or l3=='' or l3=='U' or l3=='NA') else int(l3)

	l4 = getValue(sections[1], 'mm C', 'mm', special=True)
	res_dict[labels[4]] = 'U' if (l4 == '-' or l4=='' or l4=='U' or l4=='NA') else int(l4)
	
	l5 = getValue(sections[1], 'mm E', 'mm', special=True)
	res_dict[labels[5]] =  'U' if (l5 == '-' or l5=='' or l5=='U' or l5=='NA') else int(l5)
	
	res_dict[labels[6]] = int(getValue(sections[1], 'Handlebar Material', '(1', special=True))
	res_dict[labels[7]] = int(getValue(sections[1], 'Handlebar Type', '(1', special=True))

	# Extracting data from section 2
	l8 = getValue(sections[2], 'Drum Condition', '(1) Function  (2) Not function properly', special=True)
	res_dict[labels[8]] = 'U' if l8 == 'U' else int(l8)
	l9 = getValue(sections[2], 'Cable Condition', '(1) Function  (2) Not function properly', special=True)
	res_dict[labels[9]] = 'U' if l9 == 'U' else int(l9)
	l10 = getValue(sections[2], 'Plates Condition', '(1) Function  (2) Not function properly', special=True)
	res_dict[labels[10]] = 'U' if l10 == 'U' else int(l10)
	l11 = getValue(sections[2], 'Return Spring Condition', '(1) Function  (2) Not function properly', special=True)
	res_dict[labels[11]] = 'U' if l11 == 'U' else int(l11)

	# Extracting data from section 3
	
	res_dict[labels[12]] = int(getValue(sections[3], 'Fuel Tank Material', '(', special=True))
	res_dict[labels[13]] = int(getValue(sections[3], 'Fuel Tank Type', '(', special=True))
	res_dict[labels[14]] = int(getValue(sections[3], 'Fuel Tank Retention', '(', special=True))
	
	res_dict[labels[15]] = int(getValue(sections[3], 'Tank Deformation', '(', special=True))

	def_source = getValue(sections[3], 'Deformation Source', '[', special=True)
	res_dict[labels[16]] = 'nan' if def_source == 'NA' else def_source
	
	res_dict[labels[17]] = int(getValue(sections[3], 'Fuel Cap Type', '(', special=True))
	res_dict[labels[18]] = int(getValue(sections[3], 'Fuel Cap Retention', '(', special=True))
	res_dict[labels[19]] = int(getValue(sections[3], 'Fuel Spills or Leak', '(', special=True))

	fuel_source = getValue(sections[3], 'Fuel Spills Source', '[', special=True)
	res_dict[labels[20]] = 'nan' if fuel_source == 'NA' else fuel_source
	
	res_dict[labels[21]] = int(getValue(sections[3], 'Fire Occurred', '(', special=True))
	comments = getValue(sections[3], 'Comments and Description', 'P', special=True)
	res_dict[labels[22]] = '-' if comments == '' else comments

	return res_dict

def extractDatabaseData(labels):
	database = pd.read_excel(r'Full database_MC_Phase1 sani M4 O4.xlsx', skiprows=3)
	database_t = database.iloc[:,177:201]  # Getting the range of data fields

	old_col_names = list(database_t.columns.values)  # Removing the unwanted columns
	old_col_names.pop(2)
	old_col_names.pop(2)
	old_col_names.insert(0, 'Case ID')
	database = database.loc[:,old_col_names]

	rename_dict = dict(zip(old_col_names, labels))
	database.rename(columns=rename_dict, inplace=True)

	database = database[database.Headlamp_Type != '(blank)']
	database = database[database.Headlamp_Type != '(no sheet)']

	return database

def adjustSources(case_d):
	case_d['Deformation_Source'] = 'nan' if type(case_d['Deformation_Source']) != str else case_d['Deformation_Source']
	case_d['Fuel_Spills_Source'] = 'nan' if type(case_d['Fuel_Spills_Source']) != str else case_d['Fuel_Spills_Source']
	return case_d

def compare(database, pdf, person):
	fields = []
	report = db_case1['Case_ID'] + '---' + str(person)
	for key in database:
		if database[key] != pdf[key]:
			fields.append(key)
	report = report + str(fields)

	if len(fields) == 0:
		results['matched'].append(report)
		print(report + '  matched')
	elif len(fields) > 0:
		results['unmatched'].append(report)
		print(report + '  unmatched')

def checkCase(database, pdf):
	if database != pdf:
		return False
	return True


def getPage(pdf, pageNum):
	error = False
	for x in [0, 1, -1]:
		page = pdf.pages[pageNum+x].extract_text()
		ind = page.find('Headlamps')
		if ind < 0:
			error = True
		else:
			error = False
			break
	if error:
		raise Exception() 
	else:
		return page


db = extractDatabaseData(labels)
forms_list = getForms(forms_path)

for form in forms_list:
	formId = getFormId(form)
	pdf = pdfplumber.open(forms_path + '/' + form)
	db_cases = db[db.Case_ID == formId]

	db_case1 = adjustSources(dict(db_cases.iloc[0]))
	try:
		page_m4 = getPage(pdf, 6)
		pd_case1 = extractFormData(page_m4, section_labels, labels)
		compare(db_case1, pd_case1, 1)
	except:
		report = formId + '---1'
		results['errors'].append(report)
		print(report + '  error')
		

	if len(db_cases) == 2: 
		db_case2 = adjustSources(dict(db_cases.iloc[1]))
		try:
			page_o4 = getPage(pdf, 12)
			pd_case2 = extractFormData(page_o4, section_labels, labels)
			compare(db_case1, pd_case1, 2)
		except:
			report = formId + '---2'
			results['errors'].append(report)
			print(report + '  error')




with open('unmatched.txt', 'w') as filehandle:
    for case in results['unmatched']:
        filehandle.write('%s\n' % case)
    filehandle.write('%s\n' % forms_path)

with open('matched.txt', 'w') as filehandle:
    for case in results['matched']:
        filehandle.write('%s\n' % case)
    filehandle.write('%s\n' % forms_path)

with open('error.txt', 'w') as filehandle:
    for case in results['errors']:
        filehandle.write('%s\n' % case)
    filehandle.write('%s\n' % forms_path)