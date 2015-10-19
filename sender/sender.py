from socket import *
import pdb
import time
import FTP as ftp

if __name__ == '__main__':
    port = 12005
    ftp.rdt_send(port, 1024)
