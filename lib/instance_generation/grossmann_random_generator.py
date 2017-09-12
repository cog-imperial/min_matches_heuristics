# Apart from FCp, all parameters of grossmann_random instances are obtained by parsing the .gms files.
# The FCp parameters are generated randomly.

from __future__ import division
from os import listdir
from lib.io_modules.readers import parse_random_gams_file
from lib.io_modules.writers import write_min_utility_random_dat_file

# Functions for the generation of the instance
from math import floor, ceil
from random import randint
from lib.problem_classes.stream import Stream
from lib.problem_classes.utility import Utility
from lib.problem_classes.min_utility_instance import Min_Utility_Instance

def generate_grossmann_random_instances():
	source_files_path = 'data/original_instances/grossmann_random/gms_files/'
	dat_files_path = 'data/original_instances/grossmann_random/dat_files/'
	test_set='grossmann_random'

	source_files = [file_name for file_name in listdir(source_files_path) if file_name.startswith('Transshipment')]
	for file_name in source_files: 
		(inst,cat)=parse_random_gams_file(source_files_path,file_name)
		for trial in range(3):
			rand_inst=random_instance(inst,cat)
			write_min_utility_random_dat_file(dat_files_path,cat,rand_inst,trial)
      
def random_instance(inst,cat):
	DTmin = inst.DTmin
	if cat == 'balanced':
		HS = [Stream(hs.Tin,hs.Tout,random_balanced(hs.FCp)) for hs in inst.HS]
		CS = [Stream(cs.Tin,cs.Tout,random_balanced(cs.FCp)) for cs in inst.CS]
	if cat == 'unbalanced':
		HS = [Stream(hs.Tin,hs.Tout,random_unbalanced(hs.FCp)) for hs in inst.HS]
		CS = [Stream(cs.Tin,cs.Tout,random_unbalanced(cs.FCp)) for cs in inst.CS]
	rand_inst = Min_Utility_Instance(inst.DTmin,HS,CS,inst.HU,inst.CU)
	return rand_inst
      
def random_balanced(FCp):
	return randint(ceil(0.9*10*FCp),floor(1.1*10*FCp))/10

def random_unbalanced(FCp):
	if FCp<1: return randint(ceil(0.9*100*FCp),floor(1.1*100*FCp))/100
	if FCp>=1 and FCp<6: return randint(ceil(0.9*20*FCp),floor(1.1*20*FCp))/20
	if FCp>=6: return randint(ceil(0.9*10*FCp),floor(1.1*10*FCp))/10