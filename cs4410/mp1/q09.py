from __future__ import with_statement
from threading import Thread, Lock, Condition
import time, random

# Big Brother Problem
#
# Our Government has gone mad with power and is now making arrests based
# on the "private" conversations of its citizens. It is watching constantly
# and sees almost anything as a threat against the nation. The National
# Surveillance Agency (NSA) has employed many to scour the population's
# emails for those up to no good. The NSA want's all the information it
# can get its hands on and store all of it into a massive database,
# syncronously of course. If the searchers find an incriminating email,
# the searchers flag it for later arrests.
# 
# Your task: model big brother with three threads: searchers, inserters,
# and arresters. All three share access to the massive db.  Searchers scour
# the db for bad entries and can search in parallel with each other. 
# Inserters add new emails to the db, and in order for big brother to not
# miss any criminals, insertions must be mutually exclusive. However, 
# searches can proceed during an insertion. Arresters remove flaged emails
# from the database, review the email, and proceed to arrest the criminal.
# When an arrest is in progress, all resources are diverted to the arrest.
# Therefore, at most one arrester can access the db at a time, and cannot 
# proceed in parallel with a search or an insertion.
#
# Use threads, monitors, and condition variables in the code below to
# implement the above specification.
#
# Do not worry about starvation

def dowork():
    time.sleep(random.randint(0, 2))

class Database:
    def __init__(self):
        self.dblock = Lock()
        self.nsearchers = 0
        self.nsearcherswaiting = 0
        self.ninserters = 0
        self.ninserterswaiting = 0
        self.narresters = 0
        self.narresterswaiting = 0
        self.searcherCond = Condition(self.dblock)
        self.inserterCond = Condition(self.dblock)
        self.arresterCond = Condition(self.dblock)

    def searcher_enter(self):
        with self.dblock:
            while self.narresters > 0:
                self.nsearcherswaiting = self.nsearcherswaiting + 1
                self.searcherCond.wait()
                self.nsearcherswaiting = self.nsearcherswaiting - 1
            self.nsearchers = self.nsearchers + 1

    def searcher_exit(self):
        with self.dblock:
            self.nsearchers = self.nsearchers - 1
            if self.narresterswaiting > 0 and self.nsearchers == 0 and self.ninserters == 0:
                self.arresterCond.notify()

    def inserter_enter(self):
        with self.dblock:
            while self.narresters > 0 or self.ninserters > 0:
                self.ninserterswaiting = self.ninserterswaiting + 1
                self.inserterCond.wait()
                self.ninserterswaiting = self.ninserterswaiting - 1
            self.ninserters = self.ninserters + 1

    def inserter_exit(self):
        with self.dblock:
            self.ninserters = self.ninserters - 1
            if self.ninserters == 0:
                if self.narresterswaiting > 0 and self.nsearchers == 0 and self.narresters == 0:
                    self.arresterCond.notify()
                elif self.ninserterswaiting > 0 and self.narresters == 0:
                    self.inserterCond.notify()

    def arrester_enter(self):
        with self.dblock:
            while self.narresters > 0 or self.ninserters > 0 or self.nsearchers > 0:
                self.narresterswaiting = self.narresterswaiting + 1
                self.arresterCond.wait()
                self.narresterswaiting = self.narresterswaiting - 1
            self.narresters = self.narresters + 1
            
    def arrester_exit(self):
        with self.dblock:
            self.narresters = self.narresters - 1
            if self.narresters == 0:
                if self.nsearcherswaiting > 0:
                    self.searcherCond.notifyAll()
                elif self.ninserterswaiting > 0 and self.ninserters == 0:
                    self.inserterCond.notify()
                elif self.narresterswaiting > 0 and self.nsearchers == 0 and self.ninserters == 0:
                    self.arresterCond.notify()


class Searcher(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            database.searcher_enter()
            print("Searcher #%d: I See All Evil" % self.id)
            dowork()
            database.searcher_exit()
            print("Searcher #%d: taking a break" % self.id)

class Inserter(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            database.inserter_enter()
            print("Inserter #%d: I Gather Your Mistakes" % self.id)
            dowork()
            database.inserter_exit()
            print("Inserter #%d: done inserting" % self.id)

class Arrester(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            database.arrester_enter()
            print("Arrester #%d: Donuts!" % self.id)
            dowork()
            database.arrester_exit()
            print("Arrester #%d: arrest made" % self.id)

NUM_SEARCHERS = 5
NUM_INSERTERS = 5
NUM_ARRESTERS = 1

database = Database()

for i in range(NUM_SEARCHERS):
    Searcher(i).start()

for i in range(NUM_INSERTERS):
    Inserter(i).start()

for i in range(NUM_ARRESTERS):
    Arrester(i).start()
