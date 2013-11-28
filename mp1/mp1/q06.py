from __future__ import with_statement
from threading import Thread, Semaphore
import time, random

# Use semaphores to simulate a (sleepy) barbershop.
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
        self.ncustomersWaiting = Semaphore(0)
        self.semaChairs = Semaphore(num_chairs)# number of vacant chairs in barber shop
        self.nbarbers = Semaphore(0)

    # check for waiting customers
    # if there are none, wait
    # if there are waiting customers, signal one
    def barber_ready_to_cut(self):
        self.ncustomersWaiting.acquire()
        self.nbarbers.release()

    # enter the barbershop if all num_chairs are not occupied
    # returns true if the customer entered successfully, and
    # false if he was turned away at the door
    def customer_enter(self):
        if self.semaChairs.acquire(False) : 
            return True
        else :
            return False

    # take a seat and wait until the barber is ready to cut hair
    def customer_take_a_seat(self):
        self.ncustomersWaiting.release() # Since release is done first, deadlock won't occur with barber
        self.nbarbers.acquire()
        self.semaChairs.release()
        

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

NUM_BARBERS = 1
NUM_CUSTOMERS = 6
barbershop = BarberShop(3)

for i in range(NUM_BARBERS):
    Barber(i).start()
for i in range(NUM_CUSTOMERS):
    Customer(i).start()
