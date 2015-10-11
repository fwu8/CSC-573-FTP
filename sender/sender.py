from socket import *
import pdb
import time

def rdt_send(port, mss):
    # sender send msg to receiver
    server_socket = socket(AF_INET,SOCK_DGRAM)
    server_socket.bind(('',port))
    
    # set congestion window
    cwd = []
    cwd_size = 6

    # set time out
    time_wd = []
    time_out = 0.5
    
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
    while(data):
        if(len(cwd) < cwd_size):
            # add header
            header_seq = '{0:032b}'.format(seq_num)# add seq number
            header_type = '0101010101010101'# indicate data packet
            header_checksum = checksum(header_seq + header_type + data)
            header_checksum = '{0:016b}'.format(header_checksum)
            header = header_seq + header_checksum + header_type
            data = header + data
            # send message
            server_socket.sendto(data, addr)
            time_wd.append(time.time())
            cwd.append(data)
            seq_num = seq_num + mss
            data = f.read(mss)
        # get ack
        server_socket.settimeout(0.01)
        try:
            ack,addr = server_socket.recvfrom(64)
            server_socket.settimeout(0.01)
        except timeout:
            if(len(time_wd) > 0):
                if(time.time() - time_wd[0] > time_out):
                    time_wd = retransmit(cwd, addr, server_socket)
                    print "time out"
            continue
        
        print "receive ack:", int(ack[0:32], 2),"expecting ack:", int(cwd[0][0:32], 2)
        if(cwd[0][0:32] == ack[0:32]) & (ack[48:64] == '1010101010101010'):
            cwd.remove(cwd[0])
            time_wd.remove(time_wd[0])
        
    data = "over"
    server_socket.sendto(data, addr)
    server_socket.close
    f.close

def retransmit(cwd, addr, server_socket):
    time_wd = []
    for data in cwd:
        server_socket.sendto(data, addr)
        time_wd.append(time.time())
    return time_wd

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
    port = 12003
    rdt_send(port, 1024)
