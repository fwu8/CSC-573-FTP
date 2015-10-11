from socket import *
import pdb
import sys
import select
import random 

ACK_TYPE = '1010101010101010'
DATA_TYPR = '0101010101010101'

def rdt_rcv(address, port, file_name, mss):
    client_socket = socket(AF_INET,SOCK_DGRAM)

    # ask server for file
    client_socket.sendto(file_name, (address, port))
    
    # open file and start receive data
    print "Receiving File:",file_name
    f = open(file_name,"wb")
    seq_num = 0
    data,address = client_socket.recvfrom(mss+1024)
    client_socket.settimeout(1)
    try:
        while(data):
            if(data == "finish"):
                f.close()
                client_socket.close()
                print "File Downloaded"
                break;
            print "receive:", int(data[0:32], 2)
            cs = checksum(data[0:32] + data[48:64] + data[64:])
            cs = '{0:016b}'.format(cs)
            if(cs == data[32:48]) & (data[48:64] == DATA_TYPR) & lost_packet():
                # ack
                if(seq_num == int(data[0:32], 2)):
                    # ack header
                    f.write(data[64:])
                    header_seq = data[0:32]
                    header_checksum = '0000000000000000'
                    header_type = ACK_TYPE
                    head = header_seq + header_checksum + header_type
                    print "ack:", int(header_seq,2)
                    client_socket.sendto(head, address)
                    seq_num = seq_num + mss
                else:
                    header_seq = '{0:032b}'.format(seq_num-mss)
                    header_checksum = '0000000000000000'
                    header_type = ACK_TYPE # re-ack
                    print "re-ack:", int(header_seq,2)
                    head = header_seq + header_checksum + header_type
                    client_socket.sendto(head, address)
            else:
                print "lost"
            data,address = client_socket.recvfrom(mss+1024)
    except timeout:
        f.close()
        client_socket.close()
        print "File Downloaded"

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def lost_packet():
    p = random.uniform(0, 1)
    r = 0.1
    if(p > r):
        return True
    else:
        return False

if __name__ == '__main__':
    address = "localhost"
    port = 12003
    rdt_rcv(address, port, "Lecture 2.pdf", 1024)
