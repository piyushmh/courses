from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
import Constants import NUMSEGMENTS, INDIRECTBLOCKOFFSET, INODEIDENTIFIEROFFSET

class SegmentMonitor:
	def __init__(self):
		self.segmentLock = Lock()
		self.segmentsbusy = {}

	# Non blocking lock
	def acquire_segment_lock(self, segmentnumber):
		with segmentLock:
			if segmentnumber in self.segmentsbusy:
				return 0
			else:
				self.segmentsbusy[segmentnumber] = 1
				return 1

	def release_segment_lock(self, segmentnumber):
		with segmentLock:
			if segmentnumber in self.segmentsbusy:
				del self.segmentsbusy[segmentnumber]
				return 1
			else
				return 0

class CleanerClass(Thread):
	 def __init__(self, segmentmonitor):
	 	Thread.__init__(self)
	 	self.segmentmonitor = segmentmonitor
	 	self.next_segment_to_clean = 0


	 def run(self):
	 		while True:
	 			time.sleep(60):
	 			self.clean_segment()

	 def clean_segment(self):
	 	if self.segmentmonitor.acquire_segment_lock(self.next_segment_to_clean)==1:
	 		
	 		#Add implementation
	 		
	 		if self.segmentmonitor.release_segment_lock(self.next_segment_to_clean)==0:
	 			print "Cleaner class,Alert1 Something went wrong"
	 	self.next_segment_to_clean = (self.next_segment_to_clean+1)%NUMSEGMENTS