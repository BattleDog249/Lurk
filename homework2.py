'''
    Due Wednesday, February 1
    Connect to port 5071 on isoptera.
    There is a server running on that port that will send you 5 32-bit (20 bytes total) integers in big endian order.
    Upload a text file with your name, the integers isoptera sent you, and explain how you received them (include source code if you wrote it).
    You are welcome to start with the simple_client.c program from class, but you can just start your own program if you prefer. 
'''

import socket

address = 'isoptera.lcsc.edu'
port = 5071

# Length in bytes of integers to read
len = 4

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to Isoptera
skt.connect((socket.gethostbyname(address), port))

# Recieve 20 bytes, store in 32 byte buffer
bytes = skt.recv(32)
#print('Full Raw Message: ', message)

start = 1
end = 4
for byte in bytes:
    value = int.from_bytes(bytes[start:end], 'big', signed = False)
    print(value)
    start += 4
    end += 4