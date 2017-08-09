from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from time import time
from ...problem_classes.heat_exchange import Heat_Exchange

epsilon = 10**(-7)

def water_filling_greedy(inst):
	
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
	  
		
		if len(M) > 0:
			current_q = max_heat(n, m, QH, QC, u, M)
			for i in range(n):
				for j in range(m):
					if current_q[i][j] > epsilon:
						q[i][j][u] += current_q[i][j]
						QH[i][u] -= current_q[i][j]
						QC[j][u] -= current_q[i][j]
						#print('Re-use H' + str(i) + ' to C' + str(j) + ': ' + str(current_q[i][j]))
						#raw_input()
		
		current_q = greedy_single_temperature_interval(n, m, QH, QC, u)
		# print(sum(current_q[i][j] for i in range(n) for j in range(m)))
		
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

	total_heat = results.problem.upper_bound
	q=[[LP.q[i,j].value for j in range(m)] for i in range(n)]

	return q






# Given the heat loads of hot and cold streams in a single temperature interval,
# it computes a solution with a small number of matches greedily.
def greedy_single_temperature_interval(n, m, QH, QC, u):
	
	# Local copy of the instance.
	h = list([QH[i][u] for i in range(n)])
	c = list([QC[j][u] for j in range(m)])
	
	# Vector of heat exchanges.
	q = [[0 for j in range(m)] for i in range(n)]
	
	# Set of matches.
	M = []
	
	# Initially, all equal streams are matched.
	for i in range(n):
		for j in range(m):
			temp_q = h[i]
			if equality(h[i],c[j]) and temp_q > epsilon:
				q[i][j] += temp_q
				h[i] = 0
				c[j] = 0
	
	sorted_H = sorted_indices(h)
	sorted_C = sorted_indices(c)
	
	#print(sorted_H)
	#print(sorted_C)
	#raw_input()
	
	##sorted_H = [h.index(heat) for heat in sorted(h)]
	##sorted_C = [c.index(heat) for heat in sorted(c)]
	
	#for i in sorted_H:
		#for j in sorted_C:
			#temp_q = min(h[i], c[j])
			#if temp_q > epsilon:
				#q[i][j] += temp_q
				#h[i] -= temp_q
				#c[j] -= temp_q
				
	
	i = 0
	j = 0
	while i < n and j < m:
	  
		hot_heat = h[ sorted_H[i] ]
		cold_heat =  c[ sorted_C[j] ]
	
		temp_q = min(hot_heat, cold_heat)
		q[ sorted_H[i] ][ sorted_C[j] ] += temp_q
		h[ sorted_H[i] ] -= temp_q
		c[ sorted_C[j] ] -= temp_q
		
		if h[ sorted_H[i] ] < epsilon:
			i += 1
		if c[ sorted_C[j] ] < epsilon:
			j += 1
	
	#i = 0
	#j = 0
	#while i < n and j < m:
		#hot_heat = h[i]
		#cold_heat =  c[j]
		#temp_q = min(hot_heat, cold_heat)
		#q[i][j] += temp_q
		#h[i] -= temp_q
		#c[j] -= temp_q
		#if h[i] < epsilon:
			#i += 1
		#if c[j] < epsilon:
			#j += 1
	
			
	#for i in range(n):
		#for j in range(m):
			#temp_q = min(h[i], c[j])
			#if temp_q > epsilon:
				#q[i][j] += temp_q
				#h[i] -= q[i][j]
				#c[j] -= q[i][j]

	return q
      
def equality(a,b):
	return a < b + epsilon and a > b - epsilon
      
def sorted_indices(L):
	
	sorted_L = []
	
	for it in range(len(L)): # number of iterations
		
		next_val = - float('inf')
		
		for i in range(len(L)):
			if i not in sorted_L: # indices are unique
				if L[i] > next_val:
					next_i = i
					next_val = L[i]
		
		sorted_L.append(next_i)
		
	return sorted_L