from __future__ import with_statement
from threading import Thread, Lock, Condition
import time, random

# Bar Wars: Greek Life Edition
#
# Three groups of the local greek life are trying to enter the bar:
# Members of the Kappa Epsilon Gamma Fraternity (Kegs)
# Members of the Delta Omnicron Gamma Fraternity (Dogs)
# Sorority Girls (Sorority Girls)
#
# Both the Kegs and the Dogs cannot stand one another as the Kegs see the
# Dogs as too preppy and the Dogs feel the Kegs are lowly alcoholics. Yet,
# both want to go out and get lucky. The sorority girls are driven by
# different motives, and will not go to the bar without some stand up
# fraternity members present to buy the girls drinks.
#
# YOUR TASK:
# Use monitor locks and condition variables to ensure that
#    (a) there are no more than N greeks inside the bar
#    (b) no Kegs enter if the bar is more than 75% Dogs
#    (c) no Dogs enter if the bar is more than 50% Kegs
#    (d) no Girls enter if the bar is not at least 10% full.
#   
# Note that b and c are relative to the amount of persons currently in
# the club while d is relative to the total capacity of the club.
#
# Fire code laws keep you from blocking
# people's exits for any reason.
#
# Note that the rules (a) through (d) above need only be
# checked upon bar entry. It is ok if a Girl enters a
# bar more than 10% full, and later some threads
# exit such that the ratio drops below 10%.
#
# Starvation is not something you need to worry about.

def hangout():
    time.sleep(random.randint(0, 2))

class Bouncer:
    def __init__(self, max_capacity):
        self.bouncerLock = Lock()
        self.totalGreeksCapacity = max_capacity
        self.totalGreeksInside = 0 
        self.nkegsInside = 0
        self.ndogsInside = 0
        self.ngirlsInside = 0
        self.nkegsWaiting = 0
        self.ndogsWaiting = 0
        self.ngirlssWaiting = 0
        self.kegsCond = Condition(self.bouncerLock)
        self.dogsCond = Condition(self.bouncerLock)
        self.girlsCond = Condition(self.bouncerLock)

    def keg_enter(self):
        with self.bouncerLock:
            while (self.totalGreeksInside >= self.totalGreeksCapacity) \
            or (self.totalGreeksInside > 0 and ((1.0*self.ndogsInside)/self.totalGreeksInside) > .75):
                self.nkegsWaiting = self.nkegsWaiting + 1
                self.kegsCond.wait()
                self.nkegsWaiting = self.nkegsWaiting - 1
            self.nkegsInside = self.nkegsInside + 1
            self.totalGreeksInside = self.totalGreeksInside + 1

    def keg_exit(self):
        with self.bouncerLock:
            self.nkegsInside = self.nkegsInside - 1
            self.totalGreeksInside = self.totalGreeksInside - 1
            if self.ndogsWaiting > 0 and (self.totalGreeksInside==0 \
                or(((1.0*self.ndogsInside)/self.totalGreeksInside) > .75)):
                self.dogsCond.notify()
            elif self.ngirlssWaiting > 0:
                self.girlsCond.notify()
            elif self.nkegsWaiting > 0:
                self.kegsCond.notify()

    def dog_enter(self):
        with self.bouncerLock:
            while (self.totalGreeksInside >= self.totalGreeksCapacity) \
            or (self.totalGreeksInside>0 and ((1.0*self.nkegsInside)/self.totalGreeksInside) > .50):
                self.ndogsWaiting = self.ndogsWaiting + 1
                self.dogsCond.wait()
                self.ndogsWaiting = self.ndogsWaiting - 1
            self.ndogsInside = self.ndogsInside + 1
            self.totalGreeksInside = self.totalGreeksInside + 1


    def dog_exit(self):
        with self.bouncerLock:
            self.ndogsInside = self.ndogsInside - 1
            self.totalGreeksInside = self.totalGreeksInside - 1
            if self.nkegsWaiting > 0 and (self.totalGreeksInside==0 \
                or (((1.0*self.ndogsInside)/self.totalGreeksInside) > .75)):
                self.kegsCond.notify()
            elif self.ngirlssWaiting > 0:
                self.girlsCond.notify()
            elif self.ndogsWaiting > 0:
                self.dogsCond.notify()

    def girl_enter(self):
        with self.bouncerLock:
            while (self.totalGreeksInside >= self.totalGreeksCapacity) \
            or (((1.0*self.totalGreeksInside)/self.totalGreeksCapacity)<.10):
                self.ngirlssWaiting = self.ngirlssWaiting + 1
                self.girlsCond.wait()
                self.ngirlssWaiting = self.ngirlssWaiting - 1
            self.ngirlsInside = self.ngirlsInside + 1
            self.totalGreeksInside = self.totalGreeksInside + 1

    def girl_exit(self):
        with self.bouncerLock:
            self.ngirlsInside = self.ngirlsInside - 1
            self.totalGreeksInside = self.totalGreeksInside - 1
            if self.nkegsWaiting > 0:
                self.kegsCond.notify()
            elif self.ndogsWaiting > 0:
                self.dogsCond.notify()
            elif self.ngirlssWaiting > 0:
                self.girlsCond.notify()

class Keg(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            bouncer.keg_enter()
            print("Keg #%d: entered" % self.id)
            hangout()
            bouncer.keg_exit()
            print("Keg #%d: exited" % self.id)

class Dog(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            bouncer.dog_enter()
            print("Dog #%d: entered" % self.id)
            hangout()
            bouncer.dog_exit()
            print("Dog #%d: exited" % self.id)

class Girl(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            bouncer.girl_enter()
            print("Girl #%d: entered" % self.id)
            hangout()
            bouncer.girl_exit()
            print("Girl #%d: exited" % self.id)

MAX_CAPACITY = 12
NUM_KEGS = 10
NUM_DOGS = 10
NUM_GIRLS = 10

bouncer = Bouncer(MAX_CAPACITY)

for i in range(NUM_KEGS):
    Keg(i).start()

for i in range(NUM_DOGS):
    Dog(i).start()

for i in range(NUM_GIRLS):
    Girl(i).start()