from __future__ import division
from ...problem_classes.heat_exchange import *
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Helper for precision issues
epsilon = 0.0000001  

def solve_fractional_relaxation(inst,lamda):
	
	# Local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC) 
 
	# Fixing precision errors
	for i in range(inst.n):
		for s in range(inst.k):
			if QH[i][s] < epsilon:
				QH[i][s] = 0
	
	for j in range(inst.m):
		for t in range(inst.k):
			if QC[j][t] < epsilon:
				QC[j][t] = 0
	
	# Computation of heat residuals
	R = [sum(QH[i][s] for i in range(n) for s in range(u+1))-sum(QC[j][t] for j in range(m) for t in range(u+1)) for u in range(k)]
	for u in range(k): 
		if R[u]<0 : R[u]=0

	(A,VH,VC) = valid_quadruples_set(n,m,k,QH,QC,R)

	model = AbstractModel()

	model.n = Param(within=NonNegativeIntegers, initialize=n) # number of hot streams
	model.m = Param(within=NonNegativeIntegers, initialize=m) # number of cold streams
	model.k = Param(within=NonNegativeIntegers, initialize=k) # number of temperature intervals

	model.H = RangeSet(0, model.n-1) # set of hot streams
	model.C = RangeSet(0, model.m-1) # set of cold streams
	model.T = RangeSet(0, model.k-1) # set of temperature intervals

	model.A = Set(within=model.H*model.T*model.C*model.T, initialize=A) # set of valid quadruples (arcs)  
	model.VH = Set(within=model.H*model.T, initialize=VH) # set of valid hot pairs (vertices)  
	model.VC = Set(within=model.C*model.T, initialize=VC) # set of valid cold pairs (vertices)

	# Parameter: heat load of hot stream i in temperature interval t 
	model.QH = Param(model.VH, within=NonNegativeReals, initialize=lambda model, i, s: QH[i][s])
	
	# Parameter: heat load of cold stream j in temperature interval t
	model.QC = Param(model.VC, within=NonNegativeReals, initialize=lambda model, j, t: QC[j][t]) 
	
	# Parameter: fractional cost values
	model.lamda = Param(model.H, model.C, within=NonNegativeReals, initialize=lambda model, i, j: lamda[i][j]) 

	# Variable: heat transferred from (i,s) to (j,t)
	model.q = Var(model.A, within=NonNegativeReals)

	# Objective: minimization of the cost of the network flow
	def min_cost_flow_objective_rule(model):
		return sum(model.lamda[i,j]*model.q[i,s,j,t] for (i,s,j,t) in model.A)
	model.obj_value = Objective(rule=min_cost_flow_objective_rule, sense=minimize)

	#Constraint: heat conservation of hot streams
	def hot_supply_rule(model, i, s):
		return sum(model.q[temp_i,temp_s,j,t] for (temp_i,temp_s,j,t) in model.A if temp_i==i and temp_s==s) == model.QH[i,s]
	model.hot_supply_constraint = Constraint(model.VH, rule=hot_supply_rule)

	#Constraint: heat conservation of cold streams
	def cold_demand_rule(model, j, t):
		return sum(model.q[i,s,temp_j,temp_t] for (i,s,temp_j,temp_t) in model.A if temp_j==j and temp_t==t) == model.QC[j,t]
	model.cold_demand_constraint = Constraint(model.VC, rule=cold_demand_rule)

	solver = 'cplex'
	opt = SolverFactory(solver)
	opt.options['threads'] = 1
	LP = model.create_instance()
	results = opt.solve(LP)
	elapsed_time = results.solver.time

	# Problem variables
	y=[[0 for j in range(inst.m)] for i in range(inst.n)]
	q=[[[[0 for t in range(inst.k)] for j in range(inst.m)] for s in range(inst.k)] for i in range(inst.n)]
	
	for (i,s,j,t) in A:
		if LP.q[i,s,j,t].value > epsilon:
			q[i][s][j][t] = LP.q[i,s,j,t].value
			y[i][j] = 1

	matches=sum(sum(y[i]) for i in range(inst.n))
	
	sol=Heat_Exchange('relaxation_rounding',inst.n,inst.m,inst.k,matches,y,q)
	
	relaxation_value = results.problem.lower_bound
	
	return (sol, elapsed_time, relaxation_value)

# It computes the set A of valid quadruples which is required for building the min cost flow LP model.
# A set M of matches is passed as parameter.
def valid_quadruples_set(n,m,k,QH,QC,R):
	
	A = [] # quadruples (i,s,j,t)
	VH = [] # vertices (i,s)
	VC = [] # vertices (j,t)
	
	for i in range(n):
		for j in range(m):
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
	return (A,VH,VC)
      
def fractional_relaxation_lower_bound(inst): # inst is a network
	
	epsilon=10**(-7)
	lamda = [[0 for j in range(inst.m)] for i in range(inst.n)]

	for i in range(inst.n):
		for j in range(inst.m):
			if inst.U[i][j] > epsilon:
				lamda[i][j] = 1 / inst.U[i][j]
			else:
				lamda[i][j] = float('inf')
				
	(sol, elapsed_time, relaxation_value) = solve_fractional_relaxation(inst,lamda)
	
	return relaxation_value