from socket import *
import pdb
import sys
import select
import random 

def rdt_rcv(address, port, file_name, mss):
    client_socket = socket(AF_INET,SOCK_DGRAM)

    # ask server for file, shake hands
    client_socket.sendto(file_name, (address, port))
    client_socket.settimeout(3)
    try:
        ack,addr = client_socket.recvfrom(mss)
        while(ack != "connection ack"):
            client_socket.sendto(file_name, (address, port))
            ack,addr = client_socket.recvfrom(mss)
            client_socket.settimeout(3)
    except timeout:
        return
    # open file and start receive
    print "Received File:",file_name
    f = open(file_name,"wb")# open file
    
    # start receive data
    seq_num = 0
    data,address = client_socket.recvfrom(mss+1024)
    while(data):
        if(data == "over"):
            f.close()
            client_socket.close()
            print "File Downloaded"
            break;
        cs = checksum(data[0:32] + data[48:64] + data[64:])
        cs = '{0:016b}'.format(cs)
        if(cs == data[32:48]) & (data[48:64] == '0101010101010101') & discard():
            # ack
            if(seq_num == int(data[0:32], 2)):
                # ack header
                f.write(data[64:])
                header_seq = data[0:32]
                header_checksum = '0000000000000000'
                header_type = '1010101010101010' # ack
                head = header_seq + header_checksum + header_type
                # print seq_num
                client_socket.sendto(head, address)
                seq_num = seq_num + mss
                print seq_num
            else:
                header_seq = '{0:032b}'.format(seq_num-mss)
                header_checksum = '0000000000000000'
                header_type = '1010101010101010' # ack
                head = header_seq + header_checksum + header_type
                # print seq_num
                client_socket.sendto(head, address)
        data,address = client_socket.recvfrom(mss+1024)
        

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def discard():
    p = random.uniform(0, 1)
    r = 0.01
    if(p > r):
        return True
    else:
        return False

if __name__ == '__main__':
    address = "localhost"
    port = 12003
    rdt_rcv(address, port, "Lecture 2.pdf", 1024)
