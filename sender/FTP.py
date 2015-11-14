from socket import *
import pdb
import sys
import select
import random
import time
import os

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
    client_socket.settimeout(5)
    try:
        while True:
            data,address = client_socket.recvfrom(mss+1024)
            if(data == "finish"):
                f.close()
                client_socket.close()
                print "File Downloaded"
                break
            print "receive:", int(data[0:32], 2)
            cs = checksum(data[0:32] + data[48:64] + data[64:])
            cs = '{0:016b}'.format(cs)
            if(cs == data[32:48]) & (data[48:64] == DATA_TYPR):
                # ack
                if(seq_num == int(data[0:32], 2)):
                    # ack header
                    f.write(data[64:])
                    header_seq = data[0:32]
                    header_checksum = '0000000000000000'
                    header_type = ACK_TYPE
                    head = header_seq + header_checksum + header_type
                    print "ack:", int(header_seq,2)
                    #client_socket.sendto(head, address)
                    transmit(client_socket,head,address)
                    seq_num = seq_num + mss
                else:
                    header_seq = '{0:032b}'.format(seq_num-mss)
                    header_checksum = '0000000000000000'
                    header_type = ACK_TYPE # re-ack
                    print "re-ack:", int(header_seq,2)
                    head = header_seq + header_checksum + header_type
                    #client_socket.sendto(head, address)
                    transmit(client_socket,head,address)
            else:
                print "lost"
    except timeout:
        f.close()
        if(os.stat(file_name).st_size == 0):
            print "File Downloaded Failed"
        else:
            print "File Downloaded"
        client_socket.close()
        

def rdt_send(port, mss):
    server_socket = socket(AF_INET,SOCK_DGRAM)
    server_socket.bind(('',port))
    
    # initial congestion window and timeout length
    cwd = []
    cwd_size = 6
    time_wd = []
    time_out = 0.3
    
    # get request from receiver
    file_name,addr = server_socket.recvfrom(mss)
    
    # send file
    seq_num = 0
    try:
        f = open(file_name, "rb")
    except:
        print "File not exist!"
        return
    data = f.read(mss)
    while(data) or (len(cwd) != 0):
        if(len(cwd) < cwd_size) and (data):
            # add header
            header_seq = '{0:032b}'.format(seq_num)
            header_type = DATA_TYPR
            header_checksum = checksum(header_seq + header_type + data)
            header_checksum = '{0:016b}'.format(header_checksum)
            header = header_seq + header_checksum + header_type
            data = header + data
            # send message
            #server_socket.sendto(data, addr)
            transmit(server_socket,data,addr)
            time_wd.append(time.time())
            cwd.append(data)
            seq_num = seq_num + mss
            data = f.read(mss)
        # get ack
        server_socket.settimeout(0.01)
        try:
            ack,addr = server_socket.recvfrom(1024)
            server_socket.settimeout(0.01)
        except timeout:
            if(len(time_wd) > 0):
                if(time.time() - time_wd[0] > time_out):
                    time_wd = retransmit(cwd, addr, server_socket)
                    print "time out"
            continue
        try:
            print "receive ack:", int(ack[0:32], 2),"expect:", int(cwd[0][0:32], 2)
            if(ack[48:64] == ACK_TYPE):
                while(cwd[0][0:32] <= ack[0:32]):
                    cwd.remove(cwd[0])
                    time_wd.remove(time_wd[0])
        except:
            continue
    # close connection
    data = "finish"
    print "Finish transfer!"
    #server_socket.sendto(data, addr)
    transmit(server_socket,data,addr)
    server_socket.close
    f.close

def transmit(udp_socket,data,addr):
    if(not lost_packet()):
        udp_socket.sendto(data, addr)

def retransmit(cwd, addr, server_socket):
    time_wd = []
    for data in cwd:
        #server_socket.sendto(data, addr)
        transmit(server_socket,data,addr)
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

def lost_packet():
    p = random.uniform(0, 1)
    r = 0.9
    if(p > r):
        return True
    else:
        return False

