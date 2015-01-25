input = [2,1]
len = 2

transition = []
transition.append([.05,0.1,0.15,0.7])
transition.append([.1,.05,.25,0.6])
transition.append([.45,.15,.05,.35])
transition.append([.35,.2,.15,.3])

emission = []
emission.append([.4,.2,.1,.2,.1])
emission.append([.3,.1,.4,.1,.1])
emission.append([.1,.1,.1,.2,.5])
emission.append([.1,.4,.1,.3,.1])

start = [.1,.4,.2,.3]

table = [[] for i in range(4)]
link = [[] for i in range(4)]

for i in range(4):
	table[i].append(start[i]*emission[i][input[0]])

for j in range(1,len): 
	for i in range(0,4):
		val = 0.0
		valindex = -1
		for k in range(4):
			temp = (1.0)*table[k][j-1]* transition[k][i]* emission[i][input[j]]
			if( temp > val):
				val = temp
				valindex = k
		table[i].append(val)
		link[i].append(valindex)

for i in range(4):
	for j in range(len):
		print str(table[i][j])+ " ",
	print "\n"

for i in range(4):
	for j in range(len-1):
		print str(link[i][j])+ " ",
	print "\n"
