from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from time import time
from ...problem_classes.heat_exchange import Heat_Exchange

epsilon = 10**(-7)

def water_filling_mip(inst):
	
	# Local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC) 
	
	total_hot_heat = sum(sum(QH[i]) for i in range(n)) 
	total_cold_heat = sum(sum(QC[j]) for j in range(m)) 
	
	q = [[[0 for u in range(k)] for j in range(m)] for i in range(n)]
	y = [[0 for j in range(m)] for i in range(n)]
	M = []
	
	# Timer
	start_time = time()
	
	for u in range(k):
		#print('TEMPERATURE INTERVAL '+str(u))
		
		if sum(QH[i][u] for i in range(n)) > epsilon and sum(QC[j][u] for j in range(m)) > epsilon:
		
			if len(M) > 0:
				current_q = max_heat(n, m, QH, QC, u, M)
				for i in range(n):
					for j in range(m):
						if current_q[i][j] > epsilon:
							q[i][j][u] += current_q[i][j]
							QH[i][u] -= current_q[i][j]
							QC[j][u] -= current_q[i][j]
							##print('Re-use H' + str(i) + ' to C' + str(j) + ': ' + str(current_q[i][j]))
							##raw_input()
		
		
		if sum(QH[i][u] for i in range(n)) > epsilon and sum(QC[j][u] for j in range(m)) > epsilon:
		  
			current_q = mip_single_temperature_interval(n, m, QH, QC, u)
			# print(sum(current_q[i][j] for i in range(n) for j in range(m)))
			
			#print(current_q)
			
			#raw_input()
			
			for i in range(n):
				for j in range(m):
					if current_q[i][j] > epsilon:
						#print(QH)
						#print(QC)
						q[i][j][u] += current_q[i][j]
						QH[i][u] -= current_q[i][j]
						QC[j][u] -= current_q[i][j]
						y[i][j] = 1
						M.append((i,j))
						#print('New H' + str(i) + ' to C' + str(j) + ': ' + str(current_q[i][j]))
						#raw_input()
		
		if u < k-1:
			for i in range(n):
				QH[i][u+1] += QH[i][u]
				QH[i][u] = 0
		
		#for i in range(n):
			#print(str(i) + ': ' + str(sum(QH[i])))
		
		#print()
		
		#for i in range(n):
		        #print(str(i) + ':' + str(sum(q[i][j][t] for j in range(m) for t in range(u))))
		
		#print('----------------------------------------------------------')
		
		#print(M)
		#raw_input()
		#break
		
	#print(QH)
	#print(QC)
	
	algo_heat = sum(q[i][j][u] for i in range(n) for j in range(m) for u in range(k)) 
	
	#if equality(algo_heat, total_hot_heat) and equality(algo_heat, total_cold_heat): 
		#print('CORRECT')
	#else:
		#print('ERROR')
	
	#print( str(algo_heat) + ' vs ' + str(total_hot_heat) + ' or ' + str(total_cold_heat))
	
	end_time = time()
	elapsed_time = end_time-start_time
	
	matches = len(M)
	
	sol = Heat_Exchange('water_filling',n,m,k,matches,y,q)
	
	return (sol, elapsed_time)
      




# Given a subset of matches M, it computes the maximum (total) heat that can be transferred using only the matches in M.
# This computation is accomplished by solving a linear program.
def max_heat(n, m, QH, QC, u, M):

	# Local copy of the instance.
	h = list([QH[i][u] for i in range(n)])
	c = list([QC[j][u] for j in range(m)])
	
	for i in range(n):
		if h[i] < epsilon:
			h[i] = 0
			
	for j in range(m):
		if c[j] < epsilon:
			c[j] = 0

	model = AbstractModel()

	model.n = Param(within=NonNegativeIntegers, initialize=n) # number of hot streams
	model.m = Param(within=NonNegativeIntegers, initialize=m) # number of cold streams

	model.H = RangeSet(0, model.n-1) # set of hot streams
	model.C = RangeSet(0, model.m-1) # set of cold streams

	model.M = Set(within=model.H*model.C, initialize=M)

	# Parameter: heat load of hot stream i in temperature interval t 
	model.h = Param(model.H, within=NonNegativeReals, initialize=lambda model, i: h[i])
	
	# Parameter: heat load of cold stream j in temperature interval t
	model.c = Param(model.C, within=NonNegativeReals, initialize=lambda model, j: c[j]) 

	# Variable: heat transferred from i to j
	model.q = Var(model.H, model.C, within=NonNegativeReals)

	# Objective: minimization of the total fraction
	def total_heat_rule(model):
		return sum(model.q[i,j] for (i,j) in model.M)
	model.total_heat = Objective(rule=total_heat_rule, sense=maximize)

	#Constraint: heat conservation of hot streams
	def hot_supply_rule(model, i):
		return sum(model.q[i,j] for j in model.C) <= model.h[i]
	model.hot_supply_constraint = Constraint(model.H, rule=hot_supply_rule)

	#Constraint: heat conservation of cold streams
	def cold_demand_rule(model, j):
		return sum(model.q[i,j] for i in model.H) <= model.c[j]
	model.cold_demand_constraint = Constraint(model.C, rule=cold_demand_rule)

	solver = 'cplex'
	opt = SolverFactory(solver)
	opt.options['threads'] = 1
	LP = model.create_instance()
	results = opt.solve(LP)

	q=[[LP.q[i,j].value for j in range(m)] for i in range(n)]

	return q






