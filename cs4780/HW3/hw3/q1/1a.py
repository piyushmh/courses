'''
Created on 06-Oct-2013

@author: piyush
'''

import numpy as np

inputTraining  = np.array([[1,5,1],
                          [3,5,1],
                          [4,7,1],
                          [4,9,1],
                          [6,9,1],
                          [3,1,1]])

w = np.array([1,1,0]) #weight vector
labels = [ -1,-1,1,1,1,-1]

isNotfinish = True
while isNotfinish:
    isNotfinish = False
    for i in range(0, len(inputTraining)):
        if labels[i]*np.asscalar(np.dot(inputTraining[i], w.T))<=0:
            isNotfinish = True
            w = w + labels[i]*inputTraining[i]
            
print (w)
        
    
    
    