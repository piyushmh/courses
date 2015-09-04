from threading import Thread, Semaphore
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

# Use only semaphores

def delay():
    time.sleep(random.randint(0, 2))

#Implement me!
class bathroom:
    def __init__(self):
        self.semaToilet = Semaphore(1)
        self.semamutex = Semaphore(1)
        self.nwashers = 0

    def washer_enter(self):
        self.semamutex.acquire()
        self.nwashers = self.nwashers + 1
        if self.nwashers == 1 : #this means this is the first washer
            self.semaToilet.acquire()
        self.semamutex.release()

    def washer_exit(self):
        self.semamutex.acquire()
        self.nwashers = self.nwashers - 1
        if self.nwashers == 0:
            self.semaToilet.release()
        self.semamutex.release()

    def toilet_enter(self):
        self.semaToilet.acquire()

    def toilet_exit(self):
        self.semaToilet.release()


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