# Given the heat loads of hot and cold streams in a single temperature interval,
# it computes a solution with a small number of matches greedily.
def mip_single_temperature_interval(n, m, QH, QC, u):
	
	# Local copy of the instance.
	h = list([QH[i][u] for i in range(n)])
	c = list([QC[j][u] for j in range(m)])
	
	Hu = [] # Hot streams with positive heat load
	Cu = [] # Cold streams with positive heat load
	
	for i in range(n):
		if h[i] < epsilon:
			h[i] = 0
		else:
			Hu.append(i) 
	
	for j in range(m):
		if c[j] < epsilon:
			c[j] = 0
		else:
			Cu.append(j)
	
	#print(h)
	#print(c)

	model = AbstractModel()

	model.n = Param(within=NonNegativeIntegers, initialize=n) # number of hot streams
	model.m = Param(within=NonNegativeIntegers, initialize=m) # number of cold streams
	model.b = Param(within=NonNegativeIntegers, initialize=min(n,m)) # number of bins

	model.H = RangeSet(0, model.n-1) # set of hot streams
	model.C = RangeSet(0, model.m-1) # set of cold streams
	model.B = RangeSet(0, model.b-1) # set of bins
	
	model.Hu = Set(within=model.H, initialize=Hu)
	model.Cu = Set(within=model.C, initialize=Cu)

	# Parameter: heat load of hot stream i in temperature interval t 
	model.h = Param(model.Hu, within=NonNegativeReals, initialize=lambda model, i: h[i])
	
	# Parameter: heat load of cold stream j in temperature interval t
	model.c = Param(model.Cu, within=NonNegativeReals, initialize=lambda model, j: c[j]) 

	# Variable: indicating whether bin b is used
	model.x = Var(model.B, within=Binary)
	
	# Variable: indicating whether hot stream i is placed into bin b 
	model.y = Var(model.Hu, model.B, within=Binary)
	
	# Variable: indicating whether cold stream j is placed into bin b 
	model.z = Var(model.Cu, model.B, within=Binary)

	# Objective: number of bins
	def number_of_bins_rule(model):
		return sum(model.x[b] for b in model.B)
	model.number_of_bins_obj = Objective(rule=number_of_bins_rule, sense=maximize)
	
	#Constraint: bin usage by hot streams
	def bin_not_used_rule(model, b):
		return model.x[b] <= sum(model.z[j,b] for j in model.Cu)
	model.bin_not_used_constraint = Constraint(model.B, rule=bin_not_used_rule)

	#Constraint: assignment of each hot stream
	def hot_assignment_rule(model, i):
		return sum(model.y[i,b] for b in model.B) <= 1
	model.hot_assignment_rule = Constraint(model.Hu, rule=hot_assignment_rule)

	#Constraint: assignment of each hot stream
	def cold_assignment_rule(model, j):
		return sum(model.z[j,b] for b in model.B) == 1
	model.cold_assignment_rule = Constraint(model.Cu, rule=cold_assignment_rule)
	
	#Constraint: heat conservation
	def heat_conservation_rule(model, b):
		return sum(model.y[i,b]*model.h[i] for i in model.Hu) >= sum(model.z[j,b]*model.c[j] for j in model.Cu)
	model.heat_conservation_rule = Constraint(model.B, rule=heat_conservation_rule)

	solver = 'cplex'
	opt = SolverFactory(solver)
	opt.options['threads'] = 1
	MIP = model.create_instance()
	results = opt.solve(MIP)
	
	#print(results)
	
	#for b in range(min(n,m)):
		#print(MIP.x[b].value)
	
	bins = []
	
	for b in range(min(n,m)):
		
		hot_streams = []
		cold_streams = []
		
		for i in Hu:
			if MIP.y[i,b].value > epsilon:
				#print('H'+str(i)+' in B'+str(b))
				hot_streams.append(i)
		for j in Cu:
			if MIP.z[j,b].value > epsilon:
				#print('C'+str(j)+' in B'+str(b))
				cold_streams.append(j)
		
		if cold_streams != []:
			bins.append((list(hot_streams),list(cold_streams)))
	
	#print(bins)
	
	q = [[0 for j in range(m)] for i in range(n)]
	
	for (H,C) in bins:
		i = 0
		j = 0
		while i <= len(H) and j < len(C):
			
			hot_heat = h[ H[i] ]
			cold_heat =  c[ C[j] ]
			
			temp_q = min(hot_heat, cold_heat)
			q[ H[i] ][ C[j] ] += temp_q
			h[ H[i] ] -= temp_q
			c[ C[j] ] -= temp_q
			
			if h[ H[i] ] < epsilon:
				i += 1
			if c[ C[j] ] < epsilon:
				j += 1
				
	#print(q)
	
	return q
      
def equality(a,b):
	return a < b + epsilon and a > b - epsilon