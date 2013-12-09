#!/usr/bin/python
import os, random,time
import Shell
import pdb

from FSE import FileSystemException
testcases = []
replies = []

def init():
	Shell.CLEANERFLAG = False
	global testcases
	testcases.append(["mkfs","mkdir dir1", "mkdir dir2"])
	replies.append(["1","1","1"])
	
	testcases.append(["create file1 100", "create file2 1000"])
	replies.append(["1","1"])
	
	testcases.append(["rmdir dir2"])
	replies.append(["1"])

	testcases.append(["rm file2"])
	replies.append(["1"])

	testcases.append(["rmdir file1"])
	replies.append(["\"rmdir: failed to remove '/file1': Not a directory\""])

	testcases.append(["rm dir1"])
	replies.append(["\"rm: cannot remove '/dir1': Is a directory\""])

	testcases.append(["create testfile 5","write testfile newton", "cat testfile"])
	replies.append(["1","1","newton"])
	
	testcases.append(["sync","mkfs -reuse", "cd dir2"])
	replies.append(["1","1","1"])
	

def testloop():
    for i in range(len(testcases)):
    	for j in range(len(testcases[i])):
        	try:
	        	#pdb.set_trace()
	        	pieces = testcases[i][j].split(" ")    
	        	func = getattr(Shell.shell, pieces[0])
	        	s = func(pieces)
	        	if (s!= replies[i][j]):
	        		print "Test case failed"
	        		continue
    		except FileSystemException, fse:
    			#print len(str(fse))
    			#print len(replies[i][j])
    			if (str(fse)!= replies[i][j]):
	        		print "Test case {} failed".format(i)
	        		continue
        print "Test {} passed".format(str(i+1))
     
if __name__ == "__main__":
    init()
    testloop()
    os._exit(0)