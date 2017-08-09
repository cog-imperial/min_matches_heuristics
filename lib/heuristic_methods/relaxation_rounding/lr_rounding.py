from __future__ import division
from fractional_relaxation import solve_fractional_relaxation
from lp_rounding import lp_rounding

def lr_rounding(inst):

	(sol, elapsed_time) = lp_rounding(inst)
	
	epsilon=10**(-7)
	
	# Total heat excahnger between each pair of streams in the LP rounding solution.
	Q = [[sum(sol.q[i][s][j][t] for s in range(inst.k) for t in range(inst.k)) for j in range(inst.m)] for i in range(inst.n)]
	lamda = [[0 for j in range(inst.m)] for i in range(inst.n)]

	for i in range(inst.n):
		for j in range(inst.m):
			if Q[i][j] > epsilon:
				lamda[i][j] = 1 / Q[i][j]
			elif inst.U[i][j] > epsilon:
				lamda[i][j] = 1 / inst.U[i][j]
			else:
				lamda[i][j] = float('inf')

	(sol, elapsed_time, relaxation_value) = solve_fractional_relaxation(inst,lamda)

	return (sol, elapsed_time)
