'''
Created on 06-Oct-2013

@author: piyush
'''

import numpy as np
import matplotlib.pyplot as plt

inputTraining  = np.array([[1,5,1],
                          [3,5,1],
                          [4,7,1],
                          [4,9,1],
                          [6,9,1],
                          [3,1,1]])

labels = [ -1,-1,1,1,1,-1]
#barr = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
barr = [0.9]
maxMargin = 1.1180

fig, ax = plt.subplots()
x = np.linspace(0,25,100)
plt.axis([0,25,0,20]);
ax.plot(1,5,'ro')
ax.plot(3,5,'ro')
ax.plot(3,1,'ro')
ax.plot(4,7,'b*')
ax.plot(4,9,'b*')
ax.plot(6,7,'b*')
y = (31-2*x)/4
ax.plot(x, y, 'y')


def checkCondition(y,x,b):
    temp = w[0:len(w)-1]
    den = np.linalg.norm(temp, 2)
    num = y*(np.asscalar(np.dot(x, w.T)))
    frac = 0
    if den==0:
        frac = 0
    else:
        frac = ((1.0)*num)/den
    if frac <= (b*maxMargin):
        return True
    else:
        return False
    
for b in barr:
    isNotfinish = True
    count = 0
    w = np.array([0,0,0]) #weight vector
    while isNotfinish:
        isNotfinish = False
        count += 1
        for i in range(0, len(inputTraining)):
            if np.linalg.norm(w,2)==0:
                isNotfinish = True
                w = w + labels[i]*inputTraining[i]
            elif checkCondition(labels[i], inputTraining[i],b):
                isNotfinish = True
                w = w + labels[i]*inputTraining[i]
            
    print (w)
    y = (-1*(w[2]+w[0]*x))/w[1]
    ax.plot(x, y, 'm')

plt.show()
    