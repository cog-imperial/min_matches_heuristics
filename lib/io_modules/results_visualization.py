from __future__ import print_function, division
from os import listdir
from readers import read_mip_instance, read_mip_solution, read_heuristic_solution, read_furman_sahinidis_paper_mip_results, read_furman_sahinidis_paper_heuristic_results, read_furman_sahinidis_test_set_references
from latex_table import *
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib as mpl
from math import log10
from bigM_comparator import bigM_compare
import pickle
from matplotlib.backends.backend_pdf import PdfPages

def get_mip_results():

	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	models = ['transshipment', 'transportation']
	results = []
	
	for test_set in test_sets:
	
		for model in models:
		
			sol_files_path = 'data/mip_solutions/'+test_set+'/'+model+'/'
			sol_files = listdir(sol_files_path) 
		
			for sol_file in sol_files :
				
				if '.log' not in sol_file:
				
					if test_set in ['furman_sahinidis', 'chen_grossman_miller']:
						test_id = sol_file.replace('.sol','').split('_', 1)[0]
						solver = sol_file.replace('.sol','').split('_', 1)[1]
					
					if test_set in ['grossman_random']:
						test_id = sol_file.replace('.sol','').split('_', 2)[0] + '_' + sol_file.replace('.sol','').split('_', 2)[1]
						solver = sol_file.replace('.sol','').split('_', 2)[2]
					
					stats = read_mip_solution(test_set,test_id,solver,model)
					
					results.append((test_set, test_id, solver, model, stats))
					
	test_set = 'furman_sahinidis'
	model = 'furman_sahinidis_paper'
	results_path = 'data/mip_solutions/'+test_set+'/'+model+'/'
	
	solver = 'cplex'
	
	furman_sahinidis_results = read_furman_sahinidis_paper_mip_results(results_path, solver)
		
	for (test_id, stats) in furman_sahinidis_results:
		results.append((test_set, test_id, solver, model, stats))
					
	return results
      
def get_heuristic_results():

	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	methods = ['greedy_packing', 'water_filling', 'relaxation_rounding']
	results = []
	
	for test_set in test_sets:
	
		for method in methods:
		
			sol_files_path = 'data/heuristic_solutions/'+test_set+'/'+method+'/'
			sol_files = listdir(sol_files_path) 
		
			for sol_file in sol_files :
				
				if test_set in ['furman_sahinidis', 'chen_grossman_miller']:
					test_id = sol_file.replace('.sol','').split('_', 1)[0]
					heuristic = sol_file.replace('.sol','').split('_', 1)[1]
					
				if test_set in ['grossman_random']:
					test_id = sol_file.replace('.sol','').split('_', 2)[0] + '_' + sol_file.replace('.sol','').split('_', 2)[1]
					heuristic = sol_file.replace('.sol','').split('_', 2)[2]
				
				(upper_bound, elapsed_time) = read_heuristic_solution(test_set, test_id, method, heuristic)
				results.append((test_set, test_id, method, heuristic, upper_bound, elapsed_time))
	
	test_set = 'furman_sahinidis'
	method = 'furman_sahinidis_paper'
	results_path = 'data/heuristic_solutions/'+test_set+'/'+method+'/'
	
	heuristics = ['lp_rounding', 'lr_rounding', 'greedy']
	
	for heuristic in heuristics:
		furman_sahinidis_results = read_furman_sahinidis_paper_heuristic_results(results_path, heuristic)
		
		for (test_id, upper_bound) in furman_sahinidis_results:
			elapsed_time = 0
			results.append((test_set, test_id, method, heuristic, upper_bound, elapsed_time))
		
	return results
      
      
