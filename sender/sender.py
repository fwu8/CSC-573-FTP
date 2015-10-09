from socket import *
import pdb
import time

def rdt_send(address, port, file_name, mss):
    # sender send msg to receiver
    server_socket = socket(AF_INET,SOCK_DGRAM)
    
    # send title
    server_socket.sendto(file_name, (address, port))
    ack,addr = server_socket.recvfrom(mss)
    while(ack != "title ack"):
        server_socket.sendto(file_name, (address, port))
        ack,addr = server_socket.recvfrom(mss)
    
    # send content
    seq_num = 0
    f = open(file_name, "rb")
    data = f.read(mss)
    while(data):
        # add header
        header_seq = '{0:032b}'.format(seq_num)# add seq number
        header_type = '0101010101010101'# indicate data packet
        header_checksum = checksum(header_seq + header_type + data)
        header_checksum = '{0:016b}'.format(header_checksum)
        header = header_seq + header_checksum + header_type
        data = header + data
        # send message
        server_socket.sendto(data,(address, port))
        # get ack
        try:
            ack,addr = server_socket.recvfrom(64)
            server_socket.settimeout(0.1) # if timeout, need retransmit packet
        except timeout:
            data = data[64:]
            continue
        if(data[0:32] == ack[0:32]):
            print seq_num
            data = f.read(mss)
            seq_num = seq_num + mss
        else:
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
    address = "localhost"
    port = 16003
    rdt_send(address, port, "Lecture 3.pdf", 1024)
