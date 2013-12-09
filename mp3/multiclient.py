#!/usr/bin/python

from __future__ import with_statement
from threading import Thread, Lock
import time, random
import socket
import datetime
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765

# This is the multi-threaded client.  This program should be able to run
# with no arguments and should connect to "127.0.0.1" on port 8765.  It
# should run a total of 1000 operations, and be extremely likely to
# encounter all error conditions described in the README.

class Synched:
    def __init__(self):
        self.lock = Lock()
        self.totalcommandssent  = 0
        self.numberofthreadsfinished = 0

    def printstring(self, s):
        with self.lock:
            print s
        pass

    def increment(self,num):
        with self.lock:
            self.totalcommandssent += num

    def readcountofthreadsfinished(self):
        with self.lock:
            return self.numberofthreadsfinished

    def readtotalcommandssent(self):
        with self.lock:
            return self.totalcommandssent

    def finishinc(self):
        with self.lock:
            self.numberofthreadsfinished +=1




messagesperclient = 10
numberofclients = 32
numberofmailrep = 3

class ClientThread(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id
        self.numcommandsverified = 0
        self.testsfailed = 0
        self.normal = 0 #0 means follow protocol, 1 means deviate
        self.timeoutresponse = "421 4.4.2 pm489 Error: timeout exceeded\n"
        self.commandtovalidresponse = {   "INIT"               :"220 pm489 SMTP CS4410MP3\n",
                                          "HELO"               :"250 pm489\n",
                                          "MAIL FROM:"         :"250 2.1.0 Ok\n",
                                          "RCPT TO:"           :"250 2.1.0 Ok\n",
                                          "DATA"               :"354 End data with <CR><LF>.<CR><LF>\n",
                                          "CONTENT"            :"NA"
                                      }
        self.validclientnames = ["piyush-S400CA", "einstein-supercomputer", "steve's-macbook", "bill's-pc"]
        self.validsenders = ["a@b","c@d","e@f", "gds@hds"]
        self.validreceivers =     ["w@x","x@y","yy@zz", "lkj@jkl"]
        self.validdataprefix =  [""]
        self.validcontent    =  ["Data1", "Data2","You can call me big data because I am supposed to be very big -jhjhfdbjhdbfjhbsbfhsbdfjkbsjfbjhsbdfjbsdjhfbhsdbfjbsjhbfjhbfjhbsjhfbsjhbfjhbsfjhbsjhbfjhsdabjfbajshbfjhbajhbfjhasbfjhbasjhfbjhsabfjhbasjhbfhjbjfbjhasbjfbasjbfjbsajhfbajhsbfjhasbfbjhasbfjhbsah"]
        self.stagetocommand = { 1 : "HELO" , 2:"MAIL FROM:", 3:"RCPT TO:", 4:"DATA", 5:"CONTENT"}
        self.commandtosuffixlist = { "HELO"               : self.validclientnames,
                                      "MAIL FROM:"   : self.validsenders,
                                      "RCPT TO:"     : self.validreceivers,
                                     "DATA"         : self.validdataprefix
                                   }

        self.invalidclientcommands = [("HELO\r\n", "501 Syntax:  HELO yourhostname\n"),(" \r\n", "502 5.5.2 Error: command not recognized\n"),("HELO bad client\r\n","501 Syntax:  HELO yourhostname\n")]
        self.invalidsendercommands = [("MAIL FROM : \r\n", "501 Syntax:  MAIL FROM: valid-email\n"),("MAIL FROM : a@ b\r\n","504 5.5.2 a@ b: Sender address rejected\n"),("MAIL\r\n","502 5.5.2 Error: command not recognized\n")]
        self.invalidreceivercommands = [("RCPT TO : \r\n", "501 Syntax:  RCPT TO: valid-email\n"),("RCPT TO : a@ b\r\n","504 5.5.2 a@ b: Recipient address invalid\n"),("RCPT\r\n","502 5.5.2 Error: command not recognized\n"),("MAIL FROM : sachin\r\n","503 5.5.1 Error: nested MAIL command\n")]
        self.invaliddatacommands = [(" \r\n","502 5.5.2 Error: command not recognized\n"),("DATA crap\r\n","501 Syntax:  DATA\n"),("MAIL FROM : God\r\n","503 5.5.1 Error: nested MAIL command\n")]

        self.commandtoinvalidcommandmap = { "HELO"        : self.invalidclientcommands,
                                            "MAIL FROM:"  : self.invalidsendercommands,
                                               "RCPT TO:"    : self.invalidreceivercommands,
                                            "DATA"        : self.invaliddatacommands
                                          }

    def run(self):      
        timeoutiter = random.randint(0,messagesperclient-1)
        #timeoutiter = -1
        for i in range(messagesperclient):
            if i != timeoutiter:
                val = self.mailcomplete()
                if(val==0):
                    print "Something went wrong on client number "+ str(self.id)
            else:
                self.mailtimeout()

        p.printstring("Thread "+str(self.id)+ " finished and command verified :" + str(self.numcommandsverified) + " and tests failed :" + str(self.testsfailed))
        p.increment(self.numcommandsverified)
        p.finishinc()

    '''
    Here we will randomly deviate from the protocol to test for the error
    condition and then verify the server response. Only 1 command is errorenous.
    The mail will be finally completed.
    Stages for random deviation - 
    1 - HELO
    2 - MAIL FROM
    3 - RCPT TO
    4 - DATA
    '''
    def mailcomplete(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.receiveresponseandverify(s, self.commandtovalidresponse["INIT"],0)#Initial response from the server            
        
        case = random.randint(1,3)
        #case = 3
        
        if case == 1: #this means only one mail would be sent
            deviation = random.randint(1,4)
            for stage in range(1,6):
                self.numcommandsverified +=1
                if stage == deviation:
                    self.sendinvalidcommand(s,stage)
                    self.sendvalidcommand(s,stage,1)
                else:
                    self.sendvalidcommand(s,stage,1)        

        elif case == 2: #this means multiple mails would be sent
            self.sendvalidcommand(s,1,0)
            self.numcommandsverified +=1
            for rep in range(numberofmailrep): #sending multiple mails
                deviation = random.randint(2,4)
                for stage in range(2,6):
                    self.numcommandsverified +=1
                    if stage == deviation:
                        self.sendinvalidcommand(s,stage)
                        self.sendvalidcommand(s,stage,0)
                        self.numcommandsverified +=1
                    else:
                        if(rep == numberofmailrep-1 and stage == 5):
                            self.sendvalidcommand(s,stage,1)                            
                        else:
                            self.sendvalidcommand(s,stage,0)
  
        elif case == 3: #this means client will send everything at one and terminate prematurely
            finalcommand = ""
            for stage in range(1,6):
                self.numcommandsverified +=1
                command,suffix = self.generatevalidcommand(stage)
                finalcommand += command
            #print repr(finalcommand)
            self.sendcommand(s, finalcommand)

        s.shutdown(socket.SHUT_RDWR)
        s.close()


    '''Here we will randomly choose a stage and time out'''
    def mailtimeout(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        case = random.randint(1,5)
        self.receiveresponseandverify(s, self.commandtovalidresponse["INIT"],0)#Initial response from the server            
        for stage in range(1,5):
            self.numcommandsverified += 1
            if stage == case:
                #time.sleep(11)
                self.receiveresponseandverify(s, self.timeoutresponse,0)
                break
            else:
                self.sendvalidcommand(s, stage, 0)

        s.shutdown(socket.SHUT_RDWR)
        s.close()


    def sendvalidcommand(self,s, stage, flag):
        command,suffix = self.generatevalidcommand(stage)
        #p.printstring("Starting stage:" + str(stage))
        #p.printstring("command:" + repr(command))
        self.sendcommand(s, command)
        expected = self.commandtovalidresponse[self.stagetocommand[stage]]
        val = self.receiveresponseandverify(s, expected,flag)
        if( val==0):
            return 0
        else:
            #p.printstring("Stage :"+str(stage)+" passed\n")
            pass


    def sendinvalidcommand(self, s, stage):
        command, response = self.generateinvalidcommand(stage)
        #p.printstring("Starting stage:" + str(stage))
        #p.printstring("command:" + repr(command))
        self.sendcommand(s,command)
        val = self.receiveresponseandverify(s, response, 0)
        if( val==0):
            return 0
        else:
            #p.printstring("Stage :"+str(stage)+" passed\n")
            pass


    def generatevalidcommand(self, stage):
        if stage == 5:
            content = self.validcontent[random.randint(0,len(self.validcontent)-1)]
            content += "\r\n.\r\n"
            return content,""
        else:    
            command = self.stagetocommand[stage]
            suffixlist = self.commandtosuffixlist[command] 
            r = random.randint(0, len(suffixlist)-1)
            suffix = suffixlist[r]
            finalcommand  = command + " " + suffix
            finalcommand += "\r\n"
            return (finalcommand, suffix)

    #This method returns both an invalid command and an appropriate error code, beware warrior!!
    def generateinvalidcommand(self, stage):
        if stage == 5:
            print "Should not be here bro"

        command = self.stagetocommand[stage]
        invalidcommandlist = self.commandtoinvalidcommandmap[command]
        r = random.randint(0, len(invalidcommandlist)-1)
        command, response = invalidcommandlist[r]
        return command, response

    def sendcommand(self, socket, command):
         socket.send(command.encode('utf-8'))

    def receiveresponseandverify(self,socket, expectedresponse, flag):
        if flag and expectedresponse == "NA":
            return 1
        s = socket.recv(500)
        #p.printstring("Response:"+repr(s))
        #p.printstring("expected:"+ repr(expectedresponse))
        if expectedresponse == "NA":
            return 1
        if s == expectedresponse:
            return 1
        else:
            self.testsfailed += 1 
            p.printstring("Client "+ str(self.id) + " got bad response, expected :" + expectedresponse)
            return 0


p = Synched()
for i in range(numberofclients):
    worker  = ClientThread(i+1)
    worker.start()

while(1):
    if(p.readcountofthreadsfinished()==numberofclients):
        print "Total commands sent by multiclient.py :" +str(p.readtotalcommandssent())
        break
