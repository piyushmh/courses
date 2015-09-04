from __future__ import with_statement
from threading import Thread, Lock, Condition
import time, random

# The Bathroom Problem

# Some sims share a bathroom and need to use that bathroom either to
# wash their hands or to use the toilet.  Only one sim may use the
# toilet at any time, and for the sake of privacy, no other sims may
# be in the bathroom while a sim is using the toilet.  When no sims
# are using the toilet, any number of sims can concurrently be in the
# bathroom to wash their hands.  If there are sims using the toilet or
# washing their hands, no other sims may use the toilet no matter how
# urgent it is.

# Use only monitors and condition variables

def delay():
    time.sleep(random.randint(0, 2))

#Implement me!
class bathroom:
    def __init__(self):
        self.nwasherWaiting = 0 # number of sims waiting for washing hands
        self.nwasherUsing = 0 # number of sims washing hands right now
        self.toiletBusy = 0 # is toilet busy right now ?
        self.bathroomLock = Lock();
        self.toiletLine = Condition(self.bathroomLock)
        self.washerLine = Condition(self.bathroomLock)

    def washer_enter(self):
        with self.bathroomLock:
            while self.toiletBusy==1:
                self.nwasherWaiting = self.nwasherWaiting + 1
                self.washerLine.wait()
                self.nwasherWaiting = self.nwasherWaiting - 1
            self.nwasherUsing = self.nwasherUsing + 1

    def washer_exit(self):
        with self.bathroomLock:
            self.nwasherUsing = self.nwasherUsing - 1
            if self.nwasherUsing==0:
                self.toiletLine.notify() #this is because only one person can enter the toilet, so notifyAll is redundant

    def toilet_enter(self):
        with self.bathroomLock:
            while(self.toiletBusy==1 or self.nwasherUsing > 0):
                self.toiletLine.wait()
            self.toiletBusy = 1

    def toilet_exit(self):
        with self.bathroomLock:
            self.toiletBusy = 0
            if self.nwasherWaiting > 0 :
                self.washerLine.notifyAll() # Since mutiple sims can use the washer now
            else:
                self.toiletLine.notify()


class SimWasher(Thread):
    def __init__(self,bathroom):
        Thread.__init__(self)
        self.bathroom = bathroom

    def run(self):
        self.bathroom.washer_enter()
        print("Sim washing hands")
        delay()
        print("Sim done washing hands")
        self.bathroom.washer_exit()

class SimToilet(Thread):
    def __init__(self,bathroom):
        Thread.__init__(self)
        self.bathroom = bathroom

    def run(self):
        self.bathroom.toilet_enter()
        print("Sim using toilet")
        delay()
        print("Sim done using toilet")
        self.bathroom.toilet_exit()

b = bathroom()

for i in range(5):
    SimWasher(b).start()
    SimToilet(b).start()
