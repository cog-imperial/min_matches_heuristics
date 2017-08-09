from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from ..problem_classes.network import Network

# Given an object of Transshipment_LP, it solves the corresponding LP.
# It computes the heat of each utility and the residual heat, per interval, 
# so that the cost is minimized and the heat load conservation is ensured.
# The values of the following unknown variables are computed:
# QHU[i,t]: heat supplied by hot utility i in temperature interval t
# QCU[j,t]: heat absorbed by cold utility j in temperature interval t
# R[t]: residual heat entering temperature interval t
def solve_transshipment_lp(test_set, test_id, solver, inst, min_utility_inst): # inst is the transshipment instance

	model = AbstractModel()
	
	model.ns = Param(within=NonNegativeIntegers, initialize=inst.ns) # number of hot streams
	model.ms = Param(within=NonNegativeIntegers, initialize=inst.ms) # number of cold streams
	model.nu = Param(within=NonNegativeIntegers, initialize=inst.nu) # number of hot utilities
	model.mu = Param(within=NonNegativeIntegers, initialize=inst.mu) # number of cold utilities
	model.k = Param(within=NonNegativeIntegers, initialize=inst.k) # number of temperature intervals
	
	model.HS = RangeSet(0, model.ns-1) # set of hot streams
	model.CS = RangeSet(0, model.ms-1) # set of cold streams
	model.HU = RangeSet(0, model.nu-1) # set of hot utilities
	model.CU = RangeSet(0, model.mu-1) # set of cold utilities
	model.TI = RangeSet(0, model.k-1) # set of temperature intervals
	
	# Parameter: amount of heat load from hot utility i to temperature interval t
	model.QHS = Param(model.HS, model.TI, within=NonNegativeReals, initialize=lambda model, i, t: inst.QHS[i][t]) 
	
	# Parameter: amount of heat load to cold utility j to temperature interval t
	model.QCS = Param(model.CS, model.TI, within=NonNegativeReals, initialize=lambda model, j, t: inst.QCS[j][t])  
	
	# Parameter: set of forbidden hot utility temperature interval pairs (i,t)
	model.forbiddenHUTI = Set(within=model.HU*model.TI, initialize=inst.forbiddenHUTI)  
	
	#Parameter: set of forbidden cold utility temperature interval pairs (j,t)
	model.forbiddenCUTI = Set(within=model.CU*model.TI, initialize=inst.forbiddenCUTI)  
    
	# Parameter: cost of hot utility i
	model.costHU = Param(model.HU, within=NonNegativeReals, initialize=lambda model, i: inst.costHU[i])    
    
	# Parameter: cost of cold utility j
	model.costCU = Param(model.CU, within=NonNegativeReals, initialize=lambda model, j: inst.costCU[j]) 
    
	# Variable: heat of hot stream i in temperature interval t 
	model.QHU = Var(model.HU, model.TI, within=NonNegativeReals)

	# Variable: heat load of cold stream j in temperature interval t
	model.QCU = Var(model.CU, model.TI, within=NonNegativeReals)  
	
	# Variable: residual heat entering temperature interval t and corresponding sets
	model.Rset = RangeSet(0, model.k) # set of residuals
	model.Rzero = Set(within=model.Rset, initialize=inst.zero_residuals) # set with first and last residual
	model.R = Var(model.Rset, within=NonNegativeReals)  
	
	# Variable: heat load of cold stream j in temperature interval t
	model.cost = Var(within=NonNegativeReals)

	# Objective: minimization of the utility cost
	def utility_cost_rule(model):
		#total_HU_cost = sum( model.costHU[i] * sum( model.QHU[i,t] for t in model.TI ) for i in model.HU)
		#total_CU_cost = sum( model.costCU[j] * sum( model.QCU[j,t] for t in model.TI ) for j in model.CU)
		#model.cost = total_HU_cost + total_CU_cost
		return model.cost
	model.utility_cost = Objective(sense=minimize, rule=utility_cost_rule)
	
	# Constraint: utility cost computation
	def utility_cost_computation_rule(model):
		total_HU_cost = sum( model.costHU[i] * sum( model.QHU[i,t] for t in model.TI ) for i in model.HU)
		total_CU_cost = sum( model.costCU[j] * sum( model.QCU[j,t] for t in model.TI ) for j in model.CU)
		return model.cost == total_HU_cost + total_CU_cost
	model.utility_cost_constraint = Constraint(rule=utility_cost_computation_rule)

	# Constraint: energy conservation
	def conservation_rule(model, t):
		entering_energy = sum(model.QHS[i,t] for i in model.HS) + sum(model.QHU[i,t] for i in model.HU) + model.R[t]
		exiting_energy = sum(model.QCS[j,t] for j in model.CS) + sum(model.QCU[j,t] for j in model.CU) + model.R[t+1]
		return entering_energy == exiting_energy
	model.conservation_constraint = Constraint(model.TI, rule=conservation_rule)
	
	# Constraint: forbidden temperature interval of a hot utility
	def forbidden_hot_rule(model, i, t):
		return model.QHU[i,t]==0
	model.forbidden_hot_constraint = Constraint(model.forbiddenHUTI, rule=forbidden_hot_rule)
    
	# Constraint: forbidden temperature interval of a cold utility
	def forbidden_cold_rule(model, j, t):
		return model.QCU[j,t]==0
	model.forbidden_cold_constraint = Constraint(model.forbiddenCUTI, rule=forbidden_cold_rule)
	
	# Constraint: the residual heat entering the first temperature interval and the one exiting the last temperature interval must be zero.
	def zero_residual_rule(model, t):
		return model.R[t]==0
	model.zero_residual_constraint = Constraint(model.Rzero, rule=zero_residual_rule)
	
	opt = SolverFactory(solver)
	#opt.options['logfile'] = 'test_cases/mip_instances/'+test_set+'/'+test_id+'_'+solver+'.log'
	lp_instance = model.create_instance()
	results = opt.solve(lp_instance)
	#lp_instance.load(results)
	
	cost = lp_instance.cost.value
	QHU=[[lp_instance.QHU[i,t].value for t in range(inst.k)] for i in range(inst.nu)]
	QCU=[[lp_instance.QCU[j,t].value for t in range(inst.k)] for j in range(inst.mu)]
	R=[lp_instance.R[t].value for t in range(inst.k+1)]
	
	network = Network(cost, inst.ns, inst.ms, inst.nu, inst.mu, inst.k, inst.QHS, inst.QCS, QHU, QCU, R, min_utility_inst)
	
	return network

