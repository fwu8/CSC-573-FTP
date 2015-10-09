from socket import *
import pdb
import time

def rdt_send(port, mss):
    # sender send msg to receiver
    server_socket = socket(AF_INET,SOCK_DGRAM)
    server_socket.bind(('',port))
    
    # get request and ack, shake hands
    file_name,addr = server_socket.recvfrom(mss)
    server_socket.sendto("connection ack", addr)
    
    # send content
    seq_num = 0
    try:
        f = open(file_name, "rb")
    except:
        return
    data = f.read(mss)
    pdb.set_trace
    while(data):
        # add header
        header_seq = '{0:032b}'.format(seq_num)# add seq number
        header_type = '0101010101010101'# indicate data packet
        header_checksum = checksum(header_seq + header_type + data)
        header_checksum = '{0:016b}'.format(header_checksum)
        header = header_seq + header_checksum + header_type
        data = header + data
        # send message
        server_socket.sendto(data, addr)
        # get ack
        try:
            ack,addr = server_socket.recvfrom(64)
            server_socket.settimeout(0.1) # if timeout, need retransmit packet
        except timeout:
            print "retransmit"
            data = data[64:]
            continue
        

        if(data[0:32] == ack[0:32]) & (ack[48:64] == '1010101010101010'):
            # print seq_num
            data = f.read(mss)
            seq_num = seq_num + mss
        else:
            print "retransmit"
            data = data[64:]
    server_socket.close
    f.close

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
    port = 12000
    rdt_send(port, 1024)
