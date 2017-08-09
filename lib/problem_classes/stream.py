# A stream of the problem is associated with the following parameters: 
# 1. an inlet (initial) temperature Tin and an outlet (target) temperature Tout
# 2. a flow rate heat capacity FCp

class Stream:

	def __init__(self, Tin, Tout, FCp):
		self.Tin=Tin
		self.Tout=Tout
		self.FCp=FCp
	
	def __repr__(self):
		return 'Tin:' + str(self.Tin) + ', Tout:' + str(self.Tout) + ', FCp:' + str(self.FCp)