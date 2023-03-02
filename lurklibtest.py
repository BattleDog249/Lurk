# Potential Bug: Check on unpack descriptions, des, = vs des =
# In messages 1 byte big, like START, may have to use startData = bytes(data[0:1]) vs. startData = data[0:1]
    # May not need to unpack because its only 1 integer?

#!/usr/bin/env python3

import socket
import struct

MESSAGE = int(1)
CHANGEROOM = int(2)
FIGHT = int(3)
PVPFIGHT = int(4)
LOOT = int(5)
START = int(6)
ERROR = int(7)
ACCEPT = int(8)
ROOM = int(9)
CHARACTER = int(10)
GAME = int(11)
LEAVE = int(12)
CONNECTION = int(13)
VERSION = int(14)

class LurkException(Exception):
    pass
class Lurk:
    def lurkSend(skt, messages):
        if type(messages) == list:
            for message in messages:
                msgType = message[0]
                try:
                    skt.sendall(message)
                    print('DEBUG: lurkSend() sent a message!')
                    continue
                except ConnectionError:
                    print('WARN: ConnectionError, raising LurkException!')
                    raise LurkException
            return 0
        try:
            skt.sendall(messages)
            print('DEBUG: lurkSend() sent 1 message!')
            return 0
        except ConnectionError:
            print('WARN: ConnectionError, raising LurkException!')
            raise LurkException
    
    def lurkRecv(skt):
        messages = []
        data = bytearray(b'')
        try:
            data = skt.recv(1024)
            if data == b'':     # If recv returns null, client disconnected. This fixes LurkScan!
                return None
        except socket.error or ConnectionError or OSError:
            return None
        
        print('DEBUG: Received binary data:', data)
        i = 0
        while i <= len(data):
            print('DEBUG: i:', i)
            lurkMsgType = data[i]
            print('DEBUG: lurkMsgType:', lurkMsgType)
            
            if (lurkMsgType < 1 or lurkMsgType > 14):
                    print('ERROR: Message not a valid lurk type')
                    i += 1
                    continue
            
            if (lurkMsgType == MESSAGE):
                print('DEBUG: Is it a MESSAGE message?')
                messageHeaderLen = i + 67
                messageHeader = data[i:messageHeaderLen]
                try:
                    msgType, msgLen, recvName, sendName, narration = struct.unpack('<BH32s30sH', messageHeader)
                except struct.error:
                    # If lurkMsgType is a valid int, but not a valid lurk message in its entirety, continue looking for next lurk msg type
                    print('ERROR: Failed to unpack constant MESSAGE data!')
                    continue
                messageData = data[messageHeaderLen:messageHeaderLen+msgLen]
                try:
                    message = struct.unpack('<%ds' %msgLen, messageData)
                except struct.error:
                    print('ERROR: Failed to unpack variable MESSAGE data!')
                    continue
                print('DEBUG: Message:', message)
                # Pack values into a tuple, and append to the list of messages to send to interpreter
                messages.append((msgType, msgLen, recvName, sendName, narration, message))
                i += messageHeaderLen + msgLen
                continue
            
            elif (lurkMsgType == CHANGEROOM):
                print('DEBUG: Is it a CHANGEROOM message?')
                changeroomHeaderLen = i + 3
                changeroomHeader = data[i:changeroomHeaderLen]
                try:
                    msgType, desiredRoomNum = struct.unpack('<BH', changeroomHeader)
                except struct.error:
                    print('ERROR: Failed to unpack CHANGEROOM data!')
                    continue
                messages.append((msgType, desiredRoomNum))
                i += changeroomHeaderLen
                continue
            
            elif (lurkMsgType == FIGHT):
                print('DEBUG: Is it a FIGHT message?')
                fightHeaderLen = i + 1
                fightHeader = data[i:fightHeaderLen]
                try:
                    msgType = struct.unpack('<B', fightHeader)
                except struct.error:
                    print('ERROR: Failed to unpack FIGHT data!')
                    continue
                messages.append((msgType,))
                i += fightHeaderLen
                continue
            
            elif (lurkMsgType == PVPFIGHT):
                print('DEBUG: Is it a PVPFIGHT message?')
                pvpfightHeaderLen = i + 33
                pvpfightHeader = data[i:pvpfightHeaderLen]
                try:
                    msgType, targetName = struct.unpack('<B32s', pvpfightHeader)
                except struct.error:
                    print('ERROR: Failed to unpack PVPFIGHT data!')
                    continue
                messages.append((msgType, targetName))
                i += pvpfightHeaderLen
                continue
            
            elif (lurkMsgType == LOOT):
                print('DEBUG: Is it a LOOT message?')
                lootHeaderLen = i + 33
                lootHeader = data[i:lootHeaderLen]
                try:
                    msgType, targetName = struct.unpack('<B32s', lootHeader)
                except struct.error:
                    print('ERROR: Failed to unpack LOOT data!')
                    continue
                messages.append((msgType, targetName))
                i += lootHeaderLen
                continue
            
            elif (lurkMsgType == START):
                print('DEBUG: Is it a START message?')
                startHeaderLen = i + 1
                startHeader = data[i:startHeaderLen]
                try:
                    msgType = struct.unpack('<B', startHeader)
                except struct.error:
                    print('ERROR: Failed to unpack START data!')
                    continue
                messages.append((msgType,))
                i += startHeaderLen
                continue
            
            elif (lurkMsgType == ERROR):
                print('DEBUG: Is it an ERROR message?')
                errorHeaderLen = i + 4
                errorHeader = data[i:errorHeaderLen]
                try:
                    msgType, errCode, errMsgLen = struct.unpack('<2BH', errorHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack constant ERROR data!')
                    continue
                errorData = data[errorHeaderLen:errorHeaderLen+errMsgLen]
                try:
                    errMsg = struct.unpack('<%ds' %errMsgLen, errorData)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack variable ERROR data!')
                    continue
                messages.append((msgType, errCode, errMsgLen))
                i += errorHeaderLen + errMsgLen
                continue
            
            elif (lurkMsgType == ACCEPT):
                print('DEBUG: Is it an ACCEPT message?')
                acceptHeaderLen = i + 2
                acceptHeader = data[i:acceptHeaderLen]
                try:
                    msgType, acceptedMsg = struct.unpack('<2B', acceptHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack ACCEPT data!')
                    continue
                messages.append((msgType, acceptedMsg))
                i += acceptHeaderLen
                continue
            
            elif (lurkMsgType == ROOM):
                print('DEBUG: Is it a ROOM message?')
                roomHeaderLen = i + 37
                roomHeader = data[i:roomHeaderLen]
                try:
                    msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', roomHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack constant ROOM data!')
                    continue
                roomData = data[roomHeaderLen:roomHeaderLen+roomDesLen]
                try:
                    roomDes = struct.unpack('<%ds' %roomDesLen, roomData)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack variable ROOM data!')
                    continue
                messages.append((msgType, roomNum, roomName, roomDesLen, roomDes))
                i += roomHeaderLen + roomDesLen
                continue
            
            elif (lurkMsgType == CHARACTER):
                print('DEBUG: Is it a CHARACTER message?')
                characterHeaderLen = i + 48
                characterHeader = data[i:characterHeaderLen]
                try:
                    msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen = struct.unpack('<B32sB7H', characterHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack constant CHARACTER data!')
                    continue
                characterData = data[characterHeaderLen:characterHeaderLen+charDesLen]
                try:
                    charDes, = struct.unpack('<%ds' %charDesLen, characterData)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack variable CHARACTER data!')
                    continue
                name = name.decode('utf-8')
                charDes = charDes.decode('utf-8')
                messages.append((msgType, name, flags, attack, defense, regen, health, gold, room, charDesLen, charDes))
                i += characterHeaderLen + charDesLen
                continue
            
            elif (lurkMsgType == GAME):
                print('DEBUG: Is it a GAME message?')
                gameHeaderLen = i + 7
                gameHeader = data[i:gameHeaderLen]
                try:
                    msgType, initPoints, statLimit, gameDesLen = struct.unpack('<B3H', gameHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack constant GAME data!')
                    continue
                gameData = data[gameHeaderLen:gameHeaderLen+gameDesLen]
                try:
                    gameDes = struct.unpack('<%ds' %gameDesLen, gameData)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack variable GAME data!')
                    continue
                messages.append((msgType, initPoints, statLimit, gameDesLen, gameDes))
                i += gameHeaderLen + gameDesLen
                continue
            
            elif (lurkMsgType == LEAVE):
                print('DEBUG: Is it a LEAVE message?')
                leaveHeaderLen = i + 1
                leaveHeader = data[i:leaveHeaderLen]
                try:
                    msgType = struct.unpack('<B', leaveHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack LEAVE data!')
                    continue
                messages.append((msgType,))
                i += leaveHeaderLen
                continue
            
            elif (data[0] == CONNECTION):
                print('DEBUG: Is it a CONNECTION message?')
                connectionHeaderLen = i + 37
                connectionHeader = data[i:connectionHeaderLen]
                try:
                    msgType, roomNum, roomName, roomDesLen = struct.unpack('<BH32sH', connectionHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack constant CONNECTION data!')
                    continue
                connectionData = data[37:37+roomDesLen]
                try:
                    roomDes = struct.unpack('<%ds' %roomDesLen, connectionData)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack variable CONNECTION data!')
                    continue
                messages.append((msgType, roomNum, roomName, roomDesLen, roomDes))
                i += connectionHeaderLen +  roomDesLen
                continue
            
            elif (data[0] == VERSION):
                print('DEBUG: Is it a VERSION message?')
                versionHeaderLen = i + 5
                versionHeader = data[i:versionHeaderLen]
                try:
                    msgType, major, minor, extSize = struct.unpack('<3BH', versionHeader)
                except struct.error:
                    print('ERROR: lurkRead() failed to unpack VERSION data!')
                    continue
                messages.append((msgType, major, minor, extSize))
                i += versionHeaderLen
                continue
            
            else:
                print('ERROR: lurkRecv() was passed an invalid message type somehow, returning None!')
                return None
        return messages
    
    def sendMessage(skt, message):
        try:
            messagePacked = struct.pack('<BH32s30sH%ds' %message[1], message[0], message[1], message[2], message[3], message[4], message[5])
            print('DEBUG: Sending MESSAGE message!')
            Lurk.lurkSend(skt, messagePacked)
        except struct.error:
            print('ERROR: Failed to pack MESSAGE structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendChangeroom(skt, changeRoom):
        try:
            changeroomPacked = struct.pack('<BH', changeRoom[0], changeRoom[1])
            print('DEBUG: Sending CHANGEROOM message!')
            Lurk.lurkSend(skt, changeroomPacked)
        except struct.error:
            print('ERROR: Failed to pack CHANGEROOM structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendFight(skt):
        try:
            fightPacked = struct.pack('<B', FIGHT)
            print('DEBUG: Sending FIGHT message!')
            Lurk.lurkSend(skt, fightPacked)
        except struct.error:
            print('ERROR: Failed to pack FIGHT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendPvpfight(skt, pvpFight):
        try:
            pvpfightPacked = struct.pack('<B32s', pvpFight[0], pvpFight[1])
            print('DEBUG: Sending PVPFIGHT message!')
            Lurk.lurkSend(skt, pvpfightPacked)
        except struct.error:
            print('ERROR: Failed to pack PVPFIGHT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendLoot(skt, loot):
        try:
            lootPacked = struct.pack('<B32s', loot[0], loot[1])
            print('DEBUG: Sending LOOT message!')
            Lurk.lurkSend(skt, lootPacked)
        except struct.error:
            print('ERROR: Failed to pack LOOT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendStart(skt, start):
        try:
            startPacked = struct.pack('<B', START)
            print('DEBUG: Sending START message!')
            Lurk.lurkSend(skt, startPacked)
        except struct.error:
            print('ERROR: Failed to pack START structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendError(skt, error):
        try:
            errorPacked = struct.pack('<2BH%ds' %error[2], error[0], error[1], error[2], error[3])
            print('DEBUG: Sending ERROR message!')
            Lurk.lurkSend(skt, errorPacked)
        except struct.error:
            print('ERROR: Failed to pack ERROR structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendAccept(skt, accept):
        try:
            acceptPacked = struct.pack('<2B', ACCEPT, accept)
            print('DEBUG: Sending ACCEPT message!')
            Lurk.lurkSend(skt, acceptPacked)
        except struct.error:
            print('ERROR: Failed to pack ACCEPT structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendRoom(skt, room):
        try:
            roomPacked = struct.pack('<BH32sH%ds' %room[3], room[0], room[1], room[2], room[3], room[4])
            print('DEBUG: Sending ROOM message!')
            Lurk.lurkSend(skt, roomPacked)
        except struct.error:
            print('ERROR: Failed to pack ROOM structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendCharacter(skt, character):
        """_summary_

        Args:
            skt (_type_): _description_
            character (_type_): _description_

        Raises:
            struct.error: _description_
            Lurk.lurkSend.Error: _description_

        Returns:
            _type_: _description_
        """
        try:
            characterPacked = struct.pack('<B32sB7H%ds' %character[8], character[0], character[1], character[2], character[3], character[4], character[5], character[6], character[7], character[8], character[9])
            print('DEBUG: Sending CHARACTER message!')
            Lurk.lurkSend(skt, characterPacked)
        except struct.error:
            print('ERROR: Failed to pack CHARACTER structure!')
            raise struct.error
        except LurkException:
            print('ERROR: lurkSend() failed!')
            raise LurkException
        return 0
    def sendGame(skt, game):
        """_summary_

        Args:
            skt (_type_): _description_
            game (_type_): _description_

        Raises:
            struct.error: _description_
            Lurk.lurkSend.Error: _description_

        Returns:
            _type_: _description_
        """
        try:
            gamePacked = struct.pack('<B3H%ds' %game[3], game[0], game[1], game[2], game[3], game[4])
            print('DEBUG: Sending GAME message!')
            Lurk.lurkSend(skt, gamePacked)
        except struct.error:
            print('ERROR: Failed to pack GAME structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendLeave(skt):
        """Send a lurk LEAVE message to a socket.

        Args:
            skt (socket): Socket to send data to

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            leavePacked = struct.pack('<B', LEAVE)
            print('DEBUG: Sending LEAVE message!')
            Lurk.lurkSend(skt, leavePacked)
        except struct.error:
            print('ERROR: Failed to pack LEAVE structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendConnection(skt, connection):
        """Send a lurk CONNECTION message to a socket.

        Args:
            skt (socket): Socket to send data to
            connection (tuple): CONNECTION data

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            connectionPacked = struct.pack('<BH32sH%ds' %connection[3], connection[0], connection[1], connection[2], connection[3], connection[4])
            print('DEBUG: Sending CONNECTION message!')
            Lurk.lurkSend(skt, connectionPacked)
        except struct.error:
            print('ERROR: Failed to pack CONNECTION structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0
    def sendVersion(skt, version):
        """Send a lurk VERSION message to a socket.

        Args:
            skt (socket): Socket to send data to
            version (tuple): VERSION data

        Raises:
            struct.error: Failed to pack data into a structure
            Lurk.lurkSend.Error: Function lurkSend failed

        Returns:
            int: 0 if function finishes successfully
        """
        try:
            versionPacked = struct.pack('<3BH', version[0], version[1], version[2], version[3])
            print('DEBUG: Sending VERSION message!')
            Lurk.lurkSend(skt, versionPacked)
        except struct.error:
            print('ERROR: Failed to pack VERSION structure!')
            raise struct.error
        except Lurk.lurkSend.error:
            print('ERROR: lurkSend() failed!')
            raise Lurk.lurkSend.Error
        return 0