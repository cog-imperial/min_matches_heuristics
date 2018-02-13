from re import search
from math import ceil, floor
from ..problem_classes.stream import Stream
from ..problem_classes.utility import Utility
from ..problem_classes.min_utility_instance import Min_Utility_Instance
from ..problem_classes.network import Network
from ..exact_methods.solver_statistics import Solver_Statistics


# It used while parsing the gams file and reads the value of a parameter 
# which is either a numerival value, or a vector of numerical values.
# We distinguish two cases depending on whether the parameter is defined 
# in a single line or multiple lines.
def gams_parameter_value(param,file_lines):
	for line in file_lines:
		if line.startswith('Parameter ' + param):
			next_line_index = file_lines.index(line)+1
			s=''
			while True:
				next_line=file_lines[next_line_index]
				s+=next_line
				if '/ ;' in next_line: break
				next_line_index+=1
			string_list = s.split('\r\n')
			val=[]
			for i in range(len(string_list)):
				string_list[i]=string_list[i].replace('/ ;','')
				string_list[i]=string_list[i].replace('/','')
				s=string_list[i].split()
				if len(s)>0: val.append(float(s[1]))
			return val

def gams_scalar_value(scalar,file_lines):
	for line in file_lines:
		if line.startswith('Scalar ' + scalar):
			next_line_index = file_lines.index(line)+1
			s = file_lines[next_line_index]
			s = s.replace('/ ;','')
			s = s.replace('/','')
			s = s.split()
			return float(s[0])

      
def parse_gams_file(dir_path,file_name):
	
	if file_name.endswith('X.gms'): 
		category='unbalanced'
	else: 
		category = 'balanced'
	
	f = open(dir_path+file_name, 'r')
	file_lines = f.readlines() 
	f.close()
	
	DTmin=gams_scalar_value('dT',file_lines)
	
	FCpHS=gams_parameter_value('FCpH',file_lines)
	TinHS=gams_parameter_value('TinH',file_lines)
	ToutHS=gams_parameter_value('ToutH',file_lines)
	
	FCpCS=gams_parameter_value('FCpC',file_lines)
	TinCS=gams_parameter_value('TinC',file_lines)
	ToutCS=gams_parameter_value('ToutC',file_lines)
	
	costHU=gams_parameter_value('CS',file_lines)
	TinHU=gams_parameter_value('TinS',file_lines)
	ToutHU=gams_parameter_value('ToutS',file_lines)
	
	costCU=gams_parameter_value('CW',file_lines)
	TinCU=gams_parameter_value('TinW',file_lines)
	ToutCU=gams_parameter_value('ToutW',file_lines)
	
	HS=[Stream(TinHS[i],ToutHS[i],FCpHS[i]) for i in range(len(FCpHS))]
	CS=[Stream(TinCS[i],ToutCS[i],FCpCS[i]) for i in range(len(FCpCS))]
	HU=[Utility(TinHU[i],ToutHU[i],costHU[i]) for i in range(len(costHU))]
	CU=[Utility(TinCU[i],ToutCU[i],costCU[i]) for i in range(len(costCU))]
	
	return (Min_Utility_Instance(DTmin,HS,CS,HU,CU),category)
      
      
