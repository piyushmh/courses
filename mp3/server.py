#!/usr/bin/python

from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
import getopt
import socket
import sys
import time, random
import select
import re
import datetime
import os


# STOP!  Don't change this.  If you do, we will not be able to contact your
# server when grading.  Instead, you should provide command-line arguments to
# this program to select the IP and port on which you want to listen.  See below
# for more details.
host = "127.0.0.1"
port = 8765

def checkHELOparam(param):
    if len(param) == 0:
        return False
    search = re.search("\s+", param)
    if search:
        return False;
    else:
        return True;

def checkMAILFROMparam(param):
    if len(param) == 0:
        return -2;
    if re.search("\s+", param):
        return -1
    if len([m.start() for m in re.finditer('@', param)])!=1:
        return -1
    if re.match( "\S+@\S+", param, flags=0):
        return 1
    return -1


def checkMAILTOparam(param):
    if len(param) == 0:
        return -2;
    if re.search("\s+", param):
        return -1
    if len([m.start() for m in re.finditer('@', param)])!=1:
        return -1
    if re.match( "\S+@\S+", param, flags=0):
        return 1
    return -1

def checkDATAparam(param):
    return True


''' Exception class for time outs'''
class Timeoutexception(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

''' Exception class for when client has disconnected'''
class Clientdisconnexception(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)



class Workerthread(Thread):
    def __init__(self,id,servermonitor, connqueuemonitor, mailboxmonitor):
        Thread.__init__(self)
        self.id = id
        self.servermonitor = servermonitor
        self.connqueuemonitor = connqueuemonitor
        self.mailboxmonitor = mailboxmonitor
        self.prevleftinput = ""
        self.millisecrem = 0
        self.state = 0
        self.numberofdeliveredmessage = 0
        self.clientname = ""
        self.mailsender = ""
        self.mailreceiver = [] #Since there can be more than 1
        self.mailcontent = ""

        self.syntaxdic = {  "HELO"          :"501 Syntax:  HELO yourhostname\n",
                            "MAIL FROM"     :"501 Syntax:  MAIL FROM: valid-email\n",
                            "RCPT TO"       :"501 Syntax:  RCPT TO: valid-email\n",
                            "DATA"          :"501 Syntax:  DATA\n"
                        }

        self.validparamdic = {  "HELO"          :checkHELOparam,
                                "MAIL FROM"     :checkMAILFROMparam,
                                "RCPT TO"       :checkMAILTOparam,
                                "DATA"          :checkDATAparam
                            }
    
    
    def printthreadstate(self):
        print "Id: "+ str(self.id)
        print "prevleftinput: "+ str(self.prevleftinput)
        print "Time rem: " + str(self.millisecrem)
        print "State: " + str(self.state)
        print "Client name: " + str(self.clientname)
        print "Mailsender: " + str(self.mailsender)
        print "Rec: " + str(self.mailreceiver)
        print "Body: " + str(self.mailcontent)

    def run(self):
        #print "Thread "+str(self.id)+ " started running"
        while True:
            self.servermonitor.thread_start_serving(self.id);
            #print "Thread "+str(self.id)+ " started serving request"
            socket = self.connqueuemonitor.consumeconnection()
            self.handleclient(socket)
            #print "Thread "+str(self.id)+ " finished serving request"
    
    def findtimeelapsed(self,start,end):
        dt = end - start
        return dt.seconds*1000 + dt.microseconds/1000
    

    def clean(self):
        self.prevleftinput = ""
        self.mailreceiver = []
        self.clientname = ""
        self.mailsender = ""
        self.numberofdeliveredmessage = 0

    def resettimer(self):
        self.millisecrem = 10*1000

    def handlestate(self,socket):
        
        if self.state == 1 : #Expecting HELO clientname
            self.writetosocket(socket,"220 pm489 SMTP CS4410MP3\n")
            while True:
                command = self.receivecommand(socket, r"\r\n")
                command = command.strip()
                pattern = "HELO\s*(.*)$"
                result = re.match(pattern, command, flags=re.IGNORECASE|re.DOTALL)
                if result:
                    l = result.groups()
                    if self.validparamdic["HELO"](l[0]) == False:
                        self.writetosocket(socket,self.syntaxdic["HELO"])
                    else:
                        self.clientname = l[0]
                        break
                else:
                    self.writetosocket(socket, "502 5.5.2 Error: command not recognized\n")
            
            return 2 # 1->2


        elif self.state == 2 : #Expecting MAIL FROM:
            if self.numberofdeliveredmessage == 0: #So that this does not get printed for every message
                self.writetosocket(socket, "250 pm489\n")

            while True:
                command = self.receivecommand(socket, "\\r\\n")
                command = command.strip()
                pattern = "MAIL\s+FROM\s*:\s*(.*)$"
                result = re.match(pattern, command, flags=re.IGNORECASE|re.DOTALL)
                if result:
                    l = result.groups()
                    if self.validparamdic["MAIL FROM"](l[0]) == True:
                        self.mailsender = l[0]
                        break
                    elif self.validparamdic["MAIL FROM"](l[0]) == -1:
                        self.writetosocket(socket,"504 5.5.2 "+l[0] +": Sender address rejected\n")
                    elif self.validparamdic["MAIL FROM"](l[0]) == -2:
                        self.writetosocket(socket,self.syntaxdic["MAIL FROM"])

                else:
                    self.writetosocket(socket, "502 5.5.2 Error: command not recognized\n")

            return 3 # 2->3


        elif self.state == 3: #Expecting RCPT TO:
            self.writetosocket(socket,"250 2.1.0 Ok\n")

            while True:
                command = self.receivecommand(socket, "\\r\\n")
                command = command.strip()
                patternrecv = "RCPT\s+TO\s*:\s*(.*)$"
                patternsender = "MAIL\s+FROM\s*:\s*(.*)$"
                resultrecv = re.match(patternrecv, command, flags=re.IGNORECASE|re.DOTALL)
                resultsender = re.match(patternsender, command, flags=re.IGNORECASE|re.DOTALL)
                if resultrecv:
                    l = resultrecv.groups()
                    if self.validparamdic["RCPT TO"](l[0]) == True:
                        self.mailreceiver.append(l[0])
                        break
                    elif self.validparamdic["RCPT TO"](l[0]) == -1:
                        self.writetosocket(socket,"504 5.5.2 "+l[0]+": Recipient address invalid\n")
                    elif self.validparamdic["RCPT TO"](l[0]) == -2:
                        self.writetosocket(socket,self.syntaxdic["RCPT TO"])

                elif resultsender:
                    l = resultsender.groups()
                    self.writetosocket(socket, "503 5.5.1 Error: nested MAIL command\n")

                else:
                    self.writetosocket(socket, "502 5.5.2 Error: command not recognized\n")

            return 4 # 3->4

        elif self.state == 4: #Expecting DATA | RCPT TO:
            self.writetosocket(socket,"250 2.1.0 Ok\n")
            finalstate = 5 #this represents the final state that will be returned
            
            while True:
                command = self.receivecommand(socket, "\\r\\n")
                command = command.strip()

                patterndata = "DATA\s*(.*)$"
                patternrecv = "RCPT\s+TO\s*:\s*(.*)$"
                patternsender = "MAIL\s+FROM\s*:\s*(.*)$"
                resultdata = re.match(patterndata, command, flags=re.IGNORECASE|re.DOTALL)
                resultrecv = re.match(patternrecv, command, flags=re.IGNORECASE|re.DOTALL)
                resultsender = re.match(patternsender, command, flags=re.IGNORECASE|re.DOTALL)

                if resultdata:
                    l = resultdata.groups()
                    if len(l[0])!=0: # Invalid usage
                        self.writetosocket(socket, self.syntaxdic["DATA"])
                    else:
                        finalstate = 5
                        break

                elif resultrecv:
                    l = resultrecv.groups()
                    if self.validparamdic["RCPT TO"](l[0]) == True:
                        self.mailreceiver.append(l[0])
                        finalstate = 4
                        break
                    elif self.validparamdic["RCPT TO"](l[0]) == -1:
                        self.writetosocket(socket,"504 5.5.2 "+l[0]+": Recipient address invalid\n")
                    elif self.validparamdic["RCPT TO"](l[0]) == -2:
                        self.writetosocket(socket,self.syntaxdic["RCPT TO"])

                elif resultsender:
                    self.writetosocket(socket, "503 5.5.1 Error: nested MAIL command\n")

                else:
                    self.writetosocket(socket, "502 5.5.2 Error: command not recognized\n")

            return finalstate # 4->(4|5)


        elif self.state == 5: #Expecting actual data
            self.writetosocket(socket,"354 End data with <CR><LF>.<CR><LF>\n")
            self.mailcontent = self.receivecommand(socket, "\\r\\n.\\r\\n")
            return 6 #5->6

        elif self.state == 6: #Wait for more mails!!
            deliveredmailnumber = self.mailboxmonitor.delivermail(self.clientname, self.mailsender, self.mailreceiver, self.mailcontent) #Write to mailbox now
            self.writetosocket(socket, "250 OK: Delivered message "+ str(deliveredmailnumber)+ "\n")
            self.numberofdeliveredmessage += 1
            self.mailreceiver = []
            self.mailsender = []
            self.mailcontent = ""
            if self.checkifclientconnopen(socket) or len(self.prevleftinput)>0 :
                return 2 #6->2
            else:
                raise Clientdisconnexception("Client has disconnected")



    #This method would contain all the logic of handling request
    def handleclient(self,socket):
        
        try:
            self.clean() #remove any residual strings of previous connections
            self.resettimer() #resest timer for first command
            self.state = 1  #initial state

            nextstate = self.handlestate(socket)
            self.state = nextstate

            while True:    
                nextstate = self.handlestate(socket)
                if nextstate!=self.state: #This is so that multiple rect do not reset clock
                    self.state = nextstate
                    self.resettimer()
            
        except Timeoutexception as e:
            #print "Client connection timed out"
            self.writetosocket(socket, "421 4.4.2 pm489 Error: timeout exceeded\n")
            socket.close()
        except Clientdisconnexception as e:
            #print "Client has disconnected, not waiting!!"
            socket.close()



    def receivecommand(self,socket, delimiter):
        retcommand  = ""
        currinput = self.prevleftinput
        while True:
            pattern = "(.*?)" + delimiter + "(.*)"
            result = re.match(pattern, currinput, flags=re.DOTALL)
            if result:
                l = result.groups()
                retcommand = l[0]
                self.prevleftinput = l[1] #this might be empty
                break
            
            else: 
                start = datetime.datetime.now()
                readcommand = self.readfromsocket(socket,self.millisecrem/1000)
                end = datetime.datetime.now()
                currinput = currinput + readcommand
                self.millisecrem -= self.findtimeelapsed(start, end) #update the time rem    
                if self.millisecrem < 0:
                    raise Timeoutexception("B: Time out occured while reading from socket")

        return retcommand
        
    
    def readfromsocket(self,socket, timeoutinseconds):
        socket.setblocking(0)
        data = ""
        ready = select.select([socket], [], [], timeoutinseconds)
        if ready[0]:
            try:
                data = socket.recv(4096)
            except Exception as e:
                pass #this is possible when connection is broken by client at this point
        return data

    def writetosocket(self, socket, message):
        try:
            socket.send(message.encode('utf-8'))
        except Exception as e:
            #print "Client connection is closed, write to socket failed"
            pass

    ''' Send empty string to check if client is still open'''
    def checkifclientconnopen(self, socket):
        retval = True
        try:
            socket.send("".encode('utf-8'))
        except Exception as e:
            retval = False
        return retval



class Servermonitor:
    def __init__(self):
        self.serverlock = Lock()
        self.numberofwaitingthreads = 0
        self.numberofwaitingclients = 0
        self.waitingthreadcond = Condition(self.serverlock)
            
    def thread_start_serving(self,id):
        with self.serverlock:
            self.numberofwaitingthreads +=1
            while self.numberofwaitingclients == 0:
                self.waitingthreadcond.wait();
            self.numberofwaitingclients -=1 
    
    #User by server to find if it can serve request or not
    def checkifcanserveclient(self):
        retval = False
        with self.serverlock:
            if(self.numberofwaitingthreads > 0):
                retval = True
        return retval 
    
    #This should only be called if there are waiting threads on the condition variable
    def wakeupthread(self):
        with self.serverlock:
            self.numberofwaitingclients += 1
            self.numberofwaitingthreads -=1
            if(self.numberofwaitingthreads <0):
                print "SHITsssssssssssssssssssssssssssssssssssssss"
            self.waitingthreadcond.notify()

class ConnectionQueuemonitor:
    def __init__(self):
        self.resoucelock = Lock()
        self.connlist = [] #Simple unsynchronized list for storing socket conn

    def produceconnection(self,socket):
        with self.resoucelock:
            self.connlist.append(socket)

    def consumeconnection(self):
        with self.resoucelock:
            if( len(self.connlist) == 0):
                print "This should not have happened"
                return
            socket  = self.connlist[0]
            self.connlist = self.connlist[1:]
            return socket

class Mailboxmonitor:
    def __init__(self):
        self.mailboxlock = Lock()
        self.mailidentifier = 0
        self.fileHandle = open("mailbox", "w")
        self.backupthreadactive = 0
        self.backupthreadswaiting = 0
        self.waitingforbackuptocomplete = Condition(self.mailboxlock)
        self.backupneededcond = Condition(self.mailboxlock)

    def delivermail(self, clientname, mailsender, mailreceiver, mailcontent):
        with self.mailboxlock:
            #if back up is happening stop writes everywhere
            while self.backupthreadactive == 1:
                self.waitingforbackuptocomplete.wait()

            mail  =  "Received from " + str(clientname) + " by pm489 (CS4410MP3)\n"
            self.mailidentifier += 1
            mail +=  "Number: " + str(self.mailidentifier) + "\n"
            mail +=  "From: " + str(mailsender) + "\n"
        
            for i in range(0, len(mailreceiver)):
                mail +=  "To: " + str(mailreceiver[i]) + "\n"

            mail +=  "\n"
            mail +=  mailcontent + "\n"
            mail +=  "\n"
            while self.backupthreadactive == 1:  #if back up is happening stop writes everywhere
                print "worker sleeping"
                self.waitingforbackuptocomplete.wait()

            self.fileHandle.write(mail)
            self.fileHandle.flush()

            if self.mailidentifier%32 == 0 and self.backupthreadswaiting > 0:
                self.backupthreadactive = 1
                self.backupthreadswaiting = 0
                self.backupneededcond.notify()
            return self.mailidentifier
            

    def startbackupthread(self):
        with self.mailboxlock:
            while self.backupthreadactive==0:
                #print "backup slept"
                self.backupthreadswaiting = 1
                self.backupneededcond.wait()
        
    def initiatebackup(self, lastbackedmessage):
        with self.mailboxlock:
            if( self.mailidentifier%32 != 0):
                print "Something went very horribly wrong"
            newfilename = "mailbox." + str(lastbackedmessage+1)+"-"+ str(lastbackedmessage+32)
            self.fileHandle.close()
            os.rename("mailbox", newfilename)
            self.fileHandle = open("mailbox", "w")
            lastbackedmessage += 32
            self.backupthreadactive = 0 
            self.waitingforbackuptocomplete.notifyAll() #wake up all waiting threads to write
            return lastbackedmessage


class Backupthread(Thread):
    def __init__(self,mailboxmonitor):
        Thread.__init__(self)
        self.mailboxmonitor = mailboxmonitor
        self.lastbackedmessage = 0

    def run(self):
        while True:
            self.mailboxmonitor.startbackupthread()
            self.lastbackedmessage = self.mailboxmonitor.initiatebackup(self.lastbackedmessage)
            #print self.lastbackedmessage


##############################################################################

# the main server loop
def serverloop(servermonitor, connectionmonitor):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # mark the socket so we can rebind quickly to this port number
    # after the socket is closed
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the local loopback IP address and special port
    serversocket.bind((host, port))
    # start listening with a backlog of 5 connections
    serversocket.listen(32)

    while True:
        if servermonitor.checkifcanserveclient(): #this check if there is any thread that can serve the request
            # accept a connection
            (clientsocket, address) = serversocket.accept()
            #print "Received connection"
            connectionmonitor.produceconnection(clientsocket) # produce connection
            servermonitor.wakeupthread() #consume connection
        
#################################################################################

# You don't have to change below this line.  You can pass command-line arguments
# -h/--host [IP] -p/--port [PORT] to put your server on a different IP/port.
opts, args = getopt.getopt(sys.argv[1:], 'h:p:', ['host=', 'port='])

for k, v in opts:
    if k in ('-h', '--host'):
        host = v
    if k in ('-p', '--port'):
        port = int(v)

print("Server coming up on %s:%i" % (host, port))

threadpoolsize = 32
server_monitor = Servermonitor()
connection_monitor = ConnectionQueuemonitor()
mailbox_monitor = Mailboxmonitor()

backupthread = Backupthread(mailbox_monitor)
backupthread.start()

for i in range(0,threadpoolsize):
    worker = Workerthread(i+1, server_monitor, connection_monitor, mailbox_monitor)
    worker.start()

serverloop(server_monitor, connection_monitor)
