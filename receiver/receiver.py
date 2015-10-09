from socket import *
import pdb
import sys
import select

def rdt_rcv(port, mss):
    client_socket = socket(AF_INET,SOCK_DGRAM)
    client_socket.bind(('',port))
    data,address = client_socket.recvfrom(mss)# receive file_name from server
    client_socket.sendto("title ack",address)# ack to file_name
    
    print "Received File:",data.strip()
    f = open(data.strip(),"wb")# open file
    
    # start receive data
    seq_num = 0
    data,address = client_socket.recvfrom(mss+64)
    client_socket.settimeout(3)
    try:
        while(data):
            cs = checksum(data[0:32] + data[48:64] + data[64:])
            cs = '{0:016b}'.format(cs)
            if(cs == data[32:48]) & (data[48:64] == '0101010101010101'):
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
            client_socket.settimeout(3)
            data,address = client_socket.recvfrom(mss+64)
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
        
if __name__ == '__main__':
    port = 16003;
    rdt_rcv(port, 1024)
