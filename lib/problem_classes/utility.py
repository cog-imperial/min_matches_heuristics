# A utility of the problem is associated with the following parameters:
# 1. an inlet temperature Tin and an outlet temperature Tout
# 2. a unitary cost (per unit of heat)

class Utility:
	
	def __init__(self,Tin,Tout,cost):
		self.Tin=Tin
		self.Tout=Tout
		self.cost=cost
		
	def __repr__(self):
		return 'Tin:' + str(self.Tin) + ', Tout:' + str(self.Tout) + ', Cost:' + str(self.cost)