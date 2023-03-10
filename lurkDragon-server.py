"""Logan's LURK Server
"""
#!/usr/bin/env python3

import socket
import sys
import threading

from colorama import Fore

import lurk

MAJOR = int(2)
MINOR = int(3)
EXT_SIZE = int(0)

INIT_POINTS = int(100)
STAT_LIMIT = int(65535)
GAME_DESCRIPTION = str(r"""Can you conquer the beasts?
    (                    (                                   
    )\ )               ) )\ )                                
(()/(   (   (    ( /((()/(   (       )  (  (              
    /(_)) ))\  )(   )\())/(_))  )(   ( /(  )\))(  (    (     
(_))  /((_)(()\ ((_)\(_))_  (()\  )(_))((_))\  )\   )\ )  
| |  (_))(  ((_)| |(_)|   \  ((_)((_)_  (()(_)((_) _(_/(  
| |__| || || '_|| / / | |) || '_|/ _` |/ _` |/ _ \| ' \)) 
|____|\_,_||_|  |_\_\ |___/ |_|  \__,_|\__, |\___/|_||_|  
                                        |___/              
""")
GAME_DESCRIPTION_LEN = int(len(GAME_DESCRIPTION))

names = {}
def add_name(skt, name):
    names.update({name: skt})
def del_name(name):
    return names.pop(name)
sockets = {}
def add_socket(skt, name):
    sockets.update({skt: name})
def del_socket(skt):
    return sockets.pop(skt)

# Dictionary (Key: Value)
# Key: Name
# Value (list): [flags, attack, defense, regen, health, gold, currentRoomNum, charDesLen, charDes]
characters = {'Blue Bunny': [lurk.ALIVE | lurk.MONSTER, 2, 2, 2, 100, 5, 3, 47,
                             'Dark gray bunny with a red collar, is it a pet?'],
              'Undead Farmer': [lurk.ALIVE | lurk.MONSTER, 10, 5, 5, 100, 100, 27, 13,
                                'Pesticide-ridden rotting guy.'],
              'Barnyard Bucko': [lurk.ALIVE | lurk.MONSTER, 30, 35, 5, 100, 100, 30, 43,
                                 'Some weird guy you should probably destroy.'],
              'Lurk Dragon': [lurk.ALIVE | lurk.MONSTER, 70, 20, 10, 100, 100, 25, 35,
                              'A terrifying beast, worthy to slay!'],
              'Sentient Sandstorm': [lurk.ALIVE | lurk.MONSTER, 20, 20, 20, 100, 100, 11, 49,
                                     'A cloud of dust and sand trying to suffocate you.'],
              'Giant Sandworm': [lurk.ALIVE | lurk.MONSTER, 50, 25, 20, 100, 100, 35, 49,
                                     'A foul worm full of teeth with a ravenous hunger.'],
              'Mudcrabs': [lurk.ALIVE | lurk.MONSTER, 10, 15, 10, 100, 100, 5, 49,
                                     'Giant crabs with claws that could lop off an arm.'],
              'Megalodon': [lurk.ALIVE | lurk.MONSTER, 50, 50, 20, 100, 100, 12, 28,
                                     'This is one massive shark...'],
              'Rabid Wolf': [lurk.ALIVE | lurk.MONSTER, 15, 15, 20, 100, 100, 2, 46,
                                     'A gray wolf frothing at the mouth, poor thing!'],
              'Rattlesnake': [lurk.ALIVE | lurk.MONSTER, 10, 2, 5, 100, 100, 4, 40,
                                     'A relatively large and loud rattlesnake.']}
def add_character(character):
    name, flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des = character
    characters.update({name: [flags, attack, defense, regen, health, gold, room_num, char_des_len, char_des]})
def get_character(name):
    """Returns tuple of information of character with name.

    Args:
        name (string): Name of character

    Returns:
        _type_: _description_
    """
    name = name.replace('\x00', '')
    if name not in characters.keys():
        print(Fore.RED+f'ERROR: get_character: Cannot find {name} in {characters.keys()}!')
        return None
    character = (name, characters[name][0], characters[name][1], characters[name][2], characters[name][3], characters[name][4], characters[name][5], characters[name][6], characters[name][7], characters[name][8])
    return character
