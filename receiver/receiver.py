from socket import *
import pdb
import sys
import select
import random
import FTP as ftp

if __name__ == '__main__':
    address = "localhost"
    port = 7778
    myport = 7770
    try:
        ftp.rdt_rcv(address, port, "Lecture 3.pdf", 1024, myport)
    except:
        print "Connection Failed!"
