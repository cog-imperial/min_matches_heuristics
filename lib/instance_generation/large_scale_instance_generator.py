from lib.io_modules.writers import write_large_scale_min_utility_dat_file
from lib.problem_classes.min_utility_instance import Min_Utility_Instance
from lib.problem_classes.stream import Stream
from lib.problem_classes.utility import Utility
from random import randint, random

def generate_large_scale_instances():
	dat_files_path = 'data/original_instances/large_scale/dat_files/'
	
	DTmin = 10
	
	n = 80
	m = 80
	TSmax = 400
	TSmin = 30
	Fmax = 15
	TUmax = 500
	TUmin = 20
	Cmax = 80 # Hot utility cost
	Cmin = 20 # Cold utility cost
	
	for i in range(4,7):
		inst = large_scale_random_instance(n, m, DTmin, TSmax, TSmin, Fmax, TUmax, TUmin, Cmax, Cmin)
		write_large_scale_min_utility_dat_file(dat_files_path, inst, i)


def large_scale_random_instance(n,m, DTmin, TSmax, TSmin, Fmax, TUmax, TUmin, Cmax, Cmin):
	
	HS = []
	for i in range(n):
		HS.append(generate_hot_stream(TSmax, TSmin, Fmax))
	
	CS = []
	for j in range(m):
		CS.append(generate_cold_stream(TSmax, TSmin, Fmax))
	
	HU = []
	HU.append(Utility(TUmax, TUmax-1, Cmax))
	
	CU = []
	CU.append(Utility(TUmin, TUmin+1, Cmin))
	
	return Min_Utility_Instance(DTmin, HS, CS, HU, CU)


def generate_hot_stream(Tmax, Tmin, Fmax):
	
	Tin = randint(Tmin+1, Tmax)
	Tout = randint(Tmin, Tin-1)
	FCp = round(random()*Fmax,2)
	return Stream(Tin, Tout, FCp)


def generate_cold_stream(Tmax, Tmin, Fmax):
	
	Tin = randint(Tmin, Tmax-1)
	Tout = randint(Tin+1, Tmax)
	FCp = round(random()*Fmax,2)
	return Stream(Tin, Tout, FCp)