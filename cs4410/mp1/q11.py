from __future__ import with_statement
from threading import Thread, Lock, Condition

# Life emulation problem

# Scientists have discovered alien life on planet Leviche 538X.
#
# Unlike earth-based lifeforms, Levicheans have three genders, he, she and it.
#
# On reaching adulthood, Levichean organisms go to a mating area in search of
# other Levicheans. When a Levichean of one gender comes together with two
# other Levicheans of the other two genders (for example, a she runs into a he
# and an it) in this area, they form a lifelong physical bond and attach
# themselves into a triad. Once in a triad, Levicheans leave the mating area
# and are not eligible to form bonds with other Levicheans. As an earth
# scientist, you have been tasked with simulating the mating habits of the
# Levicheans, using threads, monitors and condition variables. Each Levichean
# is modeled by a thread. Fill in the missing code segments below such that
#`
# a) the Levichean triad formation is modeled according to the specification
# above, paying special attention to make sure that the three-way join is
# simulated correctly,
#
# b) the code makes forward progress whenever possible to do so (i.e. your
# simulation should accommodate every mating opportunity that is present on
# Leviche 538X.

class MatingArea:
    def __init__(self):
        self.maLock = Lock()
        self.nheWaiting = 0
        self.nsheWaiting = 0
        self.nitWaiting = 0
        self.nheTaken = 0 
        self.nsheTaken = 0
        self.nitTaken = 0
        self.heCond = Condition(self.maLock)
        self.sheCond = Condition(self.maLock)
        self.itCond = Condition(self.maLock)

    def he_ready(self):
        with self.maLock:
          while self.nheTaken == 0 and (self.nsheWaiting == 0 or self.nitWaiting == 0) :
            self.nheWaiting = self.nheWaiting + 1
            self.heCond.wait()
            self.nheWaiting = self.nheWaiting - 1

          if(self.nheTaken > 0):
            self.nheTaken = self.nheTaken - 1
          else: # this means second condition was false, can form a triad now
            self.nsheTaken = self.nsheTaken + 1
            self.nitTaken = self.nitTaken + 1
            self.sheCond.notify()
            self.itCond.notify()

    def she_ready(self):
        with self.maLock:
          while self.nsheTaken == 0 and (self.nheWaiting == 0 or self.nitWaiting == 0):
            self.nsheWaiting = self.nsheWaiting + 1
            self.sheCond.wait()
            self.nsheWaiting = self.nsheWaiting - 1

          if self.nsheTaken > 0:
            self.nsheTaken = self.nsheTaken - 1
          else:
            self.nheTaken += 1
            self.nitTaken += 1
            self.heCond.notify()
            self.itCond.notify()

    def it_ready(self):
        with self.maLock:
          while self.nitTaken == 0 and (self.nheWaiting == 0 or self.nsheWaiting == 0):
            self.nitWaiting = self.nitWaiting + 1
            self.itCond.wait()
            self.nitWaiting = self.nitWaiting - 1

          if self.nitTaken > 0:
            self.nitTaken = self.nitTaken - 1
          else:
            self.nheTaken += 1
            self.nsheTaken += 1
            self.heCond.notify()
            self.sheCond.notify()


ma = MatingArea()
printLock = Lock()
class he(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with printLock:
            print("He: I'm born!")
        # grow up
        with printLock:
            print("He: Adult now, time to form a triad!")
        ma.he_ready()
        # the code should never get here unless this organism
        # is in a triad
        with printLock:
            print("He: Yay, I'm part of a triad!!!")
        # lives happily ever after, sends laser pulses into
        # space towards earth.

class she(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with printLock:
            print("She: I'm born!")
        # grow up
        with printLock:
            print("She: Adult now, time to form a triad!")
        ma.she_ready()
        # the code should never get here unless this organism
        # is in a triad
        with printLock:
            print("She: Yay, I'm part of a triad!!!")
        # lives happily ever after, sends laser pulses into
        # space towards earth.

class it(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with printLock:
            print("It: I'm born!")
        # grow up
        with printLock:
            print("It: Adult now, time to form a triad!")
        ma.it_ready()
        # the code should never get here unless this organism
        # is in a triad
        with printLock:
            print("It: Yay, I'm part of a triad!!!")
        # lives happily ever after, sends laser pulses into
        # space towards earth.

for i in range(1):
    m = he()
    m.start()
for i in range(1):
    f = she()
    f.start()
for i in range(100):
    n = it()
    n.start()
