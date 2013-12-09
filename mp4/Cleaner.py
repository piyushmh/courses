from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
from Constants import NUMSEGMENTS, INDIRECTBLOCKOFFSET, INODEIDENTIFIEROFFSET, NUMBLOCKS
from Constants import BLOCKSIZE, MAXDATABLOCKSINODE
from Inode import Inode,getmaxinode
import Segment,Disk, InodeMap
import struct
import time

DEBUG = True

class SegmentMonitor:
	def __init__(self):
		self.segmentLock = Lock()
		self.segmentsbusy = {}

	# Non blocking lock
	def acquire_segment_lock(self, segmentnumber):
		with self.segmentLock:
			if segmentnumber in self.segmentsbusy:
				return 0
			else:
				self.segmentsbusy[segmentnumber] = 1
				return 1

	def release_segment_lock(self, segmentnumber):
		with self.segmentLock:
			if segmentnumber in self.segmentsbusy:
				del self.segmentsbusy[segmentnumber]
				return 1
			else:
				return 0

class CleanerClass(Thread):
	def __init__(self, segmentmonitor):
	 	Thread.__init__(self)
	 	self.segmentmonitor = segmentmonitor
	 	self.next_segment_to_clean = 0


	def run(self):
	 		while True:
	 			time.sleep(1)
	 			try:
	 				if self.segmentmonitor.acquire_segment_lock(self.next_segment_to_clean)==1:
	 					self.clean_segment()
	 					if self.segmentmonitor.release_segment_lock(self.next_segment_to_clean)==0:
	 						if DEBUG:
				 				print "Cleaner class, Alert 1 Something went wrong"
	 				self.next_segment_to_clean = (self.next_segment_to_clean+1)%NUMSEGMENTS # Next time, pick a new segment
	 			except Exception, e:
	 				print e
	 				self.segmentmonitor.release_segment_lock(self.next_segment_to_clean)

	def clean_segment(self):
 		segment = Segment.SegmentClass(self.next_segment_to_clean)
 		
 		for i in range(0,NUMBLOCKS):
 			blockidtocheck = segment.segmentbase + 1 + i
 			data = Disk.disk.blockread(blockidtocheck)
 			data = data[BLOCKSIZE:]
 			inodeid, blockoffset = struct.unpack("II", data)
 			if not self._is_valid(inodeid, blockoffset):
 				continue

 			inodeblockid = InodeMap.inodemap.lookup(inodeid)
 			if inodeblockid == None:
 				segment.superblock.blockinuse[i] = False
 				if DEBUG:
 					print "Cleaner cleaned :", blockidtocheck
 			else:
 				if blockoffset != INODEIDENTIFIEROFFSET:
 					inodeobject = Inode(str=Segment.segmentmanager.blockread(inodeblockid))
 					if blockoffset == INDIRECTBLOCKOFFSET:
 						if inodeobject.indirectblock != blockidtocheck:
 							segment.superblock.blockinuse[i] = False			
 							if DEBUG:
 								print "Cleaner cleaned :", blockidtocheck
 					else:
 						storedblockid = inodeobject.find_datablock_by_offset(blockoffset)
 						if storedblockid != blockidtocheck:
 							segment.superblock.blockinuse[i] = False
 							if DEBUG:	 								
 								print "Cleaner cleaned :", blockidtocheck
 				else:
 					if inodeblockid != blockidtocheck:
 						segment.superblock.blockinuse[i] = False				
 						if DEBUG:
 							print "Cleaner cleaned :", blockidtocheck
	 		
	 		
	 	

 	def _is_valid(self,inodeid, blockoffset):
 	 	if inodeid < 1 or inodeid > getmaxinode():
 			return 0
 		if blockoffset!= INODEIDENTIFIEROFFSET and blockoffset!= INDIRECTBLOCKOFFSET:
	 		if blockoffset >= MAXDATABLOCKSINODE or blockoffset < 0:
	 			return 0
 		return 1

cleaner = None