def generate_exact_methods_table():
	
	mip_results = get_mip_results()
	
	file_name = 'data/tex_tables/exact_methods.tex'
	path = ''
	f=open(path+file_name,'w')
	
	# WRITING THE FIRST LINES OF THE TABLE
	
	write_begin_table(f)
	write_script_size(f)
	write_begin_adjustbox(f)
	write_begin_non_bordered_tabular(f,13) # there are 7 columns
	write_hline(f)
	
	tid = multirow_element( bold_element('Test Case'), 2)
	cplex_transportation = multicolumn_element_both_borders( bold_element('CPLEX Transportation'), 3 ) 
	cplex_transshipment = multicolumn_element( bold_element('CPLEX Transshipment'), 3 ) 
	gurobi_transportation = multicolumn_element( bold_element('Gurobi Transportation'), 3 )
	gurobi_transshipment = multicolumn_element( bold_element('Gurobi Transshipment'), 3 )
	solver_line = [tid, cplex_transportation, cplex_transshipment, gurobi_transportation, gurobi_transshipment]
	write_line(f, solver_line)
	write_cline(f,2,13)
	
	obj = multicolumn_element_left_border(bold_element('Value'),1)
	cpu_time = bold_element('Time')
	gap = bold_element('Gap')
	label_line = ['', obj, cpu_time, gap, obj, cpu_time, gap, obj, cpu_time, gap, obj, cpu_time, gap]
	write_line(f, label_line)
	write_hline(f)
	
	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	
	for test_set in test_sets:
		
		if test_set == 'furman_sahinidis':
			test_set_label = bold_element('Furman Sahinidis Test Set \\cite{furman:2004} (30min time limit)')
			timeout = 1800
		if test_set == 'chen_grossman_miller':
			test_set_label = bold_element('Chen Grossman Miller Test Set \\cite{minlp,chen:2015} (2h time limit)')
			timeout = 7200
		if test_set == 'grossman_random':
			test_set_label = bold_element('Grossman Random Test Set \\cite{grossman:2017} (4h time limit)')
			timeout = 14400
		
		test_set_line = [non_centered_multicolumn_element(test_set_label, 13)]
		write_line(f, test_set_line)
		
		dat_files_path = 'data/mip_instances/' + test_set
		test_ids = listdir(dat_files_path) 
		test_ids.sort()
	
		for test_id in test_ids:
			if '~' not in test_id:
				
				results_line = []
			
				test_id = test_id.replace('.dat','')
				results_line.append(test_id.replace('_','\\_'))
				
				solvers = ['cplex', 'gurobi']
				models = ['transportation', 'transshipment']
				
				for solver in solvers:
					for model in models:
						for (tset, tid, solv, mod, stats) in mip_results:
							if test_set == tset and test_id == tid and solv == solver and mod == model:
								relative_gap = ((stats.upper_bound - stats.lower_bound) / stats.upper_bound)*100
								# The CPU time is added with 2 decimal precision
								if float(stats.elapsed_time) < timeout:
									results_line.append(int(stats.upper_bound))
									results_line.append(format(float(stats.elapsed_time),'.2f'))
									results_line.append('')
								else:
									results_line.append(str(int(stats.upper_bound)))
									#results_line.append(str(int(stats.upper_bound)) + '*')
									results_line.append('*')
									#results_line.append(int(float(stats.elapsed_time)))
									if relative_gap >= 4:
										results_line.append(str(int(relative_gap)) + '\\%')
									else:
										results_line.append('4' + '\\%')
								
				print(results_line)
				write_line(f, results_line)
			
		write_hline(f)
	
	write_end_tabular(f)
	write_end_adjustbox(f)
	write_vspace(f,'-0.2cm')
	write_caption(f,'Computational results using exact solvers CPLEX 12.6.3 and Gurobi 6.5.2 with relative gap 4\\%. The relative gap is (best incumbent - best lower bound) / best incumbent and  * indicates timeout. All exact method results are available online in \\cite{source_code}.')
	write_label(f,'Table:Exact_Methods')	
	write_end_table(f)
	f.close()

