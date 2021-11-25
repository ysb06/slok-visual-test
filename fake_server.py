import socket
import time
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)

data_1 = 999.0
data_2 = 1

count = 0
while True:
    if count > 10:
        if data_2 == 1:
            data_2 = 0
        else:
            data_2 = 1
            
        count = 0

    message = struct.pack('d', data_1) + struct.pack('d', data_2)
    # print(list(message))

    server.sendto(message, ('<broadcast>', 2222))
    print(f'Sended: {message}')
    
    count += 1
    time.sleep(0.1)