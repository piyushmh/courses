from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore

# Stay awake!
# You are running a simulated program of a typical cs student.
# The coffee gives the student energy, which keeps him awake.
# However, the deadline for the project is tomorrow, so the hacker 
# has been up for quite a while and consumes energy fast.
#
# Answer the following questions:
# a. When both threads terminate, what is the largest possible value
#    of how energetic the student can be? (Is it over 1000?)
# 
# Ans - Yes the value of largest possible value of how energetic student is can be over 1000. It can be till 10000 
# 
# b. When both threads terminate, what is the smallest possible value
#    of how energetic the student can be?
# Ans - (-10000)

# c. What other values can the energy level be when both threads have
#    terminated?
# Ans- The energy level can take any value from -10000 to +10000

# d. Add appropriate synchronization such that updates to students energy
#    occur in a critical section, ensuring that the energy level is
#    always at 0 when the two threads terminate.


EnergyLevel = 0
#Lock used for mutual exclusion of critical section
EnergyLock = Lock();

#These 2 locks are for making sure that the student and the coffee threads complete
#before the main thread exits.
CoffeeComplete = Lock();
StudentComplete = Lock();

class Coffee(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with EnergyLock:
            global EnergyLevel
            for i in range(10000):
                EnergyLevel += 1
        CoffeeComplete.release();


class Student(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        with EnergyLock:
            global EnergyLevel
            for j in range(10000):
                EnergyLevel -= 1
        StudentComplete.release();


CoffeeComplete.acquire();
StudentComplete.acquire();
w1 = Coffee()
w2 = Student()
w1.start()
w2.start()

#We should wait for the threads to complete executing before printing the value
CoffeeComplete.acquire();
StudentComplete.acquire();
print("The energy level is " + str(EnergyLevel))
CoffeeComplete.release();
StudentComplete.release();