def generate_heuristic_methods_table():

	mip_results = get_mip_results()
	heuristic_results = get_heuristic_results()
	
	upper_bounds_file_name = 'data/tex_tables/heuristic_upper_bounds.tex'
	elapsed_times_file_name = 'data/tex_tables/heuristic_elapsed_times.tex'
	path = ''
	f_upper_bounds = open(path + upper_bounds_file_name,'w')
	f_elapsed_times = open(path + elapsed_times_file_name,'w')
	
	write_begin_table(f_upper_bounds)
	write_script_size(f_upper_bounds)
	write_begin_adjustbox(f_upper_bounds)
	write_begin_non_bordered_tabular(f_upper_bounds,11) # there are 6 columns
	write_hline(f_upper_bounds)
	
	write_begin_table(f_elapsed_times)
	write_script_size(f_elapsed_times)
	write_begin_adjustbox(f_elapsed_times)
	write_begin_non_bordered_tabular(f_elapsed_times,11) # there are 6 columns
	write_hline(f_elapsed_times)
	
	tid = multirow_element( bold_element('Test Case'), 2)
	rr = multicolumn_element_both_borders( bold_element('Relaxation Rounding'), 3) 
	wf = multicolumn_element( bold_element('Water Filling'), 2 ) 
	gp = multicolumn_element( bold_element('Greedy Packing'), 4 ) 
	cplex = multirow_element( bold_element('CPLEX'), 2)
	method_line = [tid, rr, wf, gp, cplex]
	
	write_line(f_upper_bounds, method_line)
	write_cline(f_upper_bounds,2,10)
	
	write_line(f_elapsed_times, method_line)
	write_cline(f_elapsed_times,2,10)
	
	lpr = multicolumn_element_left_border( bold_element('FLPR'), 1 )
	lrr = bold_element('LRR')
	crr = multicolumn_element( bold_element('CRR'), 1 )
	wfg = bold_element('WFG')
	wfm = multicolumn_element( bold_element('WFM'), 1 )
	lhmg = bold_element('LHM')
	lfm = bold_element('LFM')
	lhmlp = bold_element('LHM-LP')
	ss = multicolumn_element( bold_element('SS'), 1 )
	label_line = ['', lpr, lrr, crr, wfg, wfm, lhmg, lfm, lhmlp, ss, '']
	
	write_line(f_upper_bounds, label_line)
	write_hline(f_upper_bounds)
	
	write_line(f_elapsed_times, label_line)
	write_hline(f_elapsed_times)
	
	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	
	for test_set in test_sets:
		
		if test_set == 'furman_sahinidis':
			test_set_label = bold_element('Furman Sahinidis Test Set \\cite{furman:2004}')
			timeout = 1800
		if test_set == 'chen_grossman_miller':
			test_set_label = bold_element('Chen Grossman Miller Test Set \\cite{minlp,chen:2015}')
			timeout = 7200
		if test_set == 'grossman_random':
			test_set_label = bold_element('Grossman Random Test Set \\cite{grossman:2017}')
			timeout = 14400
		
		test_set_line = [non_centered_multicolumn_element(test_set_label, 11)]
		write_line(f_upper_bounds, test_set_line)
		write_line(f_elapsed_times, test_set_line)
		
		dat_files_path = 'data/mip_instances/' + test_set
		test_ids = listdir(dat_files_path) 
		test_ids.sort()
	
		for test_id in test_ids:
			if '~' not in test_id:
			
				upper_bound_results = []
				elapsed_time_results = []
			
				test_id = test_id.replace('.dat','')
				upper_bound_results.append(test_id.replace('_','\\_'))
				elapsed_time_results.append(test_id.replace('_','\\_'))
			
				method = 'relaxation_rounding'
				heuristics = ['lp_rounding', 'lr_rounding', 'cr_rounding']
			
				for heuristic in heuristics:
					for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
						if test_set == tset and test_id == tid and meth == method and heur == heuristic:
							upper_bound_results.append(int(upper_bound))
							elapsed_time_results.append(format(float(elapsed_time),'.2f'))
			
				method = 'water_filling'
				heuristics = ['water_filling_greedy', 'water_filling_mip']
			
				for heuristic in heuristics:
					for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
						if test_set == tset and test_id == tid and meth == method and heur == heuristic:
							upper_bound_results.append(int(upper_bound))
							elapsed_time_results.append(format(float(elapsed_time),'.2f'))
			
				method = 'greedy_packing'
				heuristics = ['largest_heat_match_greedy', 'largest_fraction_match', 'largest_heat_match_lp_based', 'shortest_stream']
			
				for heuristic in heuristics:
					for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
						if test_set == tset and test_id == tid and meth == method and heur == heuristic:
							upper_bound_results.append(int(upper_bound))
							elapsed_time_results.append(format(float(elapsed_time),'.2f'))
			
				solver = 'cplex'
				model = 'transshipment'
			
				for (tset, tid, solv, mod, stats) in mip_results:
					if test_set == tset and test_id == tid and solv == solver and mod == model:
						if float(stats.elapsed_time) < timeout:
							upper_bound_results.append(bold_element(str(int(stats.upper_bound))))
							elapsed_time_results.append(bold_element(str(format(float(stats.elapsed_time), '.2f'))))
						else:
							upper_bound_results.append(bold_element(str(int(stats.upper_bound))+'*'))
							elapsed_time_results.append(bold_element('*'))
			
				print(upper_bound_results)
				print(elapsed_time_results)
				write_line(f_upper_bounds, upper_bound_results)
				write_line(f_elapsed_times, elapsed_time_results)
		
		write_hline(f_upper_bounds)
		write_hline(f_elapsed_times)
	
	write_end_tabular(f_upper_bounds)
	write_end_adjustbox(f_upper_bounds)
	write_vspace(f_upper_bounds,'-0.2cm')
	write_caption(f_upper_bounds,'Upper bounds computed by the heuristics and CPLEX 12.6.3 with time limit (i) 30min for Furman Sahinidis test set, (ii) 2h for Chen Grossman Miller test set, and (iii) 4h for Grossman random test set. An * indicates timeout. All heuristic results are available online in \\cite{source_code}.')
	write_label(f_upper_bounds,'Table:Heuristic_Upper_Bounds')
	write_end_table(f_upper_bounds)
	f_upper_bounds.close()
	
	write_end_tabular(f_elapsed_times)
	write_end_adjustbox(f_elapsed_times)
	write_vspace(f_elapsed_times,'-0.2cm')
	write_caption(f_elapsed_times,'CPU times of the heuristics and CPLEX 12.6.3 with time limit (i) 30min for Furman Sahinidis test set, (ii) 2h for Chen Grossman Miller test set, and (iii) 4h for Grossman random test set. An * indicates timeout. All heuristic results are available online in \\cite{source_code}.')
	write_label(f_elapsed_times,'Table:Heuristic_CPU_Times')
	write_end_table(f_elapsed_times)
	f_elapsed_times.close()
	
