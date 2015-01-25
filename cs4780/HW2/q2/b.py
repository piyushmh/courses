'''
Created on 21-Sep-2013

@author: piyush
'''

import sklearn.datasets as skl
import numpy as np
from matplotlib.mlab import log2
from Queue import *
import pylab as py
import random

class DTNode:
    pass
        
def findEntropy(ts):
    pos=0
    neg =0
    for i in range(0,len(ts)):
        if(ts[i][1] == 1):
            pos = pos+1
        else:
            neg = neg+1
    
    p = (float)(pos) / (pos+neg)
    n = (float)(neg) / (pos+neg)
    e = 0  
    if (p!=0):
        e = e + (-1)*(p)*log2(p)
    if(n!=0):
        e = e + (-1)*(n)*log2(n)
    return e

def split(attribute, ts):
    index, th = attribute
    incList  = []
    excList = []
    for i in range(0,len(ts)):
        if( ts[i][0][0][index] >= th): 
            incList.append(ts[i])
        else:
            excList.append(ts[i])
    return incList, excList
           
def gain(ent, attribute, ts):
    incList, excList  = split(attribute, ts)
    a = ((float)(len(incList)) * findEntropy(incList)) / len(ts)
    b = ((float)(len(excList)) * findEntropy(excList)) / len(ts)
    return (ent-a-b)

def findDataRange(trainingData):
    xmax = sorted(trainingData, key=lambda x:(-x[0][0][0]))[0][0][0][0]
    xmin = sorted(trainingData, key=lambda x:(x[0][0][0]))[0][0][0][0]
    ymax = sorted(trainingData, key=lambda x:(-x[0][0][1]))[0][0][0][1]
    ymin = sorted(trainingData, key=lambda x:(x[0][0][1]))[0][0][0][1]
    return xmin,xmax,ymin,ymax

def findSplittingAttribute(trainingData):
    xmin,xmax,ymin,ymax = findDataRange(trainingData)
    #print xmin,xmax,ymin,ymax
    etpy = findEntropy(trainingData)
    m = -10000
    attr = ()
    for x in range((int)(xmin) +1, (int)(xmax)+1):
        if( gain(etpy, (0,x), trainingData) > m ):
            m  = gain(etpy, (0,x), trainingData)
            attr = (0,x)
    
    for y in range((int)(ymin) +1, (int)(ymax)+1):
        if( gain(etpy, (1,y), trainingData) > m ):
            m  = gain(etpy, (1,y), trainingData)
            attr = (1,y)   
    #print attr
    return attr
           
    
def findMaximumVote(td):
    pos = 0
    neg = 0
    for i in range(0,len(td)):
        if( td[i][1]==1):
            pos = pos+1
        else:
            neg= neg+1
    if(pos>=neg):
        return 1;
    else:
        return 0;

def allMatchingLabel(td):
    pos = 0
    neg = 0
    for i in range(0,len(td)):
        if( td[i][1]==1):
            pos = pos+1
        else:
            neg= neg+1
    if( len(td)==pos or len(td)==neg ):
        return 1
    else:
        return 0

def create_dt(trainingData):
    xmin,xmax,ymin,ymax = findDataRange(trainingData)
    root = DTNode()
    root.td = trainingData
    root.threshold = -1
    root.attribute = -1
    root.entropy = findEntropy(trainingData)
    root.label = -1 
    root.leftTree = -1;
    root.rightTree = -1
    root.isLeaf = 0
    xmin  = (int)(xmin);
    xmax  = (int)(xmax);
    ymin  = (int)(ymin);
    ymax  = (int)(ymax);
    if( ( (xmin==xmax) or (xmin+1==xmax) ) and ( (ymin==ymax) or (ymin+1==ymax) )): #attributes over
        root.isLeaf = 1;
        root.label = findMaximumVote(trainingData)
        return root;
    if(allMatchingLabel(trainingData)): #all labels are same, leaf node time 
        root.isLeaf = 1;
        root.label = findMaximumVote(trainingData)
        return root;
    
    attribute, th = findSplittingAttribute(trainingData)
    root.attribute = attribute
    root.threshold = th
    rightSplit, leftSplit = split((attribute,th), trainingData)
    root.leftTree = create_dt(leftSplit)
    root.rightTree = create_dt(rightSplit)        
    return root;
                  
                  
