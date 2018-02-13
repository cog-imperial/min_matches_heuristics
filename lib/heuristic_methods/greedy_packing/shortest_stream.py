from time import time
from ...problem_classes.heat_exchange import Heat_Exchange

def shortest_stream(inst):
	
	# Initialization of a local copy of the instance
	n = inst.n
	m = inst.m
	k = inst.k
	QH = list(inst.QH)
	QC = list(inst.QC)
	R = list(inst.R)
	
	# Initialization of variables for storing the solution
	y = [[0 for j in range(m)] for i in range(n)]
	q = [[[[0 for t in range(k)] for j in range(m)] for s in range(k)] for i in range(n)]
	M = []
	
	# Termination criterion: zero remaining heat
	remaining_heat = sum(sum(QH[i]) for i in range(n))
	
	# Helper for dealing with precision issues
	epsilon = 10**(-7)
	
	# Algorithm's timer
	start_time = time()
	
	hot_streams_sorting(n, QH)
	
	for i in range(n):
		
		while sum(QH[i]) > epsilon:
		
			# Storing the new match
			matched_j = -1
		
			# Heat exchanges between the new matched pair of streams
			# q[s][t] specifies the heat exchange between (matched_i,s) and (matched_j,t)
			matched_q = [[0 for t in range(k)] for s in range(k)]
		
			# Storing the heat transferred via the chosen match of the iteration match 
			matched_heat = 0
		
			# The new heat residuals after performing the above heat exchanges.
			resulting_R = list(R)
		
			# For each cold stream j, compute the one with the maximum fraction
			for j in range(m):
				if (i,j) not in M:
				
					# Compute the maximum heat exchanged between (i,j)
					(temp_heat,temp_q,temp_R)=max_heat(i,j,k,QH[i],QC[j],R)
					
					if temp_heat > matched_heat:
						matched_j = j
						matched_q = temp_q
						resulting_R = temp_R
						matched_heat = temp_heat
		
			# Introduction of the new match
			M.append((i, matched_j))
			y[i][matched_j]=1
			
			print('Matches: ' + str(len(M)))
			
			for s in range(k):
				for t in range(k):
					q[i][s][matched_j][t] = matched_q[s][t]
					QH[i][s] -= matched_q[s][t]
					QC[matched_j][t] -= matched_q[s][t]
			R=resulting_R
			
	end_time = time()
	elapsed_time = end_time - start_time
	
	matches = len(M)
	
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
      
def hot_streams_sorting(n, QH):
	for ia in range(n-1):
		for ib in range(ia+1,n):
			if sum(QH[ia]) > sum(QH[ib]):
				temp=QH[ia]
				QH[ia]=QH[ib]
				QH[ib]=temp