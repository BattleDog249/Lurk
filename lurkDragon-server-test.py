#!/usr/bin/env python3

from serverlibtest import *

class Server:
    """Class for tracking, finding, adding, and removing clients"""
    clients = {}
    characters = {}
    monsters = {}
    rooms = {}
    conenctions = {}
    def addClient(skt):
        Server.clients[skt] = skt.fileno()              # Add file descriptor to dictionary for tracking connections
        print('DEBUG: Added Client: ', Server.clients[skt])
    def removeClient(skt):
        print('DEBUG: Removing Client: ', Server.clients[skt])
        Server.clients.pop(skt)
        #print('DEBUG: Connected Clients:', Client.clients)
    def getClients():                   # Pull list of all connected clients
        return Server.clients
    def getClient(skt):                 # Pull information on specified client
        return Server.clients[skt]

def handleClient(skt):
    while True:
        try:
            messages = lurkRecv(skt)
        except:
            break
        print('DEBUG: List of Messages:', messages)
        for message in messages:
            msgType = message[0]
            print('DEBUG: Type:', msgType)
            
            if (msgType == MESSAGE):
                msgLen = message[1]
                print('DEBUG: Message Length:', msgLen)
                recvName = message[2]
                print('DEBUG: Recipient Name:', recvName)
                sendName = message[3]
                print('DEBUG: Sender Name:', sendName)
                narration = message[4]
                print('DEBUG: End of sender Name or narration marker:', narration)
                message = message[5]
                print('DEBUG: Message:', message)
                continue
            
            elif (msgType == CHANGEROOM):
                desiredRoomNum = message[1]
                print('DEBUG: desiredRoomNum:', desiredRoomNum)
                continue
            
            elif (msgType == FIGHT):
                continue
            
            elif (msgType == PVPFIGHT):
                targetName = message[1]
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (msgType == LOOT):
                targetName = message[1]
                print('DEBUG: targetName:', targetName)
                continue
            
            elif (msgType == START):
                continue
            
            elif (msgType == ERROR):
                errCode = message[1]
                print('DEBUG: errCode:', errCode)
                errMsgLen = message[2]
                print('DEBUG: errMsgLen:', errMsgLen)
                errMsg = message[3]
                print('DEBUG: errMsg:', errMsg)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = Error.sendError(skt, 0)
                continue
            
            elif (msgType == ACCEPT):
                acceptedMsg = message[1]
                print('DEBUG: acceptedMsg:', acceptedMsg)
                continue
            
            elif (msgType == ROOM):
                roomNum = message[1]
                print('DEBUG: roomNum:', roomNum)
                roomName = message[2]
                print('DEBUG: roomName:', roomName)
                roomDesLen = message[3]
                print('DEBUG: roomDesLen:', roomDesLen)
                roomDes = message[4]
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = Error.sendError(skt, 0)
                continue
            
            elif (msgType == CHARACTER):
                name = message[1]
                print('DEBUG: Name:', name)
                flags = message[2]
                print('DEBUG: Flags:', flags)
                attack = message[3]
                print('DEBUG: Attack:', attack)
                defense = message[4]
                print('DEBUG: Defense:', defense)
                regen = message[5]
                print('DEBUG: Regen:', regen)
                health = message[6]
                print('DEBUG: Health:', health)
                gold = message[7]
                print('DEBUG: Gold:', gold)
                room = message[8]
                print('DEBUG: Room:', room)
                charDesLen = message[9]
                print('DEBUG: charDesLen:', charDesLen)
                charDes = message[10]
                print('DEBUG: charDes:', charDes)
                
                if (attack + defense + regen > Game.initPoints):
                    print('WARN: Character stats invalid, sending ERROR code 4!')
                    error = Error.sendError(skt, 4)
                    return 3
                
                accept = Accept.sendAccept(skt, msgType)
                
                if (name in Character.characters):
                    print('INFO: Existing character found, reprising!')
                    character = Character.getCharacter(name)
                    character = Character.sendCharacter(skt, name)
                    # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                    continue
                
                print('INFO: Adding new character to world!')
                character = Character.characters.update({name: [0x58, attack, defense, regen, 100, 0, 0, charDesLen, charDes]})
                character = Character.sendCharacter(skt, name)
                # Send MESSAGE to client from narrator that the character has joined the game here, perhaps?
                continue
            
            elif (msgType == GAME):
                initPoints = message[1]
                print('DEBUG: initPoints:', initPoints)
                statLimit = message[2]
                print('DEBUG: statLimit:', statLimit)
                gameDesLen = message[3]
                print('DEBUG: gameDesLen:', gameDesLen)
                gameDes = message[4]
                print('DEBUG: gameDes:', gameDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = Error.sendError(skt, 0)
                continue
            
            # Probably needs some work and potential error handling, alongside returning something useful rather than continue?
            elif (msgType == LEAVE):
                Client.removeClient(skt)
                skt.shutdown(2)
                skt.close()
                continue
            
            elif (msgType == CONNECTION):
                roomNum = message[1]
                print('DEBUG: roomNum:', roomNum)
                roomName = message[2]
                print('DEBUG: roomName:', roomName)
                roomDesLen = message[3]
                print('DEBUG: roomDesLen:', roomDesLen)
                roomDes = message[4]
                print('DEBUG: roomDes:', roomDes)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = Error.sendError(skt, 0)
                continue
            
            elif (msgType == VERSION):
                major = message[1]
                print('DEBUG: major:', major)
                minor = message[2]
                print('DEBUG: minor:', minor)
                extSize = message[3]
                print('DEBUG: extSize:', extSize)
                
                print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
                error = Error.sendError(skt, 0)
                continue
    # Cleanup disconencted client routine goes here

# Establish IPv4 TCP socket
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if serverSkt == -1:
    print('ERROR: Server socket error!')
    exit

# Assigned range: 5010 - 5014
address = '0.0.0.0'
port = 5010

serverSkt.bind((address, port))

serverSkt.listen()
print('DEBUG: Listening on address:', address, 'port:', port)

while True:
    clientSkt, clientAddr = serverSkt.accept()
    
    version = Version.sendVersion(clientSkt)
    game = Game.sendGame(clientSkt)
    
    if (version == 0 and game == 0):
        Client.addClient(clientSkt)
        clientThread = threading.Thread(target=handleClient, args=(clientSkt,), daemon=True).start()
    else:
        print('ERROR: VERSION & GAME message failed somehow!')