def levelOrder(root):
    
    q = Queue(maxsize=0)
    q.put((1,root))
    while q.qsize()>0:
        lev, node = q.get();
        if(node.isLeaf == 1):
            print lev, "Label : ",node.label;
        else:
            print lev, node.attribute, node.threshold
            if( node.leftTree != -1):
                q.put((lev+1,node.leftTree))
            if( node.rightTree != -1):
                q.put((lev+1, node.rightTree))
    
           
def printHeight(root): 
    lh = 0
    if(root.leftTree != -1):
        lh = printHeight(root.leftTree)
    rh = 0
    if(root.rightTree != -1):
        rh = printHeight(root.rightTree)
       
    return (1+ max(lh,rh))
    
def descentTree(test, root):
    if root.isLeaf==1:
        return root.label;
    
    attr = root.attribute;
    th = root.threshold;
    
    if test[attr]>=th:
        return descentTree(test, root.rightTree)
    else:
        return descentTree(test, root.leftTree)

def randomPartitionTD(td, l):
    counter  = 0
    used = {}
    retList = []
    while counter<=l:
        rand =  random.randint(0,289)
       # print rand
        if rand not in used.keys ():
            used[rand]=1
            retList.append(td[rand])
            counter = counter+1
    return retList;        


def plotDecisionBoundary(root):
    colorMap = ['b','r']
    py.subplot(211)
    py.xlim(0,100)
    py.ylim(0,100)
    for i in range(0,100):
        for j in range(0,100):
                predLabel = descentTree([(float)(i)/10, (float)(j)/10], root)
                py.scatter(i,j,color=colorMap[predLabel])   
    py.show()

def findMajority(l):
    pos = 0
    neg = 0
    for i in range(0,len(l)):
        if l[i]==1:
            pos = pos+1
        else:
            neg = neg+1
    if(pos>=neg):
        return 1
    else:
        return 0

def calculateNumberOfNodes(root):
    l = 0
    r = 0 
    if root.leftTree!=-1:
        l = calculateNumberOfNodes(root.leftTree)
    if root.rightTree!=-1:
        r = calculateNumberOfNodes(root.rightTree)
    return 1+l+r


#Entry point for a.py
circleTrain = open('/home/piyush/machine-learning/HW2/ps2_Data/circle.train', 'r')
m,label= skl.load_svmlight_file(circleTrain)
trainCircleMatrix =m.todense()
trainingData = []
for i in range(0,len(label)):
    tup = np.array(trainCircleMatrix[i]), label[i]
    trainingData.append(tup)

decisionTreeList = []
dTNodeList = []
for i in range(0,101):
        tdInner = randomPartitionTD(trainingData, len(trainingData)/5)
        dt = create_dt(tdInner)
        decisionTreeList.append(dt)
        dTNodeList.append((dt,calculateNumberOfNodes(dt)))
        
dTNodeList = sorted(dTNodeList, key=lambda x:(-x[1]))
print dTNodeList[0][1], dTNodeList[1][1]
plotDecisionBoundary(dTNodeList[1][0])
# colorMap = ['b','r']
# py.subplot(211)
# py.xlim(0,100)
# py.ylim(0,100)
# for x in range(0,100):
#     for y in range(0,100):
#         labelList = []
#         for dt in range(0,101):
#             predLabel = descentTree([(float)(x)/10, (float)(y)/10], decisionTreeList[dt])
#             labelList.append(predLabel)
#         
#         mLabel = findMajority(labelList)
#         py.scatter(x,y,color=colorMap[mLabel])
#        
# py.show()
        

