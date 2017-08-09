def multicolumn_element(e, columns):
	return '\\multicolumn{' + str(columns) + '}{c|} {' + e + '}'
      
def multicolumn_element_left_border(e, columns):
	return '\\multicolumn{' + str(columns) + '}{|c} {' + e + '}'
      
def multicolumn_element_both_borders(e, columns):
	return '\\multicolumn{' + str(columns) + '}{|c|} {' + e + '}'

def non_centered_multicolumn_element(e, columns):
	return '\\multicolumn{' + str(columns) + '}{|l|} {' + e + '}'
      
def multirow_element(e, rows):
	return '\\multirow{' + str(rows) + '}{*} {' + e + '}'

def bold_element(e):
	return '\\textbf{' + e + '}'
      
def cell_color(color):
	return '\\cellcolor{' + color + '}'

def write_script_size(f):
	f.write('\\scriptsize \n')

# A latex tabular line is written in the file accessed by the file object f.
# The elements of the line are given in a list of strings.
def write_line(f, elements):
	for i in range(len(elements)):
		f.write(str(elements[i]) + ' ')
		if i < len(elements) - 1 :
			f.write('& ')
		else:
			f.write('\\\\ \n')

def write_hline(f):
	f.write('\hline \n')

def write_cline(f,left,right):
	f.write('\cline{' + str(left) + '-' + str(right) + '}')

def write_begin_table(f):
	f.write('\\begin{table} \n')
	
def write_begin_table_with_ht(f):
	f.write('\\begin{table}[ht!] \n')
	
def write_end_table(f):
	f.write('\\end{table} \n')

def write_begin_adjustbox(f):
	f.write('\\begin{adjustbox}{center} \n')

def write_end_adjustbox(f):
	f.write('\\end{adjustbox} \n')

# The tabular specifies the number of columns.
def write_begin_non_bordered_tabular(f, columns):
	f.write('\\begin{tabular}')
	col_param = '{|'
	for c in range(columns):
		col_param += 'c'
	col_param += '|}'
	f.write(col_param + '\n')

# The tabular specifies the number of columns.
def write_begin_tabular(f, columns):
	f.write('\\begin{tabular}')
	col_param = '{|'
	for c in range(columns):
		col_param += 'c|'
	col_param += '}'
	f.write(col_param + '\n')
	
def write_end_tabular(f):
	f.write('\\end{tabular} \n')
	
def write_caption(f, caption):
	f.write('\\caption{' + caption + '} \n')
	
def write_label(f, label):
	f.write('\\label{' + label + '} \n')
	
def write_vspace(f, spacing):
	f.write('\\vspace*{' + spacing + '} \n')
	
def write_hspace(f, spacing):
	f.write('\\hspace*{' + spacing + '} \n')