def send_characters(room_num):
    """Function for sending all characters to to all connected clients located in provided room number.

    Args:
        room_num (int): Room number.
    """
    for socket, name in sockets.items():
        player = get_character(name)
        player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
        if player_room != room_num:
            continue
        for name, stats in characters.items():
            if stats[6] != room_num:
                continue
            lurk.write(socket, (lurk.CHARACTER, name, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8]))
def update_characters(target_name, old_room_num):
    """Used to update all connected clients in old_room_num that name moved to a new room"""
    for key, value in sockets.items():
        player = get_character(value)
        player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
        if player_room != old_room_num:
            continue
        target = get_character(target_name)
        target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des = target
        lurk.write(key, (lurk.CHARACTER, target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des))
errors = {
    0: 'ERROR: This message type is not supported!',
    1: 'ERROR: Bad Room! Attempt to change to an inappropriate room.',
    2: 'ERROR: Player Exists. Attempt to create a player that already exists.',
    3: 'ERROR: Bad Monster. Cannot loot a nonexistent, not present, or a living monster.',
    4: 'ERROR: Stat error. Caused by setting inappropriate player stats. Try again!',
    5: 'ERROR: Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.',
    6: 'ERROR: No target. Attempt to loot nonexistent players, fight players in different rooms, message someone offline, etc.',
    7: 'ERROR: No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)',
    8: 'ERROR: No player vs. player combat on the server. Servers do not have to support player-vs-player combat.',
    9: 'ERROR: Monster. Cannot create or reprise a monster character.'
    }
rooms = {
    100: ('Narrator Room', 'Just a room with no connections where the narrator lives.'),
    0: ('Backrooms', 'You should not be here!'),
    1: ('Village of Valhalla', 'Home of the mighty hunters, this is the only place to find respite for miles.'),
    2: ('Great Aster Meadow', 'Green rolling hills full of wildflowers and small game for as far as the eye can see.'),
    3: ('Ashen Taiga', 'A dark and expansive spruce forest, with a slow climb to higher altitudes in the east.'),
    4: ('Rainless Fells', 'Endless miles of sun-soaked rock and sand under an endless blue sky, this massive tract of land is hostile to all known life.'),
    5: ('Sunset Coast', 'Where the setting sun meets the rolling sea, stretching for untold distances to the north and south.'),
    6: ('Hidden Groves', 'A lively grove of oak trees and song birds, tucked away in a shallow valley.'),
    7: ('Abandoned Swamps', 'Murky swamps that remained unexplored, for whatever reason.'),
    8: ('Bloodsoaked Gorge', 'A dangerous beast must live here, considering the gore and remains strewn about.'),
    9: ('Snowy Mountains', 'The Ashen Taiga gives way to rougher terrain, elevation, and rapidly thinning trees.'),
    10: ('Scorched Frontier', 'TBW'),
    11: ('Arid Badlands', 'TBW'),
    12: ('Open Sea', 'TBW'),
    13: ('Rugged Coastline', 'TBW'),
    14: ('Forgotten Bog', 'TBW'),
    15: ('Misty Temple', 'TPW'),
    16: ('Sulphur Pools', 'TBW'),
    17: ('Golden Marshes', 'TBW'),
    18: ('Sheltered Crevices', 'TBW'),
    19: ('Dark Cavern', 'TBW'),
    20: ('Deep Abyss', 'TBW'),
    21: ('Submerged Cave', 'TBW'),
    22: ('Raging River', 'TBW'),
    23: ('Frozen Lake', 'TBW'),
    24: ('Jagged Peaks', 'TBW'),
    25: ('Peaceful Promontory', 'TBW'),
    26: ('Hidden Valley', 'Seems to be remnants of a ranch here...'),
    27: ('Crop Fields', 'TBW'),
    28: ('Cliffside Roost', 'TBW'),
    29: ('Glacial Highlands', 'TBW'),
    30: ('Red Barn', 'TBW'),
    31: ('Loft', 'TBW'),
    32: ('Roof', 'TBW'),
    33: ('Wintery Thicket', 'TBW'),
    34: ('Dusty Ruins', 'TBW'),
    35: ('Smoldering Sands', 'TBW'),
    36: ('Dire Pits', 'TBW'),
    37: ('Rayless Depths', 'TBW'),
    38: ('Korpijnen Shores', 'TBW'),
    39: ('Hiemal Inlet', 'TBW'),
    40: ('Remote Estuary', 'TBW'),
}
connections = {
    0: (1,),
    1: (2, 3, 4, 5),
    2: (1, 6, 7),
    3: (1, 8, 9),
    4: (1, 10, 11),
    5: (1, 12, 13),
    6: (2,),
    7: (2, 14, 16),
    8: (3, 18, 22),
    9: (3, 23, 26, 29),
    10: (4, 34),
    11: (4, 35),
    12: (5, 37),
    13: (5, 38, 40),
    14: (7, 15, 16),
    15: (14,),
    16: (7, 14, 17),
    17: (16,),
    18: (8, 19),
    19: (18, 20, 21),
    20: (19,),
    21: (19, 22, 23),
    22: (8,),
    23: (9, 24),
    24: (23, 25, 28),
    25: (24,),
    26: (9, 27, 30),
    27: (26, 30),
    28: (24,),
    29: (9, 33),
    30: (26, 27, 31),
    31: (30, 32),
    32: (31,),
    33: (29,),
    34: (10,),
    35: (11, 36),
    36: (35,),
    37: (12,),
    38: (13, 39),
    39: (38,),
    40: (13,)
}
def cleanup_client(skt):
    """Function for cleaning up a disconnected client.

    Args:
        skt (socket): Client socket.
    """
    try:
        del_name(sockets[skt])
        del_socket(skt)
    except KeyError as exc:
        print(Fore.YELLOW+'WARN: cleanup_client: Nothing to clean!')
    skt.shutdown(2)
    skt.close()
    print(Fore.WHITE+'INFO: cleanup_client: Finished!')
