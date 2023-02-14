'''
CS435 LurkDragon: Server
    Author: Logan Hunter Gray
    Email: lhgray@lcmail.lcsc.edu
    KNOWN ISSUES
        Reevaluate how bind works
            Currently using localhost, trying to use gethostname() for address causing stuff to fail on isoptera
                Pretty sure this is an issue with my understanding of bind() and gethostname(), rather than isoptera issue
        Does not handle client abruptly ending connection
'''

#!/usr/bin/env python3

# Import socket module, necessary for network communications
import socket
# Import threading module, required for multithreading & handling multiple clients
import threading

# Import custom lurk module
from lurk import *

# Function for handling individual clients
#   cSkt: Client socket to handle
def handleClient(cSkt):
    version = Version.sendVersion(cSkt)
    if (version != 0):
        print('WARN: sendVersion() returned unexpected code', version, 'for client', cSkt)
        return 2
    game = Game.sendGame(cSkt)
    if (game != 0):
        print('WARN: sendGame() returned unexpected code', game, 'for client', cSkt)
        return 2
    while True:
        buffer = b''                                        # I think this method breaks if recv receives more than one message into buffer
        buffer = cSkt.recv(4096)
        if (buffer != b'' and buffer[0] == 1):
            # Handle MESSAGE
            pass
        elif (buffer != b'' and buffer[0] == 2):
            # Handle CHANGEROOM
            pass
        elif (buffer != b'' and buffer[0] == 3):
            # Handle FIGHT
            pass
        elif (buffer != b'' and buffer[0] == 4):
            # Handle PVPFIGHT
            pass
        elif (buffer != b'' and buffer[0] == 5):
            # Handle LOOT
            pass
        elif (buffer != b'' and buffer[0] == 6):
            # Handle START
            startBuffer = buffer
            msgType = Start.recvStart(cSkt, startBuffer)
            continue
        elif (buffer != b'' and buffer[0] == 7):
            # Handle ERROR
            errorBuffer = buffer
            error = Error.recvError(cSkt, errorBuffer)
            continue
        elif (buffer != b'' and buffer[0] == 8):
            # Handle ACCEPT
            acceptBuffer = buffer
            accept = Accept.recvAccept(cSkt, acceptBuffer)
            continue
        elif (buffer != b'' and buffer[0] == 9):
            # Handle ROOM
            pass
        elif (buffer != b'' and buffer[0] == 10):
            # Handle CHARACTER
            characterBuffer = buffer
            name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = Character.recvCharacter(cSkt, characterBuffer)
            
            # If stats and CHARACTER message is valid, send ACCEPT
            if (attack + defense + regen <= Game.initPoints):
                print('DEBUG: Detected valid stats, sending ACCEPT!')
                accept = Accept.sendAccept(cSkt, 10)
                room = Room.sendRoom(cSkt, 0)
            else:
                print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                error = Error.sendError(cSkt, 4)
            continue
        
        elif (buffer != b'' and buffer[0] == 11):
            # Handle GAME
            pass
        elif (buffer != b'' and buffer[0] == 12):
            # Handle LEAVE
            cSkt.shutdown(2)    # Not necessary AFAIK, testing
            cSkt.close(cSkt)        # Close connection to server
        elif (buffer != b'' and buffer[0] == 13):
            # Handle CONNECTION
            pass
        elif (buffer != b'' and buffer[0] == 14):
            # Handle VERSION
            pass
        else:
            continue


# Create dictionary to track connected clients
clients = {}

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign address & port number
# Logan's assigned range: 5010 - 5014
# Testing 5195 for isoptera, connection refused on assigned ports...
address = '0.0.0.0'
port = 5010

# Bind server to machine's assigned address & port number
serverSkt.bind((address, port))

# Server listens and queues up connections
serverSkt.listen()
print('DEBUG: Listening on address:', address, 'port:', port)

while True:
    clientSkt, clientAddr = serverSkt.accept()                                                      # Accept & assign client socket & address
    #print('DEBUG: Client Socket:', clientSkt)
    #print('DEBUG: Client Address:', clientAddr)

    clients[clientSkt] = clientSkt.fileno()                                                         # Add file descriptor to dictionary for tracking connections
    #print('DEBUG: Connected Clients: ', clients)

    clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()    # Create thread for connected client and starts it
    #print("DEBUG: Client Thread:", clientThread)