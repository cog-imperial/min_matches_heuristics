from __future__ import print_function
from os import listdir
from lib.io_modules.readers import read_mip_instance
from lib.io_modules.writers import write_mip_solution
from transshipment_mip_solver import solve_transshipment_mip
from transportation_mip_solver import solve_transportation_mip


def solve_exactly():
	
	#test_sets = ['furman_sahinidis','chen_grossman_miller','grossman_random']
	
	#test_sets = ['furman_sahinidis']
	#timeout = 1800
	
	#test_sets = ['chen_grossman_miller']
	#timeout = 7200
	
	test_sets = ['grossman_random']
	timeout = 14400
	
	for test_set in test_sets:
		dat_files_path='data/mip_instances/'+test_set
		test_ids=listdir(dat_files_path) 
	
		for test_id in test_ids:
			if '~' not in test_id:
				
				test_id=test_id.replace('.dat','') 
				print(test_id)
				
				for solver in ['cplex','gurobi']:
					print(solver)
					
					network = read_mip_instance(test_set,test_id)
					(sol,stats) = solve_transportation_mip(test_set,test_id,solver,timeout,network)
					write_mip_solution(test_set,test_id,solver,sol,stats)
					(sol,stats) = solve_transshipment_mip(test_set,test_id,solver,timeout,network)
					write_mip_solution(test_set,test_id,solver,sol,stats)
