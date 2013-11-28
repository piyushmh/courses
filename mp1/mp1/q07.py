from __future__ import with_statement
from threading import Thread, Lock, Condition
import time, random

# Use monitors and condition variables to simulate a (sleepy) barbershop.
#
#    A barbershop holds N customers, and M sleepy barbers
#    work on the customers. Correctness criteria are:
#
#    (a) no customers should enter the barbershop unless
#        there is room for them inside
#    (b) the barber should cut hair if there is a waiting
#        customer
#    (c) customers should enter the barbershop if there is
#        room inside
#
#    This is a sleepy town with laid back people, so strict
#    FIFO ordering of waiting customers is not a requirement.
#

def delay():
    time.sleep(random.randint(0, 2))

class BarberShop:
    def __init__(self, num_chairs):
        self.shopLock = Lock()
        self.numChairs = num_chairs
        self.nfreeBarbers = 0
        self.nwaitingCustomers = 0
        self.waitingCustomersCond = Condition(self.shopLock)
        self.waitingBarbersCond= Condition(self.shopLock)

    # check for waiting customers
    # if there are none, wait
    # if there are waiting customers, signal one
    def barber_ready_to_cut(self):
        with self.shopLock:
            self.nfreeBarbers = self.nfreeBarbers + 1
            while self.nwaitingCustomers == 0:
                self.waitingBarbersCond.wait()
            self.nwaitingCustomers = self.nwaitingCustomers - 1
            self.waitingCustomersCond.notify()
            

    # enter the barbershop if all num_chairs are not occupied
    # returns true if the customer entered successfully, and
    # false if he was turned away at the door
    def customer_enter(self):
        with self.shopLock:
            if self.numChairs <= 0:
                return False
            else:
                self.numChairs = self.numChairs - 1
                return True

    # take a seat and wait until the barber is ready to cut hair
    def customer_take_a_seat(self):
        with self.shopLock:
            self.nwaitingCustomers = self.nwaitingCustomers + 1
            while self.nfreeBarbers == 0:
                self.waitingCustomersCond.wait()
            
            self.nfreeBarbers = self.nfreeBarbers - 1 
            self.waitingBarbersCond.notify()
            self.numChairs = self.numChairs + 1


class Barber(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            print("Barber #%d: ready to cut hair" % self.id)
            barbershop.barber_ready_to_cut()
            print("Barber #%d: cutting hair" % self.id)
            delay()
            print("Barber #%d: done cutting hair" % self.id)

class Customer(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        while True:
            print("Customer #%d: has long hair" % self.id)
            if barbershop.customer_enter():
                print("Customer #%d: entered, taking a seat" % self.id)
                barbershop.customer_take_a_seat()
                print("Customer #%d: got a haircut!" % self.id)
            else:
                print("Customer #%d: turned away from the door" % self.id)
            delay()

NUM_BARBERS = 3
NUM_CUSTOMERS = 3
barbershop = BarberShop(3)

for i in range(NUM_BARBERS):
    Barber(i).start()
for i in range(NUM_CUSTOMERS):
    Customer(i).start()
