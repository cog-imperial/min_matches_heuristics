from __future__ import division
from fractional_relaxation import solve_fractional_relaxation

def lp_rounding(inst):

	epsilon=10**(-7)
	lamda = [[0 for j in range(inst.m)] for i in range(inst.n)]

	for i in range(inst.n):
		for j in range(inst.m):
			if inst.U[i][j] > epsilon:
				lamda[i][j] = 1 / inst.U[i][j]
			else:
				lamda[i][j] = float('inf')

	(sol, elapsed_time, relaxation_value) = solve_fractional_relaxation(inst,lamda)

	return (sol, elapsed_time)