def parse_random_gams_file(dir_path,file_name):
	
	if 'Unbalanced' in file_name: category='unbalanced'
	else: category = 'balanced'
	
	f = open(dir_path+file_name, 'r')
	file_lines = f.readlines() 
	f.close()
	
	random_file_name='Random_Parameters'+file_name.split('Transshipment_v1')[1]
	f = open(dir_path+random_file_name, 'r')
	random_file_lines = f.readlines() 
	f.close()
	
	DTmin=gams_scalar_value('dT',file_lines)
	
	FCpHS=gams_parameter_value('FCpH',random_file_lines)
	TinHS=gams_parameter_value('TinH',file_lines)
	ToutHS=gams_parameter_value('ToutH',file_lines)
	
	FCpCS=gams_parameter_value('FCpC',random_file_lines)
	TinCS=gams_parameter_value('TinC',file_lines)
	ToutCS=gams_parameter_value('ToutC',file_lines)
	
	costHU=gams_parameter_value('CS',file_lines)
	TinHU=gams_parameter_value('TinS',file_lines)
	ToutHU=gams_parameter_value('ToutS',file_lines)
	
	costCU=gams_parameter_value('CW',file_lines)
	TinCU=gams_parameter_value('TinW',file_lines)
	ToutCU=gams_parameter_value('ToutW',file_lines)
	
	HS=[Stream(TinHS[i],ToutHS[i],FCpHS[i]) for i in range(len(FCpHS))]
	CS=[Stream(TinCS[i],ToutCS[i],FCpCS[i]) for i in range(len(FCpCS))]
	HU=[Utility(TinHU[i],ToutHU[i],costHU[i]) for i in range(len(costHU))]
	CU=[Utility(TinCU[i],ToutCU[i],costCU[i]) for i in range(len(costCU))]
	
	return (Min_Utility_Instance(DTmin,HS,CS,HU,CU),category)


def read_min_utility_test_case(test_set,test_id):
	
	path='data/original_instances/'+test_set+'/dat_files/'+test_id+'.dat'
	f = open(path, 'r')
	lines = f.readlines()
	f.close()
	
	for line in lines: 
		if line.startswith('DTmin'): DTmin = float(line.split()[1])
	
	elements=[line.split() for line in lines]
	HS=[Stream(float(e[1]),float(e[2]),float(e[3])) for e in elements if e[0][0]=='H' and e[0][1]!='U']
	CS=[Stream(float(e[1]),float(e[2]),float(e[3])) for e in elements if e[0][0]=='C' and e[0][1]!='U']
	HU=[Utility(float(e[1]),float(e[2]),float(e[3])) for e in elements if e[0][0]=='H' and e[0][1]=='U']
	CU=[Utility(float(e[1]),float(e[2]),float(e[3])) for e in elements if e[0][0]=='C' and e[0][1]=='U']

	return Min_Utility_Instance(DTmin,HS,CS,HU,CU)


def read_mip_instance(test_set,test_id):
	
	path='data/mip_instances/'+test_set+'/'+test_id+'.dat'
	f = open(path, 'r')
	lines = f.readlines()
	f.close()
	
	for line in lines:
		s=line.replace('\n','')
		if s.startswith('Cost='): cost = float(s.replace('Cost=',''))
		if s.startswith('n='): n = int(s.replace('n=',''))
		if s.startswith('m='): m = int(s.replace('m=',''))
		if s.startswith('k='): k = int(s.replace('k=',''))
		
	QH=[[0 for t in range(k)] for i in range(n)]
	QC=[[0 for t in range(k)] for i in range(m)]
	R=[0 for t in range(k+1)]
	
	for line in lines:
		s=line.replace('\n','')
		if s.startswith('QH'):
			s=line.split()
			str_i=s[0].replace('QH[','')
			str_i=str_i.replace(']:','')
			i= int(str_i)
			heat_transfers=[]
			for e in range(len(s)):
				if e%2!=0:
					t=int(s[e].replace('T',''))
					q=float(s[e+1])
					QH[i][t]=q
		elif s.startswith('QC'):
			s=line.split()
			str_j=s[0].replace('QC[','')
			str_j=str_j.replace(']:','')
			j= int(str_j)
			heat_transfers=[]
			for e in range(len(s)):
				if e%2!=0:
					t=int(s[e].replace('T',''))
					q=float(s[e+1])
					QC[j][t]=q
		elif s.startswith('R'):
			s=line.split()
			str_t=s[0].replace('R[','')
			str_t=str_t.replace(']=','')
			t=int(str_t)
			R[t]=float(s[1])
			
	return Network(cost, n, m, 0, 0, k, QH, QC, [], [], R, None)
      
def read_mip_instance_heats(test_set,test_id):
	
	network = read_mip_instance(test_set,test_id)
	hot_heats = []
	cold_heats = []
	
	for i in range(network.n):
		hot_heats.append(sum(network.QH[i]))
	
	for j in range(network.m):
		cold_heats.append(sum(network.QC[j]))
	
	return (hot_heats, cold_heats)

