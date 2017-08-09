from __future__ import division
from time import time
from ...problem_classes.heat_exchange import Heat_Exchange

def largest_fraction_match(inst):
  
	# Initialization of a local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC)
	R = list(inst.R)
	
	# Initialization of lists for storing the solution
	y = [[0 for j in range(m)] for i in range(n)]
	q = [[[[0 for t in range(k)] for j in range(m)] for s in range(k)] for i in range(n)]
	M = []
	
	# The entire heat loads of the streams.
	h = [sum(QH[i]) for i in range(n)]
	c = [sum(QC[j]) for j in range(m)]
	
	# Termination criterion: zero remaining heat
	remaining_fraction = n + m
	
	# Helper for dealing with precision issues
	epsilon = 10**(-7)
	
	# Algorithm's timer
	start_time = time()
	
	while remaining_fraction > epsilon:
		
		# Storing the new match
		matched_i = -1
		matched_j = -1
		
		# Heat exchanges between the new matched pair of streams
		# q[s][t] specifies the heat exchange between (matched_i,s) and (matched_j,t)
		matched_q = [[0 for t in range(k)] for s in range(k)]
		
		# Storing the maximum fraction in the remaining instance
		matched_fraction = 0
		
		# The new heat residuals after performing the above heat exchanges.
		resulting_R = list(R)
		
		# For each pair (i,j), compute the one with the maximum fraction
		for i in range(n):
			for j in range(m):
				if (i,j) not in M and sum(QH[i]) > 0 and sum(QC[j]) > 0:
					
						# Compute the covered fraction of (i,j)
						(matched_heat,temp_q,temp_R)=max_heat(i,j,k,QH[i],QC[j],R)
						fraction = matched_heat / h[i] + matched_heat / c[j]
				
						if fraction - matched_fraction > epsilon:
							matched_i = i
							matched_j = j
							matched_q = temp_q
							resulting_R = temp_R
							matched_fraction = fraction
		
		# Introduction of the new match
		M.append((matched_i,matched_j))
		y[matched_i][matched_j]=1
		
		for s in range(k):
			for t in range(k):
				q[matched_i][s][matched_j][t] = matched_q[s][t]
				QH[matched_i][s] -= matched_q[s][t]
				QC[matched_j][t] -= matched_q[s][t]
		R=resulting_R
		
		remaining_fraction -= matched_fraction 
		
	end_time = time()
	elapsed_time = end_time - start_time
	
	matches = sum(sum(y[i]) for i in range(n))
	
	sol = Heat_Exchange('greedy_packing',n,m,k,matches,y,q)
	
	return (sol, elapsed_time)


# It computes the maximum heat that can be exchanged between i and j
# with heat vectors QH and QC, respectively.
def max_heat(i,j,k,QH,QC,R):
  
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
			q[s][t] = min(QH[s],QC[t],min(R[s+1:t+1]))
			QH[s] -= q[s][t]
			QC[t] -= q[s][t]
			for u in range(s+1,t+1):
				R[u] -= q[s][t]
			total_heat += q[s][t]
			
	return (total_heat,q,R)