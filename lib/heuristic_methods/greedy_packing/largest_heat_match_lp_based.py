from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from time import time
from ...problem_classes.heat_exchange import Heat_Exchange

# Helper for precision issues
epsilon = 10**(-7)

def largest_heat_match_lp_based(inst):
  
	# Local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC)
	
	# Computation of heat residuals
	R = [sum(QH[i][s] for i in range(n) for s in range(u+1))-sum(QC[j][t] for j in range(m) for t in range(u+1)) for u in range(k)]
	for u in range(k): 
		if R[u]<0 : R[u]=0
	
	# Problem variables
	y = [[0 for j in range(m)] for i in range(n)]
	q = [[[[0 for t in range(k)] for j in range(m)] for s in range(k)] for i in range(n)]
	
	# Resulting set of matches
	M=[]
	
	# Variables for termination
	total_heat = sum(sum(QH[i]) for i in range(n))
	remaining_heat = total_heat
	
	# Timer
	start_time = time()
	
	# Termination criterion: zero remaining heat
	while remaining_heat > epsilon: 
	  
		# Largest heat match of the iteration
		matched_i = -1
		matched_j = -1
		
		# Computation of the largest heat match
		for i in range(n):
			for j in range(m):
				if (i,j) not in M:
					
					(new_heat,new_q) = max_heat(n,m,k,QH,QC,R,M+[(i,j)])
					
					if new_heat > total_heat - remaining_heat:  
						(matched_i,matched_j) = (i,j)
						remaining_heat = total_heat - new_heat
						q = new_q
						
		M += [(matched_i,matched_j)]
		
	end_time = time()
	elapsed_time = end_time-start_time
	
	matches = 0
	
	for i in range(n):
		for j in range(m):
			if (i,j) in M:
				y[i][j] = 1
				matches += 1
			else:
				y[i][j] = 0
	
	sol = Heat_Exchange('greedy_packing',n,m,k,matches,y,q)
	
	return (sol, elapsed_time)


# Given a subset of matches M, it computes the maximum (total) heat that can be transferred using only the matches in M.
# This computation is accomplished by solving a linear program.
def max_heat(n,m,k,QH,QC,R,M):

	(A,VH,VC,AT) = valid_quadruples_set(k,QH,QC,R,M)
	
	if len(A) == 0:
		total_fraction = 0
		q=[[[[0 for t in range(k)] for j in range(m)] for ti in range(k)] for i in range(n)]
		Q=[[0 for j in range(m)] for i in range(n)]
		return (total_fraction,q)

	model = AbstractModel()

	model.n = Param(within=NonNegativeIntegers, initialize=n) # number of hot streams
	model.m = Param(within=NonNegativeIntegers, initialize=m) # number of cold streams
	model.k = Param(within=NonNegativeIntegers, initialize=k) # number of temperature intervals

	model.H = RangeSet(0, model.n-1) # set of hot streams
	model.C = RangeSet(0, model.m-1) # set of cold streams
	model.T = RangeSet(0, model.k-1) # set of temperature intervals

	model.M = Set(within=model.H*model.C, initialize=M)
	model.A = Set(within=model.H*model.T*model.C*model.T, initialize=A) # set of valid quadruples (arcs)  
	model.VH = Set(within=model.H*model.T, initialize=VH) # set of valid hot pairs (vertices)  
	model.VC = Set(within=model.C*model.T, initialize=VC) # set of valid cold pairs (vertices)
	model.AT = Set(within=model.T, initialize=AT) # set of active heat residuals

	# Parameter: heat load of hot stream i in temperature interval t 
	model.QH = Param(model.VH, within=NonNegativeReals, initialize=lambda model, i, s: QH[i][s])
	
	# Parameter: heat load of cold stream j in temperature interval t
	model.QC = Param(model.VC, within=NonNegativeReals, initialize=lambda model, j, t: QC[j][t]) 

	# Parameter: heat load of hot stream i 
	model.h = Param(model.H, within=NonNegativeReals, initialize=lambda model, i: sum(QH[i]))

	# Parameter: heat load of cold stream j
	model.c = Param(model.C, within=NonNegativeReals, initialize=lambda model, j: sum(QC[j]))

	# Parameter: heat load of cold stream j in temperature interval t
	model.R = Param(model.AT, within=NonNegativeReals, initialize=lambda model, t: R[t]) 

	# Variable: heat transferred from (i,s) to (j,t)
	model.q = Var(model.A, within=NonNegativeReals)

	# Objective: minimization of the total fraction
	def total_heat_rule(model):
		return sum(model.q[i,s,j,t] for (i,s,j,t) in model.A)
	model.total_heat = Objective(rule=total_heat_rule, sense=maximize)

	#Constraint: heat conservation of hot streams
	def hot_supply_rule(model, i, s):
		return sum(model.q[temp_i,temp_s,j,t] for (temp_i,temp_s,j,t) in model.A if temp_i==i and temp_s==s) <= model.QH[i,s]
	model.hot_supply_constraint = Constraint(model.VH, rule=hot_supply_rule)

	#Constraint: heat conservation of cold streams
	def cold_demand_rule(model, j, t):
		return sum(model.q[i,s,temp_j,temp_t] for (i,s,temp_j,temp_t) in model.A if temp_j==j and temp_t==t) <= model.QC[j,t]
	model.cold_demand_constraint = Constraint(model.VC, rule=cold_demand_rule)
	
	#Constraint: heat conservation of cold streams
	def residual_feasibility_rule(model, u):
		return sum(model.q[i,s,j,t] for (i,s,j,t) in model.A if s<=u and t>u) <= model.R[u]
	model.residual_feasibility_constraint = Constraint(model.AT, rule=residual_feasibility_rule)

	solver = 'cplex'
	opt = SolverFactory(solver)
	opt.options['threads'] = 1
	LP = model.create_instance()
	results = opt.solve(LP)

	total_heat = results.problem.upper_bound
	q=[[[[0 for t in range(k)] for j in range(m)] for ti in range(k)] for i in range(n)]
	for (i,s,j,t) in A:
		q[i][s][j][t] = LP.q[i,s,j,t].value

	return (total_heat,q)

# It computes the set A of valid quadruples which is required for building the maximum fraction LP model.
# A set M of matches is passed as parameter.
def valid_quadruples_set(k,QH,QC,R,M):
	
	A = [] # quadruples (i,s,j,t)
	VH = [] # vertices (i,s)
	VC = [] # vertices (j,t)
	AT = [] # active temperature interval residuals, affected residual capacities of temperature intervals
	for (i,j) in M:
		for s in range(k):
			for t in range(k):
				
				zero_residual = False
				for u in range(s,t):
					if R[u] == 0:
						zero_residual = True
				
				if s <= t and QH[i][s] > epsilon and QC[j][t] > epsilon and not zero_residual:
					A.append((i,s,j,t))
					
					if (i,s) not in VH:
						VH.append((i,s))
						
					if (j,t) not in VC:
						VC.append((j,t))
						
					for u in range(s,t):
						if u not in AT:
							AT.append(u)
	return (A,VH,VC,AT)
