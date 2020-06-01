import curses 
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint 
from network import Network
import json
import time
import threading

height = 20
width = 60 
t = 0.3
clientnumber = 0
key = KEY_RIGHT
x = randint(1, 17)
y = randint(1, 50)
snake = [[x, y+3], [x,y+2], [x, y+1], [x, y]] #initial snake 
alive = True
what = False
lastmessage = {}


n = Network()
clientnumber = n.getid()
print(clientnumber)
snakearray = json.loads(n.send(json.dumps(snake)))
print(snakearray)

numofsnakes = len(snakearray)
keyarray = []
for i in snakearray:
    ID = i["id"]
    key = KEY_RIGHT
    item = {"id": ID, "key": key}
    keyarray.append(item)




#use global variables - three threads - keypressing, listening, update 

def recv_Serv(): #constantly recieving key presses from server 
    global key
    global alive
    global lastmessage
    global snakearray
    global keyarray
    global clientnumber
    keynum = 0
    
    while alive:
        recieved = n.simplercv() 

        if not recieved:
            break

        recieved = json.loads(recieved) #recieving keys of clients with their ids
        ID = int(recieved['id'])
        keynum = int(recieved['move']) #get key from other player
        
        if keynum == 5:
            for i in snakearray:
                snakeID = int(i["id"])
                if int(snakeID) == ID: 
                    blankbody = i["body"]
                    for x in blankbody:
                        win.addch(x[0], x[1], ' ')
                    snakearray.remove(i)
                    break
            for i in keyarray:
                keyID = int(i["id"])
                if keyID == ID: 
                    keyarray.remove(i)
                    break
            continue
        if keynum == 6:
            lastmessage = recieved
            alive = False
            break

        if keynum == 0:
            for i in snakearray:
                snakeID = int(i["id"])
                if int(snakeID) == ID: 
                    blankbody = i["body"]
                    for x in blankbody:
                        win.addch(x[0], x[1], ' ')
                    snakearray.remove(i)
                    break
            for i in keyarray:
                keyID = int(i["id"])
                if keyID == ID: 
                    keyarray.remove(i)
                    break
            

        for i in keyarray:
            keyID = i["id"]
            if int(keyID) == ID:
                if keynum == 1: i["key"] = KEY_UP
                elif keynum == 2: i["key"] = KEY_DOWN
                elif keynum == 3: i["key"] = KEY_RIGHT
                elif keynum == 4: i["key"] = KEY_LEFT

        if (ID == int(clientnumber)): 
            if keynum == 1: key = KEY_UP
            elif keynum == 2: key = KEY_DOWN
            elif keynum == 3: key = KEY_RIGHT
            elif keynum == 4: key = KEY_LEFT
            elif keynum == 5: break

    print('server ended')


def keythread():
    global key 
    global alive
    global what
    global keyarray
    global clientnumber

    keynum = 0

    while alive:
        while what:
            pass

        prevkey = key #assigns prevkey to current key pressed or remains at prevkey
        event = win.getch() #blocking 

        if event == -1:
            continue
        what = True


        if event == KEY_UP: keynum = 1
        elif event == KEY_DOWN: keynum = 2
        elif event == KEY_RIGHT: keynum = 3
        elif event == KEY_LEFT: keynum = 4

        keydict = {"id":clientnumber, "move":keynum}

        if alive:
            time.sleep(0.1)
            n.simplesend(json.dumps(keydict)) #sending player's move

    print('key ended')


def snakethread(win):
    global key
    global snake
    global alive
    global what
    global snakearray
    global keyarray
    global clientnumber
    global lastmessage

    keyplayer = 1
    snakearray2 = []

    while True:
        win.border(0)
        time.sleep(t)
        what = False

        if not alive:
            break

        for i in snakearray:
            if (int(i["id"]) == int(clientnumber)):
                i["body"].insert(0, [i["body"][0][0] + (key == KEY_DOWN and 1) + (key == KEY_UP and -1), i["body"][0][1] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1)])
                final = i["body"].pop()                                         
                win.addch(final[0], final[1], ' ')
                snake = i["body"]
            else:
                for j in keyarray:
                    if (i["id"] == j["id"]): 
                        keyplayer = j["key"]
                        break
                i["body"].insert(0, [i["body"][0][0] + (keyplayer == KEY_DOWN and 1) + (keyplayer == KEY_UP and -1), i["body"][0][1] + (keyplayer == KEY_LEFT and -1) + (keyplayer == KEY_RIGHT and 1)])
                final = i["body"].pop()                                         
                win.addch(final[0], final[1], ' ')

        if snake[0][0] == 0 or snake[0][0] == 19 or snake[0][1] == 0 or snake[0][1] == 59:
            curses.beep()
            alive = False 
            keydict = {"id":clientnumber, "move":0}
            lastmessage = keydict
            n.simplesend(json.dumps(keydict))
            break

        for i in snakearray:
            if int(i["id"] == int(clientnumber)):
                continue
            else:
                if (snake[0][0] == int(i["body"][0][0]) and int(snake[0][1]) == int(i["body"][0][1])) or (snake[0][0] == int(i["body"][1][0]) and int(snake[0][1]) == int(i["body"][1][1])) or (snake[1][0] == int(i["body"][0][0]) and int(snake[1][1]) == int(i["body"][0][1])):
                    curses.beep()
                    alive = False
                    keydict = {"id":clientnumber, "move":5}
                    lastmessage = keydict
                    n.simplesend(json.dumps(keydict))
                    keydict = {"id":int(i["id"]), "move":5}
                    n.simplesend(json.dumps(keydict))
                    break
                elif snake[0] in i["body"]:
                    curses.beep()
                    alive = False
                    keydict = {"id": clientnumber, "move": 0}
                    lastmessage = keydict
                    n.simplesend(json.dumps(keydict))
                    break

        if alive:
            for i in snakearray:
                if int(i["id"]) == int(clientnumber):
                    for b in i["body"]:
                        if b == i["body"][0]: 
                            char = 'X'
                            win.addch(b[0], b[1], char)
                        else: 
                            char = 'D'
                            win.addch(b[0], b[1], char)
                else: 
                    for coord in i["body"]:
                        if coord == i["body"][0]: 
                            char = 'X'
                            win.addch(coord[0], coord[1], char)
                        else: 
                            char = 'S'
                            win.addch(coord[0], coord[1], char)

    curses.endwin()
    print('End game')

curses.initscr()
curses.beep()
curses.beep()
win = curses.newwin(height, width, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

keypress = threading.Thread(target = keythread, args = ())
recv = threading.Thread(target = recv_Serv, args = ())
mainplayer = threading.Thread(target = snakethread, args = (win,))

recv.start()
keypress.start()
mainplayer.start()

mainplayer.join()


print(lastmessage)
print(snakearray)
ID = lastmessage["id"]
move = lastmessage["move"]

if move == 5:
    print('Head on collision!')
    print('Game over')
    print('You lose')
elif move == 0:
    print('You are a loser -> "L"')
    print('xDDDDDDDDD')
    print('Just kidding')
    print('')
    print('Nopes. You are still a loser xDDDDDD')
elif move == 6:
    print('You are the last snake standing. YOU WIN!')

