import sklearn.datasets as skl
import numpy as np
import math

dtrain = open('/home/piyush/machine-learning/HW4/arxiv/arxiv.train','r')
dtrainmat, dtrainlabel = skl.load_svmlight_file(dtrain)
#dTrainMatDense = dTrainMat.todense()
dtest = open('/home/piyush/machine-learning/HW4/arxiv/arxiv.test','r')
dtestmat, dtestlabel = skl.load_svmlight_file(dtest)

#print dtrainmat[0]
#print len(dtrainmat[0].toarray())
 
sumofwords  = [0,0]
freqofwords = [{},{}]
vocabsize = 0
numberofdocuments = [0,0]
totaldocument = 0
probabpredic = [0.0,0.0]

for i in range(0, len(dtrainlabel)):
    
    print ("Iterating over training ex no " + str(i+1))
    if dtrainlabel[i] == 1:
        numberofdocuments[1]+=1
    else:
        numberofdocuments[0]+=1
    
    totaldocument+=1
    documentwordsfreq = dtrainmat[i].data
    documentwordsindex = dtrainmat[i].indices
    
    for j in range(0, len(documentwordsfreq)):
        if(dtrainlabel[i]==1):
            sumofwords[1] += documentwordsfreq[j]
            if documentwordsindex[j] in freqofwords[1]:
                freqofwords[1][documentwordsindex[j]] += documentwordsfreq[j]
            else:
                freqofwords[1][documentwordsindex[j]] = documentwordsfreq[j]
        else:
            sumofwords[0] += documentwordsfreq[j]
            if documentwordsindex[j] in freqofwords[0]:
                freqofwords[0][documentwordsindex[j]] += documentwordsfreq[j]
            else:
                freqofwords[0][documentwordsindex[j]]  = documentwordsfreq[j]
              
        if documentwordsindex[j]+1 > vocabsize:
            vocabsize  = documentwordsindex[j]+1 

acctotal = 0.0
falsepos = 0
falseneg = 0
predcorrect  = 0
outlier = 0
pospredic = 0
negpredic = 0

for i in range(0, len(dtestlabel)): #iterating over each test document
    print ("Iterating over test ex no " + str(i+1))
    probabpredic[0] = 0.0
    probabpredic[1] = 0.0
    
    testdocumentwordfreq = dtestmat[i].data
    testdocumentwordindex = dtestmat[i].indices 
    for j in range(0, len(testdocumentwordindex)): #iterating over each word of a test document
        for cls in range(0,2): # iterating over each class
            nr = 0
            if testdocumentwordindex[j] in freqofwords[cls]:
                nr = 1 + freqofwords[cls][testdocumentwordindex[j]]
            else:
                nr = 1
                outlier+=1
            dr = vocabsize + sumofwords[cls]
            #print (len(testdocumentwordfreq))
            #print (len(testdocumentwordindex))
            probabpredic[cls] += (math.log((1.0 * nr)/dr) * testdocumentwordfreq[j])
            
    probabpredic[0] = probabpredic[0] + math.log((1.0*numberofdocuments[0])/ totaldocument)
    probabpredic[1] = probabpredic[1] + math.log((1.0*numberofdocuments[1])/ totaldocument)
    
    predlabel = 0
    if probabpredic[0] > probabpredic[1]:
        predlabel = -1
    elif probabpredic[0] == probabpredic[1]:
        if(numberofdocuments[0] > numberofdocuments[1] ):
            predlabel = -1
        else:
            predlabel = 1
    else:
        predlabel = 1
    
    if predlabel == 1:
        pospredic +=1
    else:
        negpredic +=1
    
    if predlabel == dtestlabel[i]:
        predcorrect +=1
    else:
        if predlabel == 1:
            falsepos +=1
        else:
            falseneg +=1 
    
acctotal = (1.0 * predcorrect) / len(dtestlabel)

#print outlier
print (acctotal*100)
print falsepos
print falseneg

print pospredic
print negpredic

print predcorrect
print len(dtestlabel)
#print len(dtestlabel)
#print sumofwords[0]
#print sumofwords[1]
#print probabpredic[0]
#print probabpredic[1]
#print numberofdocuments[0]
#print numberofdocuments[1]
        
        
        
        
        
        
        
        
        
        
        
        
        