def generate_comparison_table():
	
	mip_results = get_mip_results()
	heuristic_results = get_heuristic_results()
	
	file_name = 'data/tex_tables/comparisons.tex'
	path = ''
	f=open(path+file_name,'w')
	
	write_begin_table(f)
	write_script_size(f)
	write_begin_adjustbox(f)
	write_begin_non_bordered_tabular(f,13) # there are 11 columns
	write_hline(f)
	
	tid = multirow_element( bold_element('Test Case'), 3)
	rr = multicolumn_element_both_borders( bold_element('Relaxation Rounding'), 5) 
	wf = multicolumn_element( bold_element('Water Filling'), 3 )  
	cplex = multicolumn_element( bold_element('CPLEX'), 4)
	method_line = [tid, rr, wf, cplex]
	write_line(f, method_line)
	write_cline(f,2,13)
	
	fs = bold_element('FS04') 
	lkm = bold_element('LKM17') 
	author_line = ['', multicolumn_element_both_borders(fs,2), multicolumn_element(lkm,3), multicolumn_element(fs,1), multicolumn_element(lkm,2), multicolumn_element_both_borders(fs,2), multicolumn_element(lkm,2)]
	write_line(f, author_line)
	write_cline(f,2,13)
	
	lpr = multicolumn_element_left_border( bold_element('FLPR'), 1 )
	lrr = bold_element('LRR')
	crr = multicolumn_element( bold_element('CRR'), 1 )
	wfg = bold_element('WFG')
	wfm = multicolumn_element( bold_element('WFM'), 1 )
	value = bold_element('Value') 
	time = bold_element('Time') 
	label_line = ['', lpr, lrr, lpr, lrr, crr, multicolumn_element(wfg,1), wfg, wfm, value, time, multicolumn_element_left_border(value,1), time]
	write_line(f, label_line)
	write_hline(f)
	
	test_set = 'furman_sahinidis'
	
	dat_files_path='data/mip_instances/'+test_set
	test_ids=listdir(dat_files_path) 
	test_ids.sort()
	
	for test_id in test_ids:
		if '~' not in test_id:
			
			current_results = []
			
			test_id = test_id.replace('.dat','')
			current_results.append(test_id)
			
			method = 'furman_sahinidis_paper'
			heuristics = ['lp_rounding', 'lr_rounding']
			
			for heuristic in heuristics:
				for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
					if test_set == tset and test_id == tid and meth == method and heur == heuristic:
						current_results.append(int(upper_bound))
						
			method = 'relaxation_rounding'
			heuristics = ['lp_rounding', 'lr_rounding', 'cr_rounding']
			
			for heuristic in heuristics:
				for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
					if test_set == tset and test_id == tid and meth == method and heur == heuristic:
						current_results.append(int(upper_bound))
						
			method = 'furman_sahinidis_paper'
			heuristics = ['greedy']
			
			for heuristic in heuristics:
				for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
					if test_set == tset and test_id == tid and meth == method and heur == heuristic:
						current_results.append(int(upper_bound))
			
			method = 'water_filling'
			heuristics = ['water_filling_greedy', 'water_filling_mip']
			
			for heuristic in heuristics:
				for (tset, tid, meth, heur, upper_bound, elapsed_time) in heuristic_results:
					if test_set == tset and test_id == tid and meth == method and heur == heuristic:
						current_results.append(int(upper_bound))
						
			solver = 'cplex'
			models = ['furman_sahinidis_paper', 'transshipment']
			
			for model in models:
				for (tset, tid, solv, mod, stats) in mip_results:
					if test_set == tset and test_id == tid and solv == solver and mod == model:
						if float(stats.elapsed_time) < 1800:
							current_results.append(int(stats.upper_bound))
							current_results.append(format(float(stats.elapsed_time),'.2f'))
						else:
							current_results.append(str(int(stats.upper_bound)))
							if model == 'transshipment':
								current_results.append('*')
							if model == 'furman_sahinidis_paper':
								current_results.append('**')
						#if model == 'transshipment':
							#relative_gap = ((stats.upper_bound - stats.lower_bound) / stats.upper_bound)*100
							#if relative_gap > 4:
								#results_line.append(str(int(relative_gap)) + '\\%')
							#else:
								#results_line.append('')
								
			print(current_results)
			write_line(f, current_results)
			
	write_hline(f)
	write_end_tabular(f)
	write_end_adjustbox(f)
	write_vspace(f,'-0.2cm')
	write_caption(f,'Comparison of our results (labelled LKM17) with the ones reported by \\citet{furman:2004} (labelled FS04). LKM17 use CPLEX 12.6.3 while FS04 use CPLEX 7.0. An * indicates 30min timeout while ** corresponds to a 7h timeout. All results are available online in \\cite{source_code}.')
	write_label(f,'Table:Comparisons')
	write_end_table(f)
	f.close()








