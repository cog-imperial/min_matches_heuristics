from stream import Stream

# It provides a template for an input of the min utility cost problem.
class Min_Utility_Instance:

	def __init__(self,DTmin,HS,CS,HU,CU):
		self.DTmin = DTmin # minimum approach temperature
		self.HS = HS # list of hot streams
		self.CS = CS # list of cold streams
		self.HU = HU # list of hot utilities
		self.CU = CU # list of cold utilities
		
	def __repr__(self):
		s='Hot Streams \n'
		for hs in self.HS: s+='HS'+str(self.HS.index(hs))+': '+str(hs)+'\n'
		s+='\n'
		s+='Cold Streams \n'
		for cs in self.CS: s+='CS'+str(self.CS.index(cs))+': '+str(cs)+'\n'
		s+='\n'
		s+='Hot Utilities \n'
		for hu in self.HU: s+='HU'+str(self.HU.index(hu))+': '+str(hu)+'\n'
		s+='\n'
		s+='Cold Utilities \n'
		for cu in self.CU: s+='CU'+str(self.CU.index(cu))+': '+str(cu)+'\n'
		return s