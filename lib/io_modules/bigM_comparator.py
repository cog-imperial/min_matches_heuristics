from __future__ import print_function
from os import listdir
from lib.io_modules.readers import read_mip_instance, read_bigM_parameters
from lib.io_modules.writers import write_mip_solution
from lib.heuristic_methods.relaxation_rounding.lp_rounding import lp_rounding
from lib.heuristic_methods.relaxation_rounding.lr_rounding import lr_rounding
from lib.heuristic_methods.relaxation_rounding.fractional_relaxation import fractional_relaxation_lower_bound
import pandas as pd
import pickle

def bigM_compare():

	test_sets = ['furman_sahinidis','chen_grossman_miller','grossman_random']
	results = []

	for test_set in test_sets:
		dat_files_path = 'data/mip_instances/'+test_set
		test_ids = listdir(dat_files_path) 
		
		test_ids.sort()

		for test_id in test_ids:
			if '~' not in test_id:
				test_id=test_id.replace('.dat','')
				print(test_id)
				
				network = read_mip_instance(test_set, test_id)
				read_bigM_parameters(test_set, test_id, 'gundersen', network)
				
				for bigM_type in ['simple', 'gundersen', 'greedy']:
					network.set_bigM_parameter(bigM_type)
					(sol, elapsed_time) = lp_rounding(network)
					value = sol.matches
					#print(bigM_type + ':' + str(sol.matches))
					results.append((test_set, test_id, 'lp_rounding', bigM_type, value))
					
				for bigM_type in ['simple', 'gundersen', 'greedy']:
					network.set_bigM_parameter(bigM_type)
					(sol, elapsed_time) = lr_rounding(network)
					value = sol.matches
					#print(bigM_type + ':' + str(sol.matches))
					results.append((test_set, test_id, 'lr_rounding', bigM_type, value))
					
				for bigM_type in ['simple', 'gundersen', 'greedy']:
					network.set_bigM_parameter(bigM_type)
					value = fractional_relaxation_lower_bound(network)
					#print(bigM_type + ':' + str(relaxation_value))
					results.append((test_set, test_id, 'lp_relaxation', bigM_type, value))
					
	pickle_results(results)
	return results

def pickle_results(results):
	p = open('data/bigM_parameters/bigM_comparisons.pkl', 'wb')
	pickle.dump(results, p)
		
def reload_pickled_results(filename):
	p = open(filename, 'rb')
	return pickle.load(p)
      
def write_bigM_comparison_spreadsheet():
	
	results = reload_pickled_results('data/bigM_parameters/bigM_comparisons.pkl')
	
	df_lpr_list = []
	df_lrr_list = []
	df_relaxation_list = []
	
	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	algorithms = ['lp_rounding', 'lr_rounding', 'lp_relaxation']
	bigM_types = ['simple', 'gundersen', 'greedy']
	column_labels = ['Test Case', 'Simple', 'GTA97', 'LKM17']
	
	for test_set in test_sets:
	  
		dat_files_path = 'data/mip_instances/' + test_set
		test_ids = listdir(dat_files_path) 
		test_ids.sort()
		
		for test_id in test_ids:
			if '~' not in test_id:
				test_id = test_id.replace('.dat','')
				
				for algorithm in algorithms:
				  
					line = []
					line.append(test_id)
					
					for bigM_type in bigM_types:
						value = find_results_value(test_set, test_id, algorithm, bigM_type, results)
						if algorithm == 'lp_relaxation':
							value = format(value,'.2f')
						line.append(value)
						
					if algorithm == 'lp_rounding':
						df_lpr_list.append(line)
					if algorithm == 'lr_rounding':
						df_lrr_list.append(line)
					if algorithm == 'lp_relaxation':
						df_relaxation_list.append(line)
	
	writer = pd.ExcelWriter('data/bigM_parameters/bigM_comparisons.xlsx', engine='xlsxwriter')
	
	add_to_excel_writer(df_lpr_list, column_labels, 'lp_rounding', writer)
	add_to_excel_writer(df_lrr_list, column_labels, 'lr_rounding', writer)
	add_to_excel_writer(df_relaxation_list, column_labels, 'lp_relaxation', writer)
	
	writer.save()
	
def find_results_value(test_set, test_id, algorithm, bigM_type, results):
	for (tset, tid, algo, bigM_t, value) in results:
		if tset == test_set and test_id == tid and algo == algorithm and bigM_t == bigM_type:
			return value

def add_to_excel_writer(df_list, column_labels, algo_name, writer):
	df = pd.DataFrame(data = df_list, columns = column_labels)
	df.to_excel(writer, sheet_name = algo_name)