def read_packing_instance(test_set,test_id):
	
	path='data/packing_instances/'+test_set+'/'+test_id+'.dat'
	f = open(path, 'r')
	lines = f.readlines()
	f.close()
	
	H=[]
	C=[]
	
	for line in lines:
		s=line.replace('\n','')
		
		if s.startswith('H'):
			s=line.split()
			str_i=s[0].replace('H[','')
			str_i=str_i.replace(']:','')
			i= int(str_i) # the index of hot stream i
			str_i=s[1].replace('Tin=','')
			Tin= float(str_i) # the inlet temperature of hot stream i
			str_i=s[2].replace('Tout=','')
			Tout= float(str_i) # the outlet temperature of hot stream i
			str_i=s[3].replace('FCp=','')
			FCp= float(str_i) # the flow rate heat capacity of hot stream i
			H.append(Stream(Tin,Tout,FCp))
		
		elif s.startswith('C'):
			s=line.split()
			str_i=s[0].replace('C[','')
			str_i=str_i.replace(']:','')
			i= int(str_i) # the index of hot stream i
			str_i=s[1].replace('Tin=','')
			Tin= float(str_i) # the inlet temperature of hot stream i
			str_i=s[2].replace('Tout=','')
			Tout= float(str_i) # the outlet temperature of hot stream i
			str_i=s[3].replace('FCp=','')
			FCp= float(str_i) # the flow rate heat capacity of hot stream i
			C.append(Stream(Tin,Tout,FCp))
			
	packing=Packing()
	packing.initialize_from_stream_lists(H,C)
	
	return packing
  

def find_substring_between(s, former, latter):
	start = s.find(former) + len(former)
	end = s.find(latter, start)
	return s[start:end]

def read_nodes_explored(test_set,test_id,solver,mip_type):
    
	f=open('data/mip_solutions/' + test_set + '/' + mip_type + '/' + test_id + '_' + solver + '.log', 'r')
	text = f.read()
    
	if solver == 'cplex':
		s_success = find_substring_between(text, 'Nodes = ', ' ')
		s_failure = find_substring_between(text, 'Nodes = ', '\n')
		if len(s_success) < len(s_failure):
			s = s_success
		else:
			s = s_failure
    
	if solver == 'gurobi':
		s = find_substring_between(text, 'Explored ', ' nodes')
    
	f.close()
    
	return int(s)


def read_mip_solution(test_set,test_id,solver,mip_type):
  
	f=open('data/mip_solutions/' + test_set + '/' + mip_type + '/' + test_id + '_' + solver + '.sol', 'r')
	lines = f.readlines()
	f.close()
      
	for line in lines:
		if line.startswith('Elapsed time:'): elapsed_time = float(line.split()[2])
		if line.startswith('Nodes explored:'): nodes_explored = int(line.split()[2])
		if line.startswith('Upper bound:'): upper_bound = int(float(line.split()[2]))
		#if line.startswith('Lower bound:'): lower_bound = ceil(float(line.split()[2]))
		if line.startswith('Lower bound:'): lower_bound = float(line.split()[2])
		
	return Solver_Statistics(elapsed_time,nodes_explored,lower_bound,upper_bound)
      
def read_mip_solution_heat_exchanges(test_set,test_id,solver,mip_type):
  
	f=open('data/mip_solutions/' + test_set + '/' + mip_type + '/' + test_id + '_' + solver + '.sol', 'r')
	lines = f.readlines()
	f.close()
	
	epsilon = 10**(-5)
	
	# Dictionary with heat exchanges
	hex_dict = dict()
	
	for line in lines:
		if line.startswith('y'): 
			i = int(line.split('[')[1].split(',')[0])
			j = int(line.split(',')[1].split(']')[0])
			hex_dict[i,j] = 0
			
	for line in lines:
		if line.startswith('q'): 
			
			if mip_type == 'transportation':
				i = int(line.split('[')[1].split(',')[0])
				j = int(line.split(',')[2].split(']')[0])
				heat = float(line.split('=')[1])
				if heat > epsilon:
					hex_dict[i,j] += heat
			
			if mip_type == 'transshipment':
				i = int(line.split('[')[1].split(',')[0])
				j = int(line.split(',')[1].split(']')[0])
				heat = float(line.split('=')[1])
				if heat > epsilon:
					hex_dict[i,j] += heat 
		
	return hex_dict


