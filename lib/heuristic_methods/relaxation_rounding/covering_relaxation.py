from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory

epsilon = 10**(-7)

def solve_covering_relaxation(n,m,h,c,U):
	
	model = AbstractModel()
	
	model.n = Param(within=NonNegativeIntegers, initialize=n) # number of hot streams
	model.m = Param(within=NonNegativeIntegers, initialize=m) # number of cold streams
	
	model.H = RangeSet(0, model.n-1) # set of hot streams
	model.C = RangeSet(0, model.m-1) # set of cold streams
	
	# Parameter: heat load of hot stream i
	model.h = Param(model.H, within=NonNegativeReals, initialize=lambda model, i: h[i])
	
	# Parameter: heat load of cold stream j
	model.c = Param(model.C, within=NonNegativeReals, initialize=lambda model, j: c[j]) 
	
	# Parameter: upper bounds
	model.U = Param(model.H, model.C, within=NonNegativeReals, initialize=lambda model, i, j: U[i][j])
	
	# Parameter: matches
	model.y = Var(model.H, model.C, within=Binary)
	
	# Objective: minimization of the number of matches
	def min_matches_rule(model):
		return sum(model.y[i,j] for i in model.H for j in model.C)
	model.obj_value = Objective(rule=min_matches_rule, sense=minimize)
	
	#Constraint: hot streams covering
	def hot_supply_rule(model, i):
		if model.h[i] > epsilon:
			return sum(model.y[i,j]*model.U[i,j] for j in model.C) >= model.h[i]
		else:
			return Constraint.Skip
	model.hot_supply_constraint = Constraint(model.H, rule=hot_supply_rule)
	
	#Constraint: cold streams covering
	def cold_demand_rule(model, j):
		if model.c[j] > epsilon:
			return sum(model.y[i,j]*model.U[i,j] for i in model.H) >= model.c[j]
		else:
			return Constraint.Skip
	model.cold_demand_constraint = Constraint(model.C, rule=cold_demand_rule)
	
	solver = 'cplex'
	opt = SolverFactory(solver)
	opt.options['threads'] = 1
	LP = model.create_instance()
	results = opt.solve(LP)
	elapsed_time = results.solver.time
	
	y=[[LP.y[i,j].value for j in range(m)] for i in range(n)]
	
	return y