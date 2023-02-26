from lurklib import *
import struct

class Client:
    """Class for tracking, finding, adding, and removing clients"""
    clients = {}
    def addClient(skt):
        Client.clients[skt] = skt.fileno()              # Add file descriptor to dictionary for tracking connections
        print('DEBUG: Added Client: ', Client.clients[skt])
    def removeClient(skt):
        print('DEBUG: Removing Client: ', Client.clients[skt])
        Client.clients.pop(skt)
        print('DEBUG: Connected Clients:', Client.clients)
    def getClients():                   # Pull list of all connected clients
        return Client.clients
    def getClient(skt):                 # Pull information on specified client
        return Client.clients[skt]

class Message:
    msgType = int(1)
    
    def sendMessage(skt, sender, receiver, message):
        messagePacked = 0
        return lurkSend(skt, messagePacked)

class ChangeRoom:
    """Server should not send CHANGEROOM messages"""
    msgType = int(2)

class Fight:
    """Server should not send FIGHT messages, but it can initiate fights at any time!"""
    msgType = int(3)

class PVPFight:
    """Server should not send PVPFIGHT messages"""
    msgType = int(4)

class Loot:
    """Server should not send LOOT messages"""
    msgType = int(5)

class Start:
    """Server should not send START messages"""
    msgType = int(6)

class Error:
    msgType = int(7)
    
    errorCodes = {
        0: 'ERROR: This message type is not yet supported!',
        1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
        2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
        3: 'ERROR: Bad Monster. Attempt to loot a nonexistent or not present monster.',
        4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
        5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
        6: 'ERROR: No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.',
        7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
        8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.'
        }
    
    def sendError(skt, code):
        errCode = int(code)
        errMsgLen = len(Error.errorCodes[code])
        errMsg = Error.errorCodes[code].encode('utf-8')
        errorPacked = struct.pack('<2BH%ds' %errMsgLen, Error.msgType, errCode, errMsgLen, errMsg)
        print('DEBUG: Sending ERROR message!')
        return lurkSend(skt, errorPacked)

class Accept:
    msgType = int(8)
    
    def sendAccept(skt, message):
        action = int(message)
        acceptPacked = struct.pack('<2B', Accept.msgType, action)
        print('DEBUG: Sending ACCEPT message!')
        return lurkSend(skt, acceptPacked)
    
class Room:
    msgType = int(9)

    rooms = {
        0: ('Pine Forest', 'Located deep in the forbidden mountain range, there is surprisingly little to see here beyond towering spruce trees and small game.'),
        1: ('Dark Grove', 'A hallway leading away from the starting room.'),
        2: ('Hidden Valley', 'Seems to be remnants of a ranch here...')
    }

    def sendRoom(skt, roomNum):
        roomNum = int(roomNum)
        roomName = Room.rooms[roomNum][0]
        roomDes = Room.rooms[roomNum][1]
        roomDesLen = len(roomDes)
        roomPacked = struct.pack('<BH32sH%ds' %roomDesLen, Room.msgType, roomNum, bytes(roomName, 'utf-8'), roomDesLen, bytes(roomDes, 'utf-8'))
        print('DEBUG: Sending ROOM message!')
        return lurkSend(skt, roomPacked)

class Character:
    msgType = int(10)
    
    characters = {}
    
    def getRoom(name):
        """Function for getting current room of provided character name"""
        if name not in Character.characters:
            print('ERROR: getRoom() cannot find character in dictionary of character!')
            return False
        character = Character.characters.get(name)
        print('DEBUG: getRoom() found {} in dictionary!'.format(name))
        room = character[7]
        print('DEBUG: getRoom() returning room number {}'.format(room))
        return room
    
    def sendCharacter(skt, name):
        """Function for sending corrected CHARACTER message back to socket from dictionary"""
        #if name not in Character.characters:
            #print('ERROR: sendCharacter() cannot find character in dictionary of character!')
            #return False
        flags = Character.characters[name][0]
        attack = Character.characters[name][1]
        defense = Character.characters[name][2]
        regen = Character.characters[name][3]
        health = Character.characters[name][4]
        gold = Character.characters[name][5]
        roomNum = Character.characters[name][6]
        charDesLen = Character.characters[name][7]
        charDes = Character.characters[name][8]
        characterPacked = struct.pack('<B32sB7H%ds' %charDesLen, Character.msgType, bytes(name, 'utf-8'), flags, attack, defense, regen, health, gold, roomNum, charDesLen, bytes(charDes, 'utf-8'))
        print('DEBUG: Sending CHARACTER message!')
        return lurkSend(skt, characterPacked)