def read_heuristic_solution(test_set,test_id,heuristic_type,heuristic):
  
	f=open('data/heuristic_solutions/' + test_set + '/' + heuristic_type + '/' + test_id + '_' + heuristic + '.sol', 'r')
	lines = f.readlines()
	f.close()
      
	for line in lines:
		if line.startswith('Elapsed time:'): elapsed_time=float(line.split()[2])
		if line.startswith('Upper bound:'): upper_bound=ceil(float(line.split()[2]))
		
	return (upper_bound,elapsed_time)


def read_heuristic_solution_heat_exchanges(test_set,test_id,heuristic_type,heuristic):
  
	f=open('data/heuristic_solutions/' + test_set + '/' + heuristic_type + '/' + test_id + '_' + heuristic + '.sol', 'r')
	lines = f.readlines()
	f.close()
	
	epsilon = 10**(-5)
	
	# Dictionary with heat exchanges
	hex_dict = dict()
	
	for line in lines:
		if line.startswith('y'): 
			i = int(line.split('[')[1].split(',')[0])
			j = int(line.split(',')[1].split(']')[0])
			hex_dict[i,j] = 0
			
	for line in lines:
		if line.startswith('q'): 
			
			if heuristic_type == 'relaxation_rounding' or heuristic_type == 'greedy_packing':
				i = int(line.split('[')[1].split(',')[0])
				j = int(line.split(',')[2].split(']')[0])
				heat = float(line.split('=')[1])
				if heat > epsilon:
					hex_dict[i,j] += heat
			
			if heuristic_type == 'water_filling':
				i = int(line.split('[')[1].split(',')[0])
				j = int(line.split(',')[1].split(']')[0])
				heat = float(line.split('=')[1])
				if heat > epsilon:
					hex_dict[i,j] += heat
		
	return hex_dict
      
def read_furman_sahinidis_paper_heuristic_results(results_path, heuristic):
  
	f = open(results_path + heuristic + '.txt', 'r')
	lines = f.readlines()
	f.close()
	
	results = []
	
	for line in lines:
		test_id = line.split()[0]
		upper_bound = line.split()[1]
		results.append((test_id, upper_bound))
		
	return results
      
def read_furman_sahinidis_paper_mip_results(results_path, solver):
  
	f = open(results_path + solver + '.txt', 'r')
	lines = f.readlines()
	f.close()
	
	results = []
	
	for line in lines:
		test_id = line.split()[0]
		upper_bound = line.split()[1]
		elapsed_time = line.split()[2]
		stats = Solver_Statistics(elapsed_time, 0, 0, upper_bound)
		results.append((test_id, stats))
		
	return results
      
def read_furman_sahinidis_test_set_references(references_path):

	f = open(references_path + 'references.txt', 'r')
	lines = f.readlines()
	f.close()
	
	references = []
	
	for line in lines:
		test_id = line.split()[0]
		reference = line.split()[1]
		references.append((test_id, reference))
		
	return references
      
def read_bigM_parameters(test_set, test_id, bigM_type, network):
	
	f = open('data/bigM_parameters/' + test_set + '/' + bigM_type + '/' + test_id + '.bgm', 'r')
	lines = f.readlines()
	f.close()
	
	for line in lines:
		
		pair = line.split()[0]
		pair = pair.replace('U[','')
		pair = pair.replace(']=','')
		i = int(pair.split(',')[0])
		j = int(pair.split(',')[1])
		
		if bigM_type == 'gundersen':
			network.U_gundersen[i][j] = float(line.split()[1])