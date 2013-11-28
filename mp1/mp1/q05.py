from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
import time, random

# Time Waster Wars: Reddit vs. 4chan
#
# a. Add synchronization primitives to ensure that
#    (a) the club is exclusively redditors or 4channers, i.e. no redditors
#        should enter as long as there are 4channers in the club,
#        and vice versa,
#    (b) the club should always be used as long as there are
#        customers
#    Note that starvation is not something you need to worry
#    about. If the club becomes redditors and remains exclusively
#    redditors for all time, the waiting 4channers will just have
#    to get old at the door.
#
# Modify only the code of the class Club to make the program
# correct.
# Place your synchronization variables inside the Club instance.
#
# You may use only monitors and condition variables.

def hangout():
    time.sleep(random.randint(0, 2))

class Club:
    def __init__(self):
        self.clubLock = Lock()
        self.redditCond = Condition(self.clubLock)
        self.fourchannerCond = Condition(self.clubLock)
        self.fourchannerCount = 0
        self.redditorCount = 0

    def redditor_enter(self):
        with self.clubLock:
            while self.fourchannerCount > 0 : 
                self.redditCond.wait()
            self.redditorCount = self.redditorCount + 1

    def redditor_exit(self):
        with self.clubLock:
            self.redditorCount = self.redditorCount - 1
            if self.redditorCount == 0 : 
                self.fourchannerCond.notify()

    def fourchanner_enter(self):
        with self.clubLock:
            while self.redditorCount > 0 :
                self.fourchannerCond.wait()
            self.fourchannerCount = self.fourchannerCount + 1

    def fourchanner_exit(self):
        with self.clubLock:
            self.fourchannerCount = self.fourchannerCount - 1
            if self.fourchannerCount == 0:
                self.redditCond.notify()


class Redditor(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            daclub.redditor_enter()
            print("Redditor #%d: in the club" % self.id)
            hangout()
            daclub.redditor_exit()

class Fourchanner(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            daclub.fourchanner_enter()
            print("4channer #%d: in the club" % self.id)
            hangout()
            daclub.fourchanner_exit()

NUM_REDDIT=3
NUM_4CHAN=3
daclub = Club()
for i in range(NUM_REDDIT):
    g = Redditor(i)
    g.start()
for i in range(NUM_4CHAN):
    h = Fourchanner(i)
    h.start()
