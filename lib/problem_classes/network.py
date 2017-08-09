
class Network:
	
	def __init__(self, cost, ns, ms, nu, mu, k, QHS, QCS, QHU, QCU, R, min_utility_inst):
		
		self.cost=cost
		
		self.n=ns+nu
		self.m=ms+mu
		self.k=k
		
		epsilon=1e-10
		
		HU_FCp = []
		CU_FCp = []
		HU_Tin = []
		CU_Tin = []
		
		for i in range(nu):
			if sum(QHU[i][t] for t in range(k))<=epsilon:
				QHU.remove(QHU[i])
				min_utility_inst.HU.remove(min_utility_inst.HU[i])
				self.n-=1
				nu-=1
			else:
				HU_FCp.append(sum(QHU[i][t] for t in range(k)) / (min_utility_inst.HU[i].Tin - min_utility_inst.HU[i].Tout))
				HU_Tin.append(min_utility_inst.HU[i].Tin)
				
		for j in range(mu):
			if sum(QCU[j][t] for t in range(k))<=epsilon:
				QCU.remove(QCU[j])
				min_utility_inst.CU.remove(min_utility_inst.CU[j])
				self.m-=1
				mu-=1
			else:
				CU_FCp.append(sum(QCU[j][t] for t in range(k)) / (min_utility_inst.CU[j].Tout - min_utility_inst.CU[j].Tin))
				CU_Tin.append(min_utility_inst.CU[j].Tin)
		
		self.QH=[QHS[i] for i in range(ns)] + [QHU[i] for i in range(nu)] #if sum(QHU[i][t] for t in range(k))>epsilon]
		self.QC=[QCS[i] for i in range(ms)] + [QCU[i] for i in range(mu)]
		
		self.R=R
		
		# Computation of bigM_parameters with our way.
		self.U = [[0 for j in range(self.m)] for i in range(self.n)]
		for i in range(self.n): 
			for j in range(self.m): 
				self.U[i][j] = self.pairwise_upper_bound(i,j)
		
		self.forbidden_quadruples = [(i,ti,j,tj) for i in range(self.n) for j in range(self.m) for ti in range(self.k) for tj in range(self.k) if ti>tj]
		
		# The bigM parameters have been computed with our greedy way.
		self.U_greedy = [[self.U[i][j] for j in range(self.m)] for i in range(self.n)]
		
		# Computation of bigM_parameters in the standard way.
		self.h=[sum(self.QH[i][t] for t in range(self.k)) for i in range(self.n)] # total heat of each hot stream/utility
		self.c=[sum(self.QC[j][t] for t in range(self.k)) for j in range(self.m)] # total heat of each cold stream/utility
		self.U_simple = [[min(self.h[i],self.c[j]) for j in range(self.m)] for i in range(self.n)]
		
		# The following are applied when the min_utility_inst is non-empty for the computation of the big-M parameters.
		if min_utility_inst: 
		
			H_Tin = [min_utility_inst.HS[i].Tin for i in range(ns)] + [HU_Tin[i] for i in range(nu)]
			C_Tin = [min_utility_inst.CS[j].Tin for j in range(ms)] + [CU_Tin[j] for j in range(mu)]
			H_FCp = [min_utility_inst.HS[i].FCp for i in range(ns)] + [HU_FCp[i] for i in range(nu)]
			C_FCp = [min_utility_inst.CS[j].FCp for j in range(ms)] + [CU_FCp[j] for j in range(mu)]
			DTmin = min_utility_inst.DTmin
			
			# Computation of bigM parameters in Gundersen et al. way.
			self.U_gundersen = [[min(self.h[i], self.c[j], max(min(H_FCp[i],C_FCp[j])*(H_Tin[i]-C_Tin[j]+DTmin) , 0)) for j in range(self.m)] for i in range(self.n)]
			
		else:
			
			self.U_gundersen = [[0 for j in range(self.m)] for i in range(self.n)]
			
	def pairwise_upper_bound(self,i,j):
		
		QHi = list(self.QH[i])
		QCj = list(self.QC[j])
		
		Ti = [t for t in range(self.k) if QHi[t]>0] # Temperature intervals of hot stream i
		Tj = [t for t in range(self.k) if QCj[t]>0] # Temperature intervals of cold stream j
		
		R = list(self.R)
		Q = 0
		
		for t in Ti:
			if t in Tj:
				heat = min(QHi[t],QCj[t])
				Q += heat 
				QHi[t] -= heat
				QCj[t] -= heat
				
		Ti = [t for t in range(self.k) if QHi[t]>0] # Temperature intervals of hot stream i
		Tj = [t for t in range(self.k) if QCj[t]>0] # Temperature intervals of cold stream j
		
		for t_cold in Tj:
			for t_hot in Ti:
				if t_hot < t_cold:
					heat = min(QHi[t_hot],QCj[t_cold],min(R[t_hot+1:t_cold+1]))
					Q += heat
					QHi[t_hot] -= heat
					QCj[t_cold] -= heat
					for t in range(t_hot+1,t_cold+1):
						R[t] -= heat
					
		return Q
		
		
	# Pinch points are zero residuals, except the one entering the first interval 
	def decomposition(self):
		
		pinch_points=[t for t in range(1,self.k+1) if self.R[t]==0]
		
		if len(pinch_points)>1:
			t_init=0
			subnetworks=[]
			for t_next in pinch_points:
				QH=[self.QH[i][t_init:t_next] for i in range(self.n)]
				QC=[self.QC[j][t_init:t_next] for j in range(self.m)]
				R=self.R[t_init:t_next+1]
				subnetworks.append(Network(0,len(QH),len(QC),0,0,t_next-t_init,list(QH),list(QC),[],[],list(R)))
				t_init=t_next
			return subnetworks
		else:
			return []
		      
	def set_bigM_parameter(self, bigM_type):
		
		if bigM_type == 'simple':
			self.U = [[self.U_simple[i][j] for j in range(self.m)] for i in range(self.n)]
		if bigM_type == 'gundersen':
			self.U = [[self.U_gundersen[i][j] for j in range(self.m)] for i in range(self.n)]
		if bigM_type == 'greedy':
			self.U = [[self.U_greedy[i][j] for j in range(self.m)] for i in range(self.n)]
	      
	def __repr__(self):
		s=''
		for t in range(self.k):
			s+='Interval ' + str(t) + ':\n'
			for i in range(self.n):
				if self.QH[i][t]!=0:
					s+='H' + str(i) + ':' + str(self.QH[i][t]) + '\n'
			for j in range(self.m):
				if self.QC[j][t]!=0:
					s+='C' + str(j) + ':' + str(self.QC[j][t]) + '\n'
			s+= 'Residual above:' + str(self.R[t]) + '\n'
			s+= 'Residual below:' + str(self.R[t+1]) +'\n'
			s+= '\n'
		return s