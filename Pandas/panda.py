import pandas as pd
import numpy as np

excel_file = 'movies.xls'
movies = pd.read_excel(excel_file)

for i in range(1):
	movies1 = pd.read_excel(excel_file,sheetname = i)
	writer = pd.ExcelWriter('movies.xlsx',engine = 'xlsxwriter')
	for index,row in movies1.iterrows():
		



