import socket
import sys
import threading
import json
import time
from random import randint 

#client - two threads - listen and send to all clients
HOST = '127.0.0.1'
PORT = 8083

threads = []
pos = []
num = 0
numofclients = 3
lastmessage = ''
snakedictionary = []

def thread(ip, port, cl, clientno):
    global threads
    global pos 
    global num
    global lastmessage
    global snakedictionary
    global numofclients
    active = True
    print('client: ', clientno)

    cl.sendall(str(clientno).encode('ascii')) #sending client number

    while (len(threads) < numofclients): #waiting for two players to join
        continue

    snake = json.loads(cl.recv(1024)) #recieiving self ki body
    item = {"id": clientno, "body": snake}
    print(item)
    print('Appending to ', snakedictionary)
    snakedictionary.append(item)

    while(len(snakedictionary) < numofclients): #waiting till both snakes have sent initial positions
        time.sleep(0.2)
        continue

    for snaku in snakedictionary:
        for snaku2 in snakedictionary:
            if snaku["id"] == snaku2["id"]:
                continue
            else:
                if snaku["body"][0] in snaku2["body"] or snaku["body"][1] in snaku2["body"] or snaku["body"][2] in snaku2["body"] or snaku["body"][3] in snaku2["body"]:
                    x = randint(1, 17)
                    y = randint(1, 50)
                    snaku["body"] = [[x, y+3], [x,y+2], [x, y+1], [x, y]]
                    continue
                else:
                    continue
    #sending initial positions to the respective clients
    print('Sending ', snakedictionary, ' to all clients')
    cl.sendall((json.dumps(snakedictionary)).encode('ascii'))
    print('Sent')

    while active:
        try: 
            d = json.loads(cl.recv(1024).decode('ascii')) #client dictionary 
            lastmessage = d

            print('Recieved: ', d)
            ID = d['id']
            key = d['move']

            if key == 5:
                print('Connection lost')
                for x in threads:
                    xid = x["clientno"]
                    if int(xid) == int(ID): 
                        threads.remove(x)
            
                d2 = json.loads(cl.recv(1024).decode('ascii')) #client dictionary 
                lastmessage = d2
                print('Recieved: ', d2)
                secID = d2['id']
                seckey = d2['move']

                for x in threads:
                    xid = x["clientno"]
                    if int(xid) == int(secID): 
                        threads.remove(x)

                for i in threads:
                    print('Sending: ', d2)
                    icl = i["client"]
                    icl.sendall(json.dumps(d2).encode('ascii'))

            if key == 0:
                print('Connection lost')
                for i in threads:
                    iid = i["clientno"]
                    if int(iid) == int(ID):
                        threads.remove(i)

            if len(threads) == 1:
                print('Sending', 6)
                idcl = threads[0]["clientno"]
                item = {"id": idcl, "move": 6}
                threads[0]["client"].sendall(json.dumps(item).encode('ascii'))
                print('Connection lost')
                threads.remove(threads[0])

            else:
                for i in threads:
                    print('Sending: ', d)
                    icl = i["client"]
                    icl.sendall(json.dumps(d).encode('ascii'))

            if key == 0 or key == 5 or len(threads) == 1:
                break

        except Exception as e: 
            break

    print(lastmessage)


    snakedictionary = []
    print('Connection closed')
    cl.close()

    for i in threads:
        print(i)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((HOST, PORT))
    except:
        print('Bind failed. Error: ' + str(sys.exc_info()))
        sys.exit()

    s.listen(numofclients)
    print("The server is ready to recieve")

    while True:
        try:
            c,info = s.accept()
            ip, port = str(info[0]), str(info[1])
            print('Connected with ' + ip + ': ' + port)  
            num = len(threads)

            try:    
                item = {"clientno": num, "client": c}
                threads.append(item)    
                t = threading.Thread(target = thread, args = (ip, port, c, num))
                print('The thread has started')
                t.start()
            except:
                print('Thread did not start')
                traceback.print_exc()
        except:
            print("Server shut down")
            sys.exit()

    s.close()

if __name__ == "__main__":
    main()
