NETID - pm489


server.py
*********

Server is a multi threaded state machine which uses monitors to achieve synchronization. I have used three monitors in my implementation -

1) Server monitor - Tis monitor encapsulated all the shared variables,condition variables and locks used to make threads sleep when there are no clients and to notify threads when there are clients.

2) ConnectionQueue monitor - This monitor controls acccess to the list used to pass connections between server loop and threads. This would be the buffer in the consumer producer problem

3) Mailbox monitor - This monitor encapsulates all access to the mailbox file handler. It ensured that the threads are writing to the file in a synchronized fashion.


multiclient.py 
**************

This file does stress testing by simulateously spawning 32 clients which would connect to the server. The number of threads can be controlled by a variable - "numberofclients". In all with its current settings it completes around 2500 commands in 12-15 seconds. It contains a set of valid and invalid comamands and their responses in a mix of lists and dictionaries. It then randomly picks up any valid or invalid command and verifies the server response. It operates as follows :
The threads randomly chooses to either time out or complete successfully. Every threads sends a fixed number of messaged controlled by a variable called "messagesperclient"

a) Complete successfully - If a thread chooses to complete successfully, it can do it in 3 ways - 
	
	1) Send one successful mail and exit - In this the thread randomly chooses one stage in which to deviate from the protocol. It send all correct commands and verifies the response. Then it randomly deviates from the protocol and then verified the error response code. This information is stored in predefined dictionary data structures. It then sends the correct command and completes successfully

	2) Send multiple mails in one connection and exit - In this the thread sends multiple mails using the same connection. It randomly chooses to deviate from the protocol and verifies the server response both in the case of a correct and an incorrect command. The number of mails send it one connection can be controlled by changing a variable called "numberofmailrep"

	3) Send everything at once and terminate prematurely - In this the thread randomly generates a complete message from a set of predefined correct commands and arguments. It then sends everything at one go and terminates prematurely. 

b) Time out - The threads starts by sending a set of valid commands and verifying the response. It then choose a command randomly and does not send that command. It then waits for the server to time it out and verifies the response code.


Extra Credit
************

Back up thread - This back up thread is woken up by the worker thread whenever the mail message id become a multiple of 32. It then stops all theads from writing into the mailbox and creates a back up file for them mailbox and empties the current mail box. It then notifies all the worker threads to resume their operation. In this way it does not interfere with the working of the threads serving the clients.