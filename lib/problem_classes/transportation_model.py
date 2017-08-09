from ..problem_classes.stream import Stream
from ..problem_classes.utility import Utility

# An object of this class is used to initialize the transshipment LP and store the obtained solution.
class Transportation_Model:

	# The constructor computes various vectors such as the boundaries of the temperature intervals
	# and the non-allowed temperature intervals of each utility. 
	# The parameter is a Min_Utility_Instance
	def __init__(self, inst):
		
		self.inst=inst
		
		self.ns=len(inst.HS)
		self.ms=len(inst.CS)
		self.nu=len(inst.HU)
		self.mu=len(inst.CU)
		
		self.DT=[] # discrete temperatures	
		self.discrete_temperatures()
		self.k=len(self.DT)-1 # number of temperature intervals
		
		self.forbiddenHUTI=[] # forbidden pairs of hot utility and temperature interval
		self.forbiddenCUTI=[] # forbidden pairs of cold utility and temperature interval
		self.forbidden_temperature_intervals()
		
		# heat loads of streams
		self.QHS=[[0 for t in range(self.k)] for i in range(self.ns)]
		self.QCS=[[0 for t in range(self.k)] for j in range(self.ms)]
		self.stream_heat_loads()
		
		# cost vectors of utilities
		self.costHU=[]
		self.costCU=[]
		self.utility_costs()
		
		# the heat entering the first temperature interval and 
		# the heat exiting the last temperature interval must be zero. 
		self.zero_residuals=[0,self.k]
		
	# Computation of the temperature interval boundaries.
	def discrete_temperatures(self):
	  
		## discrete temperatures
		#self.DT = [hot_stream.Tin for hot_stream in self.H if hot_stream.Tin not in self.DT] 
		#self.DT += [hot_utility.Tin for hot_utility in self.HU if hot_utility.Tin not in self.DT]
		#self.DT += [cold_stream.Tin + self.dTmin for cold_stream in self.C if cold_stream.Tin not in self.DT]
		#self.DT += [cold_utility.Tin + self.dTmin for cold_utility in self.CU if cold_utility.Tin not in self.DT]
		#self.DT.sort(reverse=True)
		
		for i in range(self.ns):
			T=self.inst.HS[i].Tin
			if T not in self.DT:
				self.DT.append(T)
		for j in range(self.ms):
			T=self.inst.CS[j].Tin + self.inst.DTmin
			if T not in self.DT:
				self.DT.append(T)
		for i in range(self.nu):
			T=self.inst.HU[i].Tin
			if T not in self.DT:
				self.DT.append(T)
		for j in range(self.mu):
			T=self.inst.CU[j].Tin + self.inst.DTmin
			if T not in self.DT:
				self.DT.append(T)
		self.DT.sort(reverse=True)
		#print(self.DT)
	
	# Computation of the forbidden temperature intervals of each utility.
	def forbidden_temperature_intervals(self):
	  
		for i in range(self.nu):
			for t in range(self.k):
				if self.inst.HU[i].Tin <= self.DT[t+1] or self.inst.HU[i].Tout >= self.DT[t]:
					self.forbiddenHUTI.append((i,t))
		for j in range(self.mu):
			for t in range(self.k):
				if self.inst.CU[j].Tin >= self.DT[t] - self.inst.DTmin or self.inst.CU[j].Tout <= self.DT[t+1] - self.inst.DTmin:
					self.forbiddenCUTI.append((j,t))
	
	# Computation of the heat load of each hot/cold stream in each temperature interval.
	def stream_heat_loads(self):
		
		for t in range(self.k):
			for i in range(self.ns):
				if self.inst.HS[i].Tin >= self.DT[t] and self.inst.HS[i].Tout < self.DT[t]:
					if self.inst.HS[i].Tout <= self.DT[t+1]:
						self.QHS[i][t]=self.inst.HS[i].FCp*(self.DT[t]-self.DT[t+1])
					else:
						self.QHS[i][t]=self.inst.HS[i].FCp*(self.DT[t]-self.inst.HS[i].Tout)
			for j in range(self.ms):
				if self.inst.CS[j].Tin <= self.DT[t+1] - self.inst.DTmin and self.inst.CS[j].Tout >= self.DT[t+1] - self.inst.DTmin:
					if self.inst.CS[j].Tout >= self.DT[t] - self.inst.DTmin:
						self.QCS[j][t]=self.inst.CS[j].FCp*(self.DT[t]-self.DT[t+1])
					else:
						self.QCS[j][t]=self.inst.CS[j].FCp*(self.inst.CS[j].Tout-(self.DT[t+1]-self.inst.DTmin))
						
	
	# Computation of the cheapest utility in each temperature interval.
	def utility_costs(self):
		
		for i in range (self.nu):
			self.costHU.append(self.inst.HU[i].cost)
		for j in range(self.mu):
			self.costCU.append(self.inst.CU[j].cost)
