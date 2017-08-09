def write_min_utility_dat_file(path,cat,inst):
	
	file_name = cat + str(len(inst.HS)) + '.dat'
	
	f=open(path+file_name,'w')
	
	f.write('DTmin ' + str(inst.DTmin) + '\n')
	
	for stream in inst.HS: f.write('HS' + str(inst.HS.index(stream)) + ' ' + str(stream.Tin) + ' ' +  str(stream.Tout) + ' ' + str(stream.FCp) + '\n')
	for stream in inst.CS: f.write('CS' + str(inst.CS.index(stream)) + ' ' + str(stream.Tin) + ' ' +  str(stream.Tout) + ' ' + str(stream.FCp) + '\n')
	for utility in inst.HU: f.write('HU' + str(inst.HU.index(utility)) + ' ' +  str(utility.Tin) + ' ' +  str(utility.Tout) + ' ' + str(utility.cost) + '\n')
	for utility in inst.CU: f.write('CU' + str(inst.CU.index(utility)) + ' ' +  str(utility.Tin) + ' ' +  str(utility.Tout) + ' ' + str(utility.cost) + '\n' )
	
	f.close()
	

def write_min_utility_random_dat_file(path,cat,inst,trial):
	
	file_name = cat + str(len(inst.HS)) + '_random'+ str(trial) +'.dat'
	
	f=open(path+file_name,'w')
	
	f.write('DTmin ' + str(inst.DTmin) + '\n')
	
	for stream in inst.HS: f.write('HS' + str(inst.HS.index(stream)) + ' ' + str(stream.Tin) + ' ' +  str(stream.Tout) + ' ' + str(stream.FCp) + '\n')
	for stream in inst.CS: f.write('CS' + str(inst.CS.index(stream)) + ' ' + str(stream.Tin) + ' ' +  str(stream.Tout) + ' ' + str(stream.FCp) + '\n')
	for utility in inst.HU: f.write('HU' + str(inst.HU.index(utility)) + ' ' +  str(utility.Tin) + ' ' +  str(utility.Tout) + ' ' + str(utility.cost) + '\n')
	for utility in inst.CU: f.write('CU' + str(inst.CU.index(utility)) + ' ' +  str(utility.Tin) + ' ' +  str(utility.Tout) + ' ' + str(utility.cost) + '\n' )
	
	f.close()
	
def write_mip_instance(test_set,test_id,network):

	#f=open('data/mip_instances/' + test_set + '/' + test_id + '_' + solver + '.dat', 'w')
	f=open('data/mip_instances/' + test_set + '/' + test_id + '.dat', 'w')
	
	epsilon=1e-10

	f.write('Cost=' + str(network.cost) + '\n')
	f.write('n=' + str(network.n) + '\n')
	f.write('m=' + str(network.m) + '\n')
	f.write('k=' + str(network.k) + '\n')

	for i in range(network.n):
		s='QH[' + str(i) + ']:'
		for t in range(network.k):
			if network.QH[i][t]>epsilon: s+=' ' + 'T' + str(t) + ' ' + str(network.QH[i][t])
		s+='\n'
		f.write(s)
	
	for j in range(network.m):
		s='QC[' + str(j) + ']:'
		for t in range(network.k):
			if network.QC[j][t]>epsilon: s+=' ' + 'T' + str(t) + ' ' + str(network.QC[j][t])
		s+='\n'
		f.write(s)
	
	for t in range(network.k+1):
		s='R[' + str(t) + ']= ' + str(network.R[t]) + '\n'
		f.write(s)
		
	f.close()
	
