from __future__ import print_function
from os import listdir
from lib.io_modules.readers import read_mip_instance
from lib.io_modules.writers import write_mip_solution
from greedy_packing.largest_heat_match_lp_based import largest_heat_match_lp_based
from greedy_packing.largest_heat_match_greedy import largest_heat_match_greedy
from greedy_packing.largest_fraction_match import largest_fraction_match
from greedy_packing.shortest_stream import shortest_stream
from relaxation_rounding.lp_rounding import lp_rounding
from relaxation_rounding.lr_rounding import lr_rounding
from relaxation_rounding.cr_rounding import cr_rounding
from water_filling.water_filling_greedy import water_filling_greedy
from water_filling.water_filling_mip import water_filling_mip

def solve_heuristically():

	#test_sets = ['furman_sahinidis','chen_grossmann_miller','grossmann_random']
	test_sets = ['large_scale']

	for test_set in test_sets:
		dat_files_path = 'data/mip_instances/'+test_set
		test_ids = listdir(dat_files_path) 
		
		test_ids.sort()

		for test_id in test_ids:
			if '~' not in test_id and test_id in ['large_scale4.dat', 'large_scale5.dat', 'large_scale6.dat']:
				test_id=test_id.replace('.dat','')
				print(test_id)
				
				network=read_mip_instance(test_set,test_id)
				
				# PACKING HEURISTICS
				#for heuristic in ['largest_heat_match_lp_based', 'largest_heat_match_greedy', 'largest_fraction_match', 'shortest_stream'] :
				for heuristic in ['shortest_stream']:
					print(heuristic)
					#if heuristic == 'largest_heat_match_lp_based': 
					#	apply_heuristic(test_set, test_id, largest_heat_match_lp_based, heuristic)
					
					if heuristic == 'largest_heat_match_greedy':
						apply_heuristic(test_set, test_id, largest_heat_match_greedy, heuristic)
						
					if heuristic == 'largest_fraction_match':
						apply_heuristic(test_set, test_id, largest_fraction_match, heuristic)
						
					if heuristic == 'shortest_stream':
						apply_heuristic(test_set, test_id, shortest_stream, heuristic)
				
				
				# RELAXATION ROUNDING METHODS
				#for heuristic in ['lp_rounding', 'lr_rounding', 'cr_rounding']:
				for heuristic in ['lp_rounding']:
					print(heuristic)
					
					if heuristic == 'lp_rounding': 
						apply_heuristic(test_set, test_id, lp_rounding, heuristic)
						
					if heuristic == 'lr_rounding': 
						apply_heuristic(test_set, test_id, lr_rounding, heuristic)
						
					if heuristic == 'cr_rounding':
						apply_heuristic(test_set, test_id, cr_rounding, heuristic)
				
				
				# WATER FILLING METHODS
				#for heuristic in ['water_filling_greedy', 'water_filling_mip'] :
				for heuristic in ['water_filling_greedy']:
					print(heuristic)
					
					if heuristic == 'water_filling_greedy':
						apply_heuristic(test_set, test_id, water_filling_greedy, heuristic)
					
					if heuristic == 'water_filling_mip':
						apply_heuristic(test_set, test_id, water_filling_mip, heuristic)
						
def apply_heuristic(test_set, test_id, heuristic_function, heuristic_name):
	network = read_mip_instance(test_set, test_id)
	(sol, elapsed_time) = heuristic_function(network)
	print(heuristic_name + ':' + str(sol.matches))
	write_mip_solution(test_set, test_id, heuristic_name, sol, elapsed_time)
	