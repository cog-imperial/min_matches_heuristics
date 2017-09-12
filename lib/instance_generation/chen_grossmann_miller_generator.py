# The minimum utility cost problem instances are originally stored into .gms files.
# These files are parsed and .dat files are generated for storing the instances.

from os import listdir
from lib.io_modules.readers import parse_gams_file
from lib.io_modules.writers import write_min_utility_dat_file

def generate_chen_grossmann_miller_instances():
	source_files_path = 'data/original_instances/chen_grossmann_miller/gms_files/'
	dat_files_path = 'data/original_instances/chen_grossmann_miller/dat_files/'
	test_set='chen_grossmann_miller'

	source_files = listdir(source_files_path)
	for file_name in source_files:
		(inst,cat)=parse_gams_file(source_files_path,file_name)
		write_min_utility_dat_file(dat_files_path,cat,inst)
