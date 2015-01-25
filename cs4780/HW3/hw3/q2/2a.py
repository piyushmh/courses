import sklearn.datasets as skl
import numpy as np
import math as m
import os
import matplotlib.pyplot as plt


groupsTrain = open('groups2_norm.train', 'r')
groupTMSparse,groupLabels= skl.load_svmlight_file(groupsTrain)
groupsTrainMatrix =groupTMSparse.todense()
trainingData = []

groups = ["AUTO", "COMPUTERS","RELIGION","SPORTS"]        
C = [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0]  
#C = [1.0]
datasetsize = 2000
dataFolds = []
labelFolds = []
numFolds = 5

arr = []
for i in range(0,datasetsize):
    arr.append(i)

arr = np.random.permutation(arr)

for i in range(numFolds):
    foldSize = datasetsize/numFolds
    dataFold = []
    labelFold = []
    for j in range(foldSize):
        index = i*foldSize + j
        dataFold.append(groupsTrainMatrix[arr[index]])
        labelFold.append(groupLabels[arr[index]])
    dataFolds.append(dataFold)
    labelFolds.append(labelFold)

#print type(dataFolds[1][1])


def generateTrainValSplit(split):
    trainingData = [] 
    trainingLabel = []
    validData = []
    validLabel = []
    
    for i in range(numFolds):
        if(i==split):
            validData.extend(dataFolds[i])
            validLabel.extend(labelFolds[i])
        else:
            trainingData.extend(dataFolds[i])
            trainingLabel.extend(labelFolds[i])
    return trainingData, trainingLabel, validData, validLabel

def write_to_file(td, l, fileName):
    f = open(fileName, 'w',0)
    for i in range(0, len(td)):
        s = str(l[i])
        for j in range(0, len(td[i][0])):
            if td[i][0][j] != 0:
                s += " " +  str(j+1) + ":" + str(td[i][0][j])
        s+= '\n'
        f.write(s)


def generateClassTrainingFile(trainingData, trainingLabel, folderPath):
    count = 0
    for i in range(1,5):
        fileName = folderPath + groups[i-1] + ".train"
        #print file
        labelCopy = []
        for index in range(0,len(trainingLabel)):
            if trainingLabel[index]==i:
                labelCopy.append(1)
                count+=1
            else:
                labelCopy.append(-1)
        trainingData = np.array(trainingData)
        write_to_file(trainingData, labelCopy, fileName)

def generateTestingFile(data, label, fileName):
    trainingData = np.array(data)
    write_to_file(trainingData, label, fileName)

def executeLearn(c, dataFilePath, finalCopyPath):
    for i in range(0,4):
        dataFilePathLocal  = dataFilePath + groups[i]+".train"
        cmd = "/home/piyush/machine-learning/HW3/hw3/svm_light/svm_learn -c " + str(c) + " " + dataFilePathLocal
        os.system(cmd)
        copycommand = "mv svm_model "+ finalCopyPath + groups[i]+".model"
        os.system(copycommand)
        
def executeClassify(c, folderPath, testFileName):
    testFilePathLocal = folderPath + testFileName
    for i in range(0,4):
        outFileNameLocal = folderPath + testFileName + "." + groups[i]+".out"
        modelFileLocal = folderPath + groups[i]+ ".model"
        cmd = "/home/piyush/machine-learning/HW3/hw3/svm_light/svm_classify " + testFilePathLocal + " " + modelFileLocal + " " + outFileNameLocal
        os.system(cmd)

def findAccuracy(folderPath, testFileName, labels):
    fileLabels = []
    for i in range(0,4):
        outFileNameLocal = folderPath + testFileName + "." + groups[i]+".out"
        outFile= open(outFileNameLocal,'r')
        fileLabel = []
        for j in range(0, len(labels)):
            s = outFile.readline()
            s.strip()
            fileLabel.append(float(s))
        fileLabels.append(fileLabel)
                      
    errorCount = 0
    for i in range(0, len(labels)):
        labelsPerTest = []
        for ii in range(0,4):
            labelsPerTest.append((ii, fileLabels[ii][i]))
        predLabel = sorted(labelsPerTest, key=lambda x:(-x[1]))[0][0]
        if (predLabel+1)!=labels[i]:
            errorCount +=1
    return ((1.0)*errorCount) / len(labels)  

def findAverage(l):
    den = len(l)
    num = 0
    for i in range(den):
        num += l[i]
    return (1.0*num)/den

averageAccTraining = []
averageAccValidation = []   
                  
for c in C:
    cmd = 'mkdir '+ str(c)
    os.system(cmd)
    accuracyTrainingPerC = []
    accuracyValidationPerC = []
    for fold in range(5):
        trainingData, trainingLabel, validData, validLabel = generateTrainValSplit(fold)
        cmd1 = cmd +"/"+ str(fold)
        os.system(cmd1)
        dataPath = str(c)+"/"+ str(fold)+"/"
        generateClassTrainingFile(trainingData, trainingLabel, str(c)+"/"+ str(fold)+"/")
        executeLearn(c, dataPath, dataPath)
        generateTestingFile(trainingData, trainingLabel, dataPath+"totaltrain.train")
        generateTestingFile(validData, validLabel, dataPath+"totalvalidation.train")
        executeClassify(c,dataPath, "totaltrain.train")
        executeClassify(c,dataPath, "totalvalidation.train")
        accuracyTrainingPerC.append(findAccuracy(dataPath,"totaltrain.train", trainingLabel))
        accuracyValidationPerC.append(findAccuracy(dataPath,"totalvalidation.train", validLabel))
    #print accuracyTrainingPerC
    #print accuracyValidationPerC
    averageAccTraining.append(findAverage(accuracyTrainingPerC))
    averageAccValidation.append(findAverage(accuracyValidationPerC))

logK = [] 
for i in range(9):
    logK.append(m.log(C[i],2))
    averageAccTraining[i] = 100*(1-averageAccTraining[i])
    averageAccValidation[i] = 100*(1-averageAccValidation[i])
    
print averageAccTraining
print averageAccValidation

fig, ax = plt.subplots()

plt.xlabel('log C')
plt.ylabel('Accuracy %')
plt.axis([-10,10,80,105]);
ax.plot(logK, averageAccTraining, 'm',logK, averageAccValidation, 'k')
plt.show()

    