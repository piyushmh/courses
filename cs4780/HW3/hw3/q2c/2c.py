'''
Created on 07-Oct-2013

@author: piyush
'''

import sklearn.datasets as skl
import numpy as np

def write_to_file(td, l, fileName):
    f = open(fileName, 'w',0)
    for i in range(0, len(l)):
        s = str(l[i])
        for j in range(0, len(td[i])):
            if td[i][j] != 0:
                s += " " +  str(j+1) + ":" + str(td[i][j])
        s+= '\n'
        f.write(s)

groupsTrain = open('groups2.train', 'r')
groupTMSparse,groupLabels= skl.load_svmlight_file(groupsTrain)
groupsTrainMatrix =groupTMSparse.todense()
groupsTest = open('groups2.test', 'r')
groupTestMatrixSparse,groupTestLabels= skl.load_svmlight_file(groupsTest)
groupsTestMatrix =groupTestMatrixSparse.todense()

groupsTrainNorm = []
groupsTestNorm = []
for i in range(0, len(groupsTrainMatrix)):
    arr = np.asarray(groupsTrainMatrix[i])
    norm = np.linalg.norm(arr[0], 2)
    singleRow = []
    for j in range(0, len(arr[0])):
        singleRow.append(arr[0][j]/norm)
    groupsTrainNorm.append(singleRow)
    
for i in range(0, len(groupsTestMatrix)):
    arr = np.asarray(groupsTestMatrix[i])
    norm = np.linalg.norm(arr[0], 2)
    singleRow = []
    for j in range(0, len(arr[0])):
        singleRow.append(arr[0][j]/norm)
    groupsTestNorm.append(singleRow)

write_to_file(groupsTrainNorm, groupLabels, "groups2_norm.train")
write_to_file(groupsTestNorm, groupTestLabels, "groups2_norm.test")