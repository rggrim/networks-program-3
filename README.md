**CSC4200 Networks Program 3**


The server (we name it lightserver) takes two arguments:
$ lightserver -p <PORT> -s <LOG FILE LOCATION> 
    1. The server must open a UDP socket on the specified port number
    2. The server should gracefully process incorrect port number and exit with a non-zero error code
    3. The server runs indefinitely - it does not exit.

The client (we name it lightclient) takes three arguments:
$ lightclient -s <SERVER-IP> -p <PORT> -l LOGFILE 


Sequence Number (32 bits): If SYN is present (the S flag is set) the sequence number is the initial sequence number (randomly choosen).
Acknowledgement Number (32 bits): If the ACK bit is set, this field contains the value of the next sequence number the sender of the segment is expecting to receive. Once a connection is established this is always sent.
The acknowledgement number is given in the unit of bytes (how many bytes you have sent)
Not Used (29 bits): Must be zero.
A (ACK, 1 bit): Indicates that there the value of Acknowledgment Number field is valid
S (SYN, 1 bit): Synchronize sequence numbers
F (FIN, 1 bit): Finish, No more data from sender

1. implement random function (so import random library from python) to randomly generate a sequence number at the beginning of the client ??? 
    - sequenceNumber = random.randint(0, 2147483647)
    - acknowledgementNumber = 0
    - notUsed = 0
    - ACK = 'N'
    - SYN = 'Y'
    - FIN = 'N'