def handle_client(skt):
    """Function for communicating with individual clients.

    Args:
        skt (socket): Client socket.
    """
    while True:
        message = lurk.read(skt)
        if not message:
            print(Fore.RED+'ERROR: handle_client: read returned None, breaking while loop!')
            cleanup_client(skt)
            break
        if message[0] == lurk.MESSAGE:
            lurk_type, msg_len, recipient_name, sender_name, message = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: Message Length:', msg_len)
            print('DEBUG: Recipient Name:', recipient_name)
            print('DEBUG: Sender Name:', sender_name)
            #print('DEBUG: Message:', message)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Player not ready, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if recipient_name not in names:
                print(Fore.YELLOW+f'WARN: Recipient {recipient_name} not online, sending ERROR code 6!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            lurk.write(skt, (lurk.ACCEPT, lurk.MESSAGE))
            lurk.write(names[recipient_name], (lurk.MESSAGE, msg_len, recipient_name, sender_name, message))
            continue
        elif message[0] == lurk.CHANGEROOM:
            lurk_type, new_room_num = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: desiredRoom:', new_room_num)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Player not ready, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            character = get_character(sockets[skt])
            name, flags, attack, defense, regen, health, gold, old_room_num, char_des_len, char_des = character
            if new_room_num not in connections[old_room_num]:
                print(Fore.YELLOW+f'WARN: {name} attempted bad move, sending ERROR code 1!')
                lurk.write(skt, (lurk.ERROR, 1, len(errors[1]), errors[1]))
                continue
            characters.update({name: [flags, attack, defense, regen, health, gold, new_room_num, char_des_len, char_des]})
            #lurk.write(skt, (lurk.ACCEPT, lurk.CHANGEROOM))
            lurk.write(skt, (lurk.ROOM, new_room_num, rooms[new_room_num][0], len(rooms[new_room_num][1]), rooms[new_room_num][1]))
            update_characters(name, old_room_num)   # Send CHARACTER message to all players in old room
            send_characters(new_room_num)           # Send CHARACTER messages for all characters in new room
            for room_num, connection in connections.items():
                if room_num != new_room_num:
                    continue
                for connection in connections[room_num]:
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))   # Send CONNECTION messages for new room
            continue
        elif message[0] == lurk.FIGHT:
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = get_character(sockets[skt])
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            count = 0
            for name, stats in characters.items():
                if stats[6] != player_room or stats[0] != lurk.MONSTER | lurk.ALIVE or name == player_name:
                    continue
                print(Fore.WHITE+f'DEBUG: {name} has monster flag set, flag: {stats[0]}')
                count+=1
                monster = get_character(name)
                monster_name, monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des = monster
                monster_damage = monster_attack * monster_attack / (monster_attack + monster_defense)
                player_health -= monster_damage
                player_health = round(player_health)
                print(f'DEBUG: player_health after fight: {player_health}')
                if player_health <= 0:
                    player_flags ^= lurk.ALIVE
                    player_health = 0
                characters.update({player_name: [player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des]})
                player_damage = player_attack * player_attack / (player_attack + player_defense)
                monster_health -= player_damage
                monster_health = round(monster_health)
                print(f'DEBUG: monster_health after fight: {monster_health}')
                if monster_health <= 0:
                    monster_flags ^= lurk.ALIVE
                    monster_health = 0
                characters.update({monster_name: [monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des]})
                lurk.write(skt, (lurk.CHARACTER, player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des))
                lurk.write(skt, (lurk.CHARACTER, monster_name, monster_flags, monster_attack, monster_defense, monster_regen, monster_health, monster_gold, monster_room, monster_char_des_len, monster_char_des))
            if count == 0:
                print(Fore.YELLOW+f"WARN: No monsters in {player_name}'s room, sending ERROR code 7!")
                lurk.write(skt, (lurk.ERROR, 7, len(errors[7]), errors[7]))
            continue
        elif message[0] == lurk.PVPFIGHT:
            lurk_type, character_name = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: targetName:', character_name)
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = get_character(sockets[skt])
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            print('ERROR: Server does not currently support PVPFIGHT, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 8, len(errors[8]), errors[8]))
            continue
        elif message[0] == lurk.LOOT:
            lurk_type, character_name = message
            print(Fore.WHITE+f'DEBUG: handle_client: Type: {lurk_type}')
            print(Fore.WHITE+f'DEBUG: targetName: {character_name}')
            if skt not in sockets:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            player = get_character(sockets[skt])
            player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des = player
            if player_flags != player_flags | lurk.STARTED:
                print(Fore.YELLOW+'WARN: Player flag STARTED not set, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            target = get_character(character_name)
            if target == None or target[7] != player_room:
                print(Fore.YELLOW+'WARN: Cannot loot nonexistent target, sending ERROR code 6!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des = target
            if target_flags == target_flags | lurk.ALIVE:
                print(Fore.YELLOW+'WARN: Cannot loot a living target, sending ERROR code 3!')
                lurk.write(skt, (lurk.ERROR, 6, len(errors[6]), errors[6]))
                continue
            player_gold += target_gold
            target_gold = 0
            characters.update({player_name: [player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des]})
            characters.update({target_name: [target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des]})
            lurk.write(skt, (lurk.CHARACTER, player_name, player_flags, player_attack, player_defense, player_regen, player_health, player_gold, player_room, player_char_des_len, player_char_des))
            lurk.write(skt, (lurk.CHARACTER, target_name, target_flags, target_attack, target_defense, target_regen, target_health, target_gold, target_room, target_char_des_len, target_char_des))
            continue
        elif message[0] == lurk.START:
            print('DEBUG: Handling START!')
            try:
                character = get_character(sockets[skt])
                name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
            except:
                print(Fore.YELLOW+'WARN: Character not yet created, sending ERROR code 5!')
                lurk.write(skt, (lurk.ERROR, 5, len(errors[5]), errors[5]))
                continue
            if room == 0:
                room = 1
            
            characters.update({name:[flags | lurk.STARTED, attack, defense, regen, health, gold, room, char_des_len, char_des]})
            # Send ACCEPT message
            lurk.write(skt, (lurk.ACCEPT, lurk.START))
            # Send CHARACTER messages for all characters with same room number
            send_characters(room)
            # Send ROOM message
            lurk.write(skt, (lurk.ROOM, room, rooms[room][0], len(rooms[room][1]), rooms[room][1]))
            # Send CONNECTION messages for all connections with current room
            for room_num, connection in connections.items():
                if room_num != room:
                    continue
                for connection in connections[room_num]:
                    lurk.write(skt, (lurk.CONNECTION, connection, rooms[connection][0], len(rooms[connection][1]), rooms[connection][1]))
            continue
        elif message[0] == lurk.ERROR:
            lurk_type, error_code, error_msg_len, error_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: errCode:', error_code)
            print('DEBUG: errMsgLen:', error_msg_len)
            print('DEBUG: errMsg:', error_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.ACCEPT:
            lurk_type, accepted_msg = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: acceptedMsg:', accepted_msg)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.ROOM:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.CHARACTER:
            lurk_type, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = message
            print(Fore.WHITE+f'DEBUG: handle_client: Type: {lurk_type}')
            print('DEBUG: Name:', name)
            print('DEBUG: Flags:', flags)
            print('DEBUG: Attack:', attack)
            print('DEBUG: Defense:', defense)
            print('DEBUG: Regen:', regen)
            print('DEBUG: Health:', health)
            print('DEBUG: Gold:', gold)
            print('DEBUG: Room:', room)
            print('DEBUG: charDesLen:', char_des_len)
            print('DEBUG: charDes:', char_des)
            if name in names:
                print(Fore.YELLOW+'WARN: Attempting to create character already tied to a socket, sending ERROR code 2!')
                lurk.write(skt, (lurk.ERROR, 2, len(errors[2]), errors[2]))
                continue
            if flags == flags | lurk.JOIN_BATTLE:
                flags = lurk.ALIVE | lurk.JOIN_BATTLE | lurk.READY
            else:
                flags = lurk.ALIVE | lurk.READY
            if name not in characters:
                if attack + defense + regen > INIT_POINTS:
                    print(Fore.YELLOW+'WARN: Character stats invalid, sending ERROR code 4!')
                    lurk.write(skt, (lurk.ERROR, 4, len(errors[4]), errors[4]))
                    continue
                new_character = name, flags, attack, defense, regen, 100, 0, 0, char_des_len, char_des
                add_character(new_character)
                print(Fore.YELLOW+f'WARN: Added new character {name}')
            character = get_character(name)
            name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des = character
            print(Fore.YELLOW+f'WARN: Accessing character {name}')
            add_name(skt, name)
            add_socket(skt, name)
            lurk.write(skt, (lurk.ACCEPT, lurk.CHARACTER))
            lurk.write(skt, (lurk.CHARACTER, name, flags, attack, defense, regen, health, gold, room, char_des_len, char_des))
            # Send MESSAGE to client from narrator here, stating welcome back!
            continue
        elif message[0] == lurk.GAME:
            lurk_type, init_points, stat_limit, game_des_len, game_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: initPoints:', init_points)
            print('DEBUG: statLimit:', stat_limit)
            print('DEBUG: gameDesLen:', game_des_len)
            print('DEBUG: gameDes:', game_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.LEAVE:
            print(Fore.GREEN+'INFO: handle_client: Received LEAVE!')
            cleanup_client(skt)
            break
        elif message[0] == lurk.CONNECTION:
            lurk_type, room_num, room_name, room_des_len, room_des = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: roomNum:', room_num)
            print('DEBUG: roomName:', room_name)
            print('DEBUG: roomDesLen:', room_des_len)
            print('DEBUG: roomDes:', room_des)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        elif message[0] == lurk.VERSION:
            lurk_type, major, minor, extension_len = message
            print(Fore.WHITE+'DEBUG: handle_client: Type:', lurk_type)
            print('DEBUG: major:', major)
            print('DEBUG: minor:', minor)
            print('DEBUG: extSize:', extension_len)
            print('ERROR: Server does not support receiving this message, sending ERROR code 0!')
            lurk.write(skt, (lurk.ERROR, 0, len(errors[0]), errors[0]))
            continue
        else:
            print('DEBUG: message[0] not a valid LURK type?')
            continue
# Establish IPv4 TCP socket
server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if server_skt == -1:
    print(Fore.RED+'ERROR: Server socket creation error, stopping!')
    sys.exit(0)
# Assigned range: 5010 - 5014
ADDRESS = '0.0.0.0'
PORTS = [5010, 5011, 5012, 5013, 5014]
for port in PORTS:
    try:
        server_skt.bind((ADDRESS, port))
        break
    except OSError:
        print(Fore.CYAN+f'WARN: Port {port} unavailable!')
        continue
server_skt.listen()
print(Fore.WHITE+f'INFO: Listening on address: {ADDRESS}, {port}')
while True:
    client_skt, client_addr = server_skt.accept()
    version = (lurk.VERSION, MAJOR, MINOR, EXT_SIZE)
    lurk.write(client_skt, version)
    game = (lurk.GAME, INIT_POINTS, STAT_LIMIT, GAME_DESCRIPTION_LEN, GAME_DESCRIPTION)
    lurk.write(client_skt, game)
    threading.Thread(target=handle_client, args=(client_skt,), daemon=True).start()