class Game:
    msgType = int(11)
    initPoints = int(100)
    statLimit = int(65535)
    gameDes = bytes(str("""Can you conquer the beast?
                        
 (                    (                                   
 )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
 /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                       |___/              
"""), 'utf-8')
    gameDesLen = int(len(gameDes))
    
    def sendGame(skt):
        gamePacked = struct.pack('<B3H%ds' %Game.gameDesLen, Game.msgType, Game.initPoints, Game.statLimit, Game.gameDesLen, Game.gameDes)
        print('DEBUG: Sending GAME message!')
        return lurkSend(skt, gamePacked)

class Leave:
    """Server should not send LEAVE messages"""
    msgType = int(12)

class Connection:
    msgType = int(13)
    
    connections = {
        Room.rooms[0]: (Room.rooms[1], Room.rooms[2]),
        Room.rooms[1]: (Room.rooms[2]),
        Room.rooms[2]: (Room.rooms[1])
    }
    
    def getConnections(roomNum):
        """Function that returns connections for provided room number"""
        if roomNum not in Connection.connections:
            print('ERROR: getConnections() cannot find requested room {}'.format(roomNum))
            return False
        print('DEBUG: getConnections() found connections for room {}'.format(roomNum))
        return Connection.connections.get(roomNum)
    
    def sendConnection(skt, roomNum):
        if (roomNum in Connection.connections):
            #for (roomNum in Connection.connections[])
            connectionPacked = struct.pack('<BH32sH%ds' %Room.rooms[roomNum][1], Connection.msgType, Room.rooms[roomNum], Room.rooms[roomNum][0], len(Room.rooms[roomNum][1]), Room.rooms[roomNum][1])
            print('DEBUG: Sending CONNECTION message!')
            return lurkSend(skt, connectionPacked)

class Version:
    msgType = int(14)
    major = int(2)
    minor = int(3)
    extSize = int(0)
    
    def sendVersion(skt):
        versionPacked = struct.pack('<3BH', Version.msgType, Version.major, Version.minor, Version.extSize)
        print('DEBUG: Sending VERSION message!')
        return lurkSend(skt, versionPacked)

# Function to takes action based on incoming message from client
def lurkServ(skt, message):
    if (message[0] == MESSAGE):
        print('DEBUG: Server handling MESSAGE message!')
        pass
    elif (message[0] == CHANGEROOM):
        print('DEBUG: Server handling CHANGEROOM message!')
        pass
    elif (message[0] == FIGHT):
        print('DEBUG: Server handling FIGHT message!')
        pass
    elif (message[0] == PVPFIGHT):
        print('DEBUG: Server handling PVPFIGHT message!')
        pass
    elif (message[0] == LOOT):
        print('DEBUG: Server handling LOOT message!')
        pass
    elif (message[0] == START):
        print('DEBUG: Server handling START message!')
        pass
    elif (message[0] == ERROR):
        print('DEBUG: Server handling ERROR message!')
        pass
    elif (message[0] == ACCEPT):
        print('DEBUG: Server handling ACCEPT message!')
        pass
    elif (message[0] == ROOM):
        print('DEBUG: Server handling ROOM message!')
        pass
    elif (message[0] == CHARACTER):
        print('DEBUG: Server handling CHARACTER message!')
        msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes = message
        name = name.decode('utf-8')
        # If received character is new to the server
        if (name not in Character.characters):
            print('DEBUG: Character not found in database, adding!')
            character = Character.characters.update({name: [flags, attack, defense, regen, 100, 0, 0, charDesLen, charDes]})   # Health = 100, Gold = 0, Room = 0
            print('DEBUG: Dictionary of characters:', Character.characters)
            # If stats and CHARACTER message is valid, send ACCEPT
            if (attack + defense + regen <= Game.initPoints):
                print('DEBUG: Stats valid, sending ACCEPT!')
                accept = Accept.sendAccept(skt, 10)
                room = Room.sendRoom(skt, 0)
                character = Character.sendCharacter(skt, name)
            else:
                print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                error = Error.sendError(skt, 4)
        else:
            print('DEBUG: Character found in database!')
            if (attack + defense + regen <= Game.initPoints):
                print('DEBUG: Detected valid stats, sending ACCEPT!')
                Character.getRoom(name)
                accept = Accept.sendAccept(skt, 10)
                room = Room.sendRoom(skt, 0)
            else:
                print('DEBUG: Detected invalid stats, sending ERROR type 4!')
                error = Error.sendError(skt, 4)
    elif (message[0] == GAME):
        print('DEBUG: Server handling GAME message!')
        pass
    elif (message[0] == LEAVE):
        print('DEBUG: Server handling LEAVE message!')
        pass
    elif (message[0] == CONNECTION):
        print('DEBUG: Server handling CONNECTION message!')
        pass
    elif (message[0] == VERSION):
        print('DEBUG: Server handling VERSION message!')
        pass
    else:
        print('DEBUG: Invalid message type passed to lurkServ()')
        pass
    