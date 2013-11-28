from threading import Thread

# a. Run the following concurrent program. Are there any particular patterns in
#    the output? Is the interleaving of the output from the two threads
#    predictable in any way?
#
# Ans -  No there are no recognizable patterns in the output. 
#        No, the interleaving of the output is not predicatable in any way. There are instances 
#        where message from worker 2 is printed many times continously and there are instances where the 
#        message from worker 1 is printed many times continously. 

# b. If the answer to part (a) is affirmative, run the same program while
#    browsing the web. Does the pattern you outlined in section (a) hold?

# Ans - No I see a different pattern everytime I run the program

# c. In general, can one rely on a particular timing/interleaving of executions
#    of concurrent processes?
# Ans - No, one cannot rely on the interleaving/timing pattern of execution of concurrent processes.
#       It purely depend upon the number of processes running at that time and the scheduling policy of the kernel
#
# d. Given that there are no synchronization operations in the code below, any
#    interleaving of executions should be possible. When you run the code, do
#    you believe that you see a large fraction of the possible interleavings? If
#    so, what do you think makes this possible? If not, what does this imply
#    about the effectiveness of testing as a way to find synchronization errors?
# 
#   Ans - Yes. In general there can be a huge number of interleavings possible since there are a quite a few processes running 
#   at a time in the operating system. This implies that testing is not a effective way of finding synchronizations errors 
#   as we can never reproduce all possible interleavings while testing our code and there can be always be some more 
#   combinations which would happen on a production system

class Worker1(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            print("Hello from Worker 1")

class Worker2(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            print("Hello from Worker 2")

w1 = Worker1()
w2 = Worker2()
w1.start()
w2.start()