def get_furman_sahinidis_test_set_references():
	
	references_path = 'data/original_instances/furman_sahinidis/'
	references = read_furman_sahinidis_test_set_references(references_path)
	return references


def get_problem_sizes():

	test_sets=['furman_sahinidis','chen_grossman_miller','grossman_random']
	sizes = []
	
	for test_set in test_sets:
		dat_files_path='data/mip_instances/'+test_set
		test_ids=listdir(dat_files_path) 
	
		for test_id in test_ids:
			if '~' not in test_id:
				
				test_id=test_id.replace('.dat','') 
				print(test_id)

				network=read_mip_instance(test_set,test_id)
				
				n = network.n
				m = network.m
				k = network.k
				
				binary_vars = n*m
				continuous_vars = n*m*k + n*k
				constraints = n*k + n + m*k + n*m
				
				sizes.append((test_set, test_id, n, m, k, binary_vars, continuous_vars, constraints))
	
	return sizes



def generate_problem_sizes_table():
  
	problem_sizes = get_problem_sizes()
  
	file_name = 'data/tex_tables/problem_sizes.tex'
	path = ''
	f=open(path+file_name,'w')
	
	write_begin_table_with_ht(f)
	write_script_size(f)
	write_begin_adjustbox(f)
	write_begin_non_bordered_tabular(f,8) # there are 11 columns
	write_hline(f)
	
	test = multirow_element( bold_element('Test Case'), 2 )
	hot = bold_element('Hot')
	cold = bold_element('Cold')
	temperature = bold_element('Temperature')
	binary = bold_element('Binary')
	continuous = bold_element('Continuous')
	constraints = multirow_element( bold_element('Constraints'), 2 )
	reference = multirow_element( bold_element('Reference'), 2 )
	first_line = [test, hot, cold, temperature, binary, continuous, constraints, reference ]
	write_line(f, first_line)
	
	streams = bold_element('Streams')
	intervals = bold_element('Intervals')
	variables = bold_element('Variables') 
	second_line = ['', streams, streams, intervals, variables, variables, '', '']
	write_line(f, second_line)
	write_hline(f)
	
	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	
	for test_set in test_sets:
		
		if test_set == 'furman_sahinidis':
			test_set_label = bold_element('Furman Sahinidis Test Set \\cite{furman:2004}')
			furman_sahinidis_references = get_furman_sahinidis_test_set_references()
		if test_set == 'chen_grossman_miller':
			test_set_label = bold_element('Chen Grossman Miller Test Set \\cite{minlp,chen:2015}')
		if test_set == 'grossman_random':
			test_set_label = bold_element('Grossman Random Test Set \\cite{grossman:2017}')
		
		test_set_line = [non_centered_multicolumn_element(test_set_label, 8)]
		write_line(f, test_set_line)
		
		dat_files_path = 'data/mip_instances/' + test_set
		test_ids = listdir(dat_files_path) 
		test_ids.sort()
	
		for test_id in test_ids:
			if '~' not in test_id:
			  
				problem_line = []
			
				test_id = test_id.replace('.dat','')
				problem_line.append(test_id.replace('_','\\_'))
				
				for (tset, tid, n, m, k, binary_vars, continuous_vars, constraints) in problem_sizes:
					if tset == test_set and tid == test_id:
						problem_line.append(n)
						problem_line.append(m)
						problem_line.append(k)
						problem_line.append(binary_vars)
						problem_line.append(continuous_vars)
						problem_line.append(constraints)
						
				if test_set == 'furman_sahinidis':
					for (tid, reference) in furman_sahinidis_references:
						tid = tid.replace('.dat','')
						if tid == test_id:
							problem_line.append(reference)
				else:
					problem_line.append('')
			
			print(problem_line)
			write_line(f, problem_line)
			
		write_hline(f)
		
	write_end_tabular(f)
	write_end_adjustbox(f)
	write_vspace(f,'-0.2cm')
	write_caption(f,'Problem sizes of the test cases. The number of variables and constraints are computed using the transshipment model. All test cases are available online in \\cite{source_code}.')
	write_label(f,'Table:Problem_Sizes')
	write_end_table(f)
	f.close()
	


