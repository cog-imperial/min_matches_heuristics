from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from time import time
from ...problem_classes.heat_exchange import Heat_Exchange
from covering_relaxation import solve_covering_relaxation

# Helper for precision issues
epsilon = 10**(-7)

def cr_rounding(inst):
  
	# Local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC)
	
	# Computation of heat residuals
	R = [sum(QH[i][s] for i in range(n) for s in range(u+1)) - sum(QC[j][t] for j in range(m) for t in range(u+1)) for u in range(k)]
	for u in range(k): 
		if R[u]<0 : 
			R[u]=0
	
	# Problem variables
	y = [[0 for j in range(m)] for i in range(n)]
	q = [[[[0 for t in range(k)] for j in range(m)] for s in range(k)] for i in range(n)]
	
	# Set of matches
	M=[]
	
	# Variable for termination
	remaining_heat = sum(sum(QH[i]) for i in range(n))
	
	# Timer
	start_time = time()
	
	iterations = 0
	
	# Termination criterion: zero remaining heat
	while remaining_heat > epsilon: 
		
		h = [sum(QH[i]) for i in range(n)]
		c = [sum(QC[j]) for j in range(m)]
		
		U = [[pairwise_max_heat(i,j,k,QH[i],QC[j],R) for j in range(m)] for i in range(n)]
		
		for i in range(n):
			for j in range(m):
				if U[i][j] < epsilon:
					U[i][j] = 0
		
		y = solve_covering_relaxation(n,m,h,c,U)
		
		#print(y)
		
		for i in range(n):
			for j in range(m):
				if y[i][j] == 1:
					if (i,j) not in M:
						M.append((i,j))
		
		(new_heat,new_q) = max_heat(n,m,k,QH,QC,R,M)
		
		#print(new_heat)
		
		for i in range(n):
			for j in range(m):
				for s in range(k):
					for t in range(k):
						if new_q[i][s][j][t] > epsilon:
							
							q[i][s][j][t] += new_q[i][s][j][t]
							
							QH[i][s] -= new_q[i][s][j][t]
							if QH[i][s] < 0: 
								QH[i][s] = 0
							
							QC[j][t] -= new_q[i][s][j][t]
							if QC[j][t] < 0: 
								QC[j][t] = 0
							
							for u in range(k):
								if s <= u and u < t:
									R[u] -= new_q[i][s][j][t]
									if R[u] < epsilon:
										R[u] = 0
		
		remaining_heat = sum(sum(QH[i]) for i in range(n))
	
	end_time = time()
	elapsed_time = end_time-start_time
	
	y = [[0 for j in range(m)] for i in range(n)]
	
	for i in range(n):
		for j in range(m):
			for s in range(k):
				for t in range(k):
					if q[i][s][j][t]:
						y[i][j] = 1
	
	matches = sum(sum(y[i]) for i in range(n))
	
	sol = Heat_Exchange('relaxation_rounding',n,m,k,matches,y,q)
	
	return (sol, elapsed_time)

      
# It computes the maximum heat that can be exchanged between i and j
# with heat vectors QH and QC, respectively.
def pairwise_max_heat(i,j,k,QH,QC,R):
  
	# Initialization to avoid modifying the global copies
	QH = list(QH)
	QC = list(QC)
	R = list(R)
	
	# Initialization of the heat exchanges
	# q[s][t]: heat exchanged between (i,s) and (j,t)
	q = [[0 for t in range(k)] for s in range(k)]
	
	# Initialization of the maximum heat exchanged between i and j
	total_heat = 0
	
	# Heat exchanged in the same temperature interval
	for t in range(k):
		q[t][t] = min(QH[t],QC[t])
		QH[t] -= q[t][t]
		QC[t] -= q[t][t]
		total_heat += q[t][t]
	
	# Heat exchanged in different temperature intervals
	for s in range(k):
		for t in range(s+1,k):
			q[s][t] = min(QH[s],QC[t],min(R[s:t]))
			QH[s] -= q[s][t]
			QC[t] -= q[s][t]
			for u in range(s,t):
				R[u] -= q[s][t]
			total_heat += q[s][t]
			
	#return (total_heat,q,R)
	return total_heat

# Given a subset of matches M, it computes the maximum (total) heat that can be transferred using only the matches in M.
# This computation is accomplished by solving a linear program.
def max_heat(n,m,k,QH,QC,R,M):

	(A,VH,VC,AT) = valid_quadruples_set(k,QH,QC,R,M)
	
	if len(A) == 0:
		total_fraction = 0
		q=[[[[0 for t in range(k)] for j in range(m)] for ti in range(k)] for i in range(n)]
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
