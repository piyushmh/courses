from threading import Thread, Semaphore
import time, random

# The Relay Race Problem

# You are on a relay race team with N members.  There are S stages of the race.
# All members of your team must finish the current stage before any member can
# move on to the next stage.

# Use only semaphores

def delay():
    time.sleep(random.randint(0, 2))

#Implement me!
class Race:
    def __init__(self):
        self.stageFinishCount = 0
        self.stageStartCount = 0 
        self.mutex = Semaphore(1) #used for mutual exclusion while writing
        self.stageFinishSema = Semaphore(0)
        self.stageStartSema = Semaphore(0) #This is used so that people dont try to finish the next stage until everyone has left the prev stage  
    def teammate_start_stage(self):
        count = 0
        with self.mutex:
            self.stageStartCount = self.stageStartCount + 1
            count = self.stageStartCount

        if count < NUM_TEAMMATES:
            self.stageStartSema.acquire()
        else:
            self.stageStartCount = 0
            for i in range(NUM_TEAMMATES-1):
                self.stageStartSema.release() # only last person starting the stage would release all thread.

    def teammate_finish_stage(self):
        count = 0 #local variable separate to each thread
        with self.mutex:
            self.stageFinishCount = self.stageFinishCount + 1
            count = self.stageFinishCount

        if count < NUM_TEAMMATES:
            self.stageFinishSema.acquire()
        else:
            self.stageFinishCount = 0
            for i in range(NUM_TEAMMATES-1):
                self.stageFinishSema.release() #last teammate only can do this

class Teammate(Thread):
    def __init__(self,id):
        Thread.__init__(self)
        self.id = id;

    def run(self):
        for stage in range(NUM_STAGES):
            r.teammate_start_stage()
            print("Teammate #%d: entered stage #%d " % (self.id, stage))
            delay()
            print("Teammate #%d: finished stage #%d" % (self.id, stage))
            r.teammate_finish_stage()
            #should not get here until all teammates are finished with the stage

NUM_STAGES = 5;
NUM_TEAMMATES = 5;

r = Race();

for i in range(NUM_TEAMMATES):
    Teammate(i).start();