def performance_ratios():

	mip_results = get_mip_results()
	heuristic_results = get_heuristic_results()
	
	optimal_values = []
	
	for (test_set, test_id, solver, model, stats) in mip_results:
		if solver == 'gurobi' and model == 'transshipment':
			optimal_values += [(test_id, stats.upper_bound)]
			
	lpr = [] ; lrr = [] ; crr = [] # relaxation rounding methods
	wfg = [] ; wfm = [] # water filling methods
	lhm = [] ; lfm = [] ; lhm_lp = [] ; ss = [] # greedy packing methods 
	cplex = []
	test_cases = []
	
	for (tid, best_value) in optimal_values:
		if tid not in test_cases:
			test_cases.append(tid)
	
	for (test_set, test_id, method, heuristic, upper_bound, elapsed_time) in heuristic_results:
		
		if heuristic == 'lp_rounding' and method == 'relaxation_rounding':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					lpr.append(int(upper_bound) / best_value)
					cplex.append(1)
		
		if heuristic == 'lr_rounding' and method == 'relaxation_rounding':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					lrr.append(int(upper_bound) / best_value)
		
		if heuristic == 'cr_rounding':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					crr.append(int(upper_bound) / best_value)
		
		if heuristic == 'water_filling_greedy':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					wfg.append(int(upper_bound) / best_value)

		if heuristic == 'water_filling_mip':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					wfm.append(int(upper_bound) / best_value)
		
		if heuristic == 'largest_heat_match_greedy':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					lhm.append(int(upper_bound) / best_value)
		
		if heuristic == 'largest_fraction_match':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					lfm.append(int(upper_bound) / best_value)
		
		if heuristic == 'largest_heat_match_lp_based':  
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					lhm_lp.append(int(upper_bound) / best_value)
		
		if heuristic == 'shortest_stream':
			for (tid, best_value) in optimal_values:
				if test_id == tid:
					ss.append(int(upper_bound) / best_value)
					
	return (test_cases, lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex)


def elapsed_times():

	mip_results = get_mip_results()
	heuristic_results = get_heuristic_results()
	
	test_cases = []
	
	for (test_set, test_id, solver, model, stats) in mip_results:
		test_cases += [test_id]
	
	cplex = []
	lpr = [] ; lrr = [] ; crr = [] # relaxation rounding methods
	wfg = [] ; wfm = [] # water filling methods
	lhm = [] ; lfm = [] ; lhm_lp = [] ; ss = [] # greedy packing methods 
	
	for (test_set, test_id, method, heuristic, upper_bound, elapsed_time) in heuristic_results:
		
		if heuristic == 'lp_rounding' and method == 'relaxation_rounding':
			lpr.append(elapsed_time)
			for (tset, tid, solver, model, stats) in mip_results:
				if solver == 'gurobi' and model == 'transshipment' and tid == test_id:
					cplex += [stats.elapsed_time]
		
		if heuristic == 'lr_rounding' and method == 'relaxation_rounding':
			lrr.append(elapsed_time)
		
		if heuristic == 'cr_rounding':
			crr.append(elapsed_time)
		
		if heuristic == 'water_filling_greedy':
			wfg.append(elapsed_time)

		if heuristic == 'water_filling_mip':
			wfm.append(elapsed_time)
		
		if heuristic == 'largest_heat_match_greedy':
			lhm.append(elapsed_time)
		
		if heuristic == 'largest_fraction_match':
			lfm.append(elapsed_time)
		
		if heuristic == 'largest_heat_match_lp_based':  
			lhm_lp.append(elapsed_time)
		
		if heuristic == 'shortest_stream':
			ss.append(elapsed_time)
	
	return (test_cases, lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex)



# Given a set of labelresultss, one for each box and a 2 dimensional matrix with te
def generate_upper_bounds_box_plot():
	
	(test_cases, lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex) = performance_ratios()
	  
	#mpl.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
	#mpl.rc('text', usetex=True)
	
	box_labels = ['FLPR', 'LRR', 'CRR', 'WFG', 'WFM', 'LHM', 'LFM', 'LHM-LP', 'SS', 'CPLEX']
	numbered_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	
	f = plt.figure()
	plt.boxplot([lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex])
	plt.xticks(numbered_labels,box_labels)
	
	yticks = np.arange(0.8, 2.8, 0.2)                                                                                          
	plt.yticks(yticks)
	
	#plt.ylim((0.8,2.7))
	
	plt.xlabel('Heuristics')
	plt.ylabel('Performance ratio')
	
	plt.grid(axis='y')
	
	f.savefig('data/plots/performance_ratios_boxplot.pdf', bbox_inches='tight')
	
	
# Given a set of labels, one for each box and a 2 dimensional matrix with te
def generate_elapsed_times_box_plot():
	
	(test_cases, lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex) = elapsed_times()
	
	for i in range(len(lpr)):
		m = min(lpr[i], lrr[i], crr[i], wfg[i], wfm[i], lhm[i], lfm[i], lhm_lp[i], ss[i], cplex[i])
		
		# Normalization so that everything is greater or equal to 1
		lpr[i] = lpr[i] / m ; lrr[i] = lrr[i] / m ; crr[i] = crr[i] / m
		wfg[i] = wfg[i] / m ; wfm[i] = wfm[i] / m
		lhm[i] = lhm[i] / m ; lfm[i] = lfm[i] / m ; lhm_lp[i] = lhm_lp[i] / m ; ss[i] = ss[i] / m
		cplex[i] = cplex[i] / m
		
		# Logarithms
		lpr[i] = log10(lpr[i]) ; lrr[i] = log10(lrr[i]) ; crr[i] = log10(crr[i]) 
		wfg[i] = log10(wfg[i]) ; wfm[i] = log10(wfm[i])
		lhm[i] = log10(lhm[i]) ; lfm[i] = log10(lfm[i]) ; lhm_lp[i] = log10(lhm_lp[i]) ; ss[i] = log10(ss[i])
		cplex[i] = log10(cplex[i])
	
	#mpl.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
	#mpl.rc('text', usetex=True)
	
	box_labels = ['FLPR', 'LRR', 'CRR', 'WFG', 'WFM', 'LHM', 'LFM', 'LHM-LP', 'SS', 'CPLEX']
	numbered_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9,10]
	
	f = plt.figure()
	plt.boxplot([lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex])
	plt.xticks(numbered_labels,box_labels)
	
	yticks = np.arange(-0.5, 6, 0.5)                                                                                          
	plt.yticks(yticks)
	
	#plt.ylim((-1,9))
	
	plt.xlabel('Heuristics')
	plt.ylabel('Elapsed time (log-10 scale)')
	
	plt.grid(axis='y')
	
	f.savefig('data/plots/elapsed_times_boxplot.pdf', bbox_inches='tight')
	
def swap(l,i,j):
	temp = l[i]
	l[i] = l[j]
	l[j] = temp
	
def generate_line_chart():
	
	(test_cases, lpr, lrr, crr, wfg, wfm, lhm, lfm, lhm_lp, ss, cplex) = performance_ratios()
	
	best_rr = [min(lpr[i], lrr[i], crr[i]) for i in range(len(lpr))]
	best_wf = [min(wfg[i], wfm[i]) for i in range(len(wfg))]
	best_packing = [min(lhm[i], lfm[i], lhm_lp[i], ss[i]) for i in range(len(lhm))]
	
	#for i in range(len(lpr)-1):
		#for j in range(i+1,len(lpr)):
			#if best_rr[i] + best_wf[i] + lhm_lp[i] + ss[i] > best_rr[j] + best_wf[j] + lhm_lp[j] + ss[j]:
				#swap(best_rr,i,j)
				#swap(best_wf,i,j)
				#swap(lhm_lp,i,j)
				#swap(ss,i,j)
				
	f = plt.figure()
	
	plt.plot(cplex, linestyle = 'dashdot', label = 'CPLEX', color = 'black')
	plt.plot(best_rr, linestyle = 'dashed', label = 'Best Relaxation Rounding', color = 'blue')
	plt.plot(best_wf, linestyle = 'dotted', label = 'Best Water Filling', color = 'green')
	plt.plot(best_packing, linestyle = 'solid', label = 'Best Greedy Packing', color = 'red')
	#plt.plot(ss)
	
	#box_labels = ['LPR', 'LRR', 'CRR', 'WFG', 'WFM', 'LHM', 'LFM', 'LHM-LP', 'SS']
	#numbered_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	#plt.xticks(numbered_labels,box_labels)
	
	plt.ylim((0.95,1.9))
	
	plt.xlabel('Test case')
	plt.ylabel('Performance ratio')
	
	plt.legend(loc = 2)
	
	f.savefig('data/plots/heuristic_comparison_line_chart.pdf', bbox_inches='tight')
	
	#plt.show()
	

def reload_pickled_results(filename):
	p = open(filename, 'rb')
	return pickle.load(p)

def generate_bigM_comparison_table():
  
	bigM_results = reload_pickled_results('data/bigM_parameters/bigM_comparisons.pkl')
	
	file_name = 'data/tex_tables/bigM_comparisons.tex'
	path = ''
	f=open(path+file_name,'w')
	
	write_begin_table(f)
	write_script_size(f)
	write_begin_adjustbox(f)
	write_begin_non_bordered_tabular(f,10) # there are 11 columns
	write_hline(f)
	
	tid = multirow_element( bold_element('Test Case'), 2)
	flpr = multicolumn_element_both_borders( bold_element('Fractional LP Rounding'), 3) 
	lrr = multicolumn_element( bold_element('Lagrangian Relaxation Rounding'), 3 )  
	fr = multicolumn_element( bold_element('Fractional Relaxation'), 3)
	algo_line = [tid, flpr, lrr, fr]
	write_line(f, algo_line)
	write_cline(f,2,10)
	
	simple = multicolumn_element_left_border( bold_element('Simple'), 1 ) 
	gta = bold_element('GTA97') 
	lkm = bold_element('LKM17') 
	author_line = ['', simple, gta, lkm, simple, gta, lkm, simple, gta, lkm ]
	write_line(f, author_line)
	write_hline(f)
	
	algorithms = ['lp_rounding', 'lr_rounding', 'lp_relaxation']
	bigM_types = ['simple', 'gundersen', 'greedy']
	test_sets = ['furman_sahinidis', 'chen_grossman_miller', 'grossman_random']
	
	for test_set in test_sets:
		
		if test_set == 'furman_sahinidis':
			test_set_label = bold_element('Furman Sahinidis Test Set \\cite{furman:2004}')
		if test_set == 'chen_grossman_miller':
			test_set_label = bold_element('Chen Grossman Miller Test Set \\cite{minlp,chen:2015}')
		if test_set == 'grossman_random':
			test_set_label = bold_element('Grossman Random Test Set \\cite{grossman:2017}')
		
		test_set_line = [non_centered_multicolumn_element(test_set_label, 10)]
		write_line(f, test_set_line)
		
		dat_files_path = 'data/mip_instances/' + test_set
		test_ids = listdir(dat_files_path) 
		test_ids.sort()
		
		for test_id in test_ids:
			if '~' not in test_id:
			  
				results_line = []
			
				test_id = test_id.replace('.dat','')
				results_line.append(test_id.replace('_','\\_'))
		
				for algorithm in algorithms:
					
					for bigM_type in bigM_types:
					
						for (tset, tid, algo, bigM_t, value) in bigM_results:
						  
							if tset == test_set and test_id == tid and algo == algorithm and bigM_t == bigM_type:
								
								if algo == 'lp_relaxation':
									value = format(value,'.2f')
								results_line.append(value)
								
				print(results_line)
				write_line(f, results_line)
		write_hline(f)
				
	write_end_tabular(f)
	write_end_adjustbox(f)
	write_vspace(f,'-0.2cm')
	write_caption(f,'Comparison of the Fractional LP Rounding and Lagrangian Relaxation Rounding upper bounds as well as the fractional relaxation lower bound using the different known ways for computing the bigM parameters, namely (i) the simple, (ii) the \\citet{gundersen:1997} (GTA97) and (iii) our greedy (LKM17).')
	write_label(f,'Table:BigM_Comparisons')
	write_end_table(f)
	f.close()