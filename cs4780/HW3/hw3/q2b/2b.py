import sklearn.datasets as skl
import numpy as np
import os



groupsTrain = open('groups2_norm.train', 'r')
groupTMSparse,groupLabels= skl.load_svmlight_file(groupsTrain)
groupsTrainMatrix =groupTMSparse.todense()
groupsTest = open('groups2_norm.test', 'r')
groupTestMatrixSparse,groupTestLabels= skl.load_svmlight_file(groupsTest)


groups = ["AUTO", "COMPUTERS","RELIGION","SPORTS"]        
C = [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0]  
#C = [1.0]
datasetsize = 2000
dataFolds = []
labelFolds = []
numFolds = 5


def write_to_file(td, l, fileName):
    f = open(fileName, 'w',0)
    for i in range(0, len(l)):
        s = str(l[i])
        for j in range(0, len(td[i])):
            if td[i][j] != 0:
                s += " " +  str(j+1) + ":" + str(td[i][j])
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

def executeLearn(c, dataFilePath, finalCopyPath):
    for i in range(0,4):
        dataFilePathLocal  = dataFilePath + groups[i]+".train"
        cmd = "./svm_learn -c " + str(c) + " " + dataFilePathLocal
        os.system(cmd)
        copycommand = "mv svm_model "+ finalCopyPath + groups[i]+".model"
        os.system(copycommand)

def executeClassify(folderPath, testFileName):
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


generateClassTrainingFile(groupsTrainMatrix,groupLabels, "")
c = 1 #optimum value from part a

executeLearn(c, "","")
executeClassify("", "groups2.train")
executeClassify("", "groups2.test")
trainAcc = findAccuracy("", "groups2.train", groupLabels)
testAcc = findAccuracy("", "groups2.test" , groupTestLabels)

print 100*(1-trainAcc), 100*(1-testAcc)
    