def write_bigM_parameters(test_set, test_id, network):
	
	bigM_types = ['simple', 'gundersen', 'greedy']
	
	for bigM_type in bigM_types: 
	
		f=open('data/bigM_parameters/' + test_set + '/' + bigM_type + '/' + test_id + '.bgm', 'w')
		
		for i in range(network.n):
			for j in range(network.m):
				
				if bigM_type == 'simple':
					s = 'U[' + str(i) + ',' + str(j) + ']= ' + str(network.U_simple[i][j]) + '\n'
				if bigM_type == 'gundersen':
					s = 'U[' + str(i) + ',' + str(j) + ']= ' + str(network.U_gundersen[i][j]) + '\n'
				if bigM_type == 'greedy':
					s = 'U[' + str(i) + ',' + str(j) + ']= ' + str(network.U[i][j]) + '\n'
				
				f.write(s)
				
		f.close()
	
def write_packing_instance(test_set,test_id,packing):
  
	f=open('data/packing_instances/' + test_set + '/' + test_id + '.dat', 'w')
	
	f.write('n=' + str(len(packing.H)) + '\n')
	f.write('m=' + str(len(packing.C)) + '\n')
	
	for i in packing.H:
		f.write('H['+str(packing.H.index(i))+']: '+ 'Tin=' +str(i.Tin)+' Tout='+str(i.Tout)+' FCp='+str(i.FCp)+'\n')
		
	for j in packing.C:
		f.write('C['+str(packing.C.index(j))+']: '+ 'Tin=' +str(j.Tin)+' Tout='+str(j.Tout)+' FCp='+str(j.FCp)+'\n')
		
	f.close()
	

def write_mip_solution(test_set,test_id,solver,mip_solution,stats):
	
	epsilon=1e-10
	
	if mip_solution.model == 'transshipment' or mip_solution.model == 'transportation': 
	  
		f=open('data/mip_solutions/'+test_set+'/'+mip_solution.model+'/'+test_id+'_'+solver+'.sol', 'w')
		f.write('Elapsed time: ' + str(stats.elapsed_time) + '\n')
		f.write('Nodes explored: ' + str(stats.nodes_explored) + '\n')
		f.write('Upper bound: ' + str(stats.upper_bound) + '\n')
		f.write('Lower bound: ' + str(stats.lower_bound) + '\n')
		
	if mip_solution.model == 'greedy_packing' or mip_solution.model == 'relaxation_rounding' or mip_solution.model == 'water_filling' : 
	  
		f=open('data/heuristic_solutions/'+test_set+'/'+mip_solution.model+'/'+test_id+'_'+solver+'.sol', 'w')
		#if solver == 'lp_rounding' or solver == 'lr_rounding':
		f.write('Elapsed time: ' + str(stats) + '\n')
		f.write('Upper bound: ' + str(mip_solution.matches) + '\n')
	
	if mip_solution.model=='transshipment' or mip_solution.model == 'water_filling' :
	  
		for i in range(mip_solution.n):
			for j in range(mip_solution.m):
				if mip_solution.y[i][j]>epsilon:
					f.write('y['+str(i)+','+str(j)+']=1\n')
		for i in range(mip_solution.n):
			for j in range(mip_solution.m):
				for t in range(mip_solution.k):
					if mip_solution.q[i][j][t]>epsilon:
						f.write('q['+str(i)+','+str(j)+','+str(t)+']='+str(mip_solution.q[i][j][t])+'\n')
						
		if mip_solution.model=='transshipment':
			for i in range(mip_solution.n):
				for t in range(mip_solution.k):
					if mip_solution.r[i][t]>epsilon:
						f.write('r['+str(i)+','+str(t)+']='+str(mip_solution.r[i][t])+'\n')
	
	else:
		for i in range(mip_solution.n):
			for j in range(mip_solution.m):
				if mip_solution.y[i][j]!=0:
					f.write('y['+str(i)+','+str(j)+']=1\n')
		for i in range(mip_solution.n):
			for ti in range(mip_solution.k):
				for j in range(mip_solution.m):
					for tj in range(mip_solution.k):
						if mip_solution.q[i][ti][j][tj]!=0:
							f.write('q['+str(i)+','+str(ti)+','+str(j)+','+str(tj)+']='+str(mip_solution.q[i][ti][j][tj])+'\n')
	
	f.close()
