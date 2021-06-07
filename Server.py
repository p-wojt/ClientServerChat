from socket import *
from _thread import *
import threading
from datetime import datetime

threading_lock = threading.Lock()

LIST_OF_NICKNAMES = list()
CLIENTS = list()


def get_server_time():
    return datetime.now().strftime("%H:%M:%S")


def client_thread(client):
    global LIST_OF_NICKNAMES, CLIENTS
    work = True
    checked_nickname = False
    while work:
        data = client.recv(1024)
        msg = data.decode(encoding='UTF-8')
        if str(msg).startswith('CLOSE'):
            LIST_OF_NICKNAMES.remove(msg[5:])
            client.send('CLOSE'.encode())
            work = False
            break
        if checked_nickname is False:
            checked_nickname = True
            if msg not in LIST_OF_NICKNAMES:
                LIST_OF_NICKNAMES.append(msg)
                client.send('Accepted'.encode())
            else:
                client.send('Deliced'.encode())
                work = False
        else:
            threading_lock.acquire()
            if str(msg).startswith('Java OPEN'):
                for connection in CLIENTS:
                    connection.send(('COMMAND Java' + get_server_time() + ' ' + msg[10:] + ' dolaczyl do chatu!').encode())
            elif str(msg).startswith('C++ OPEN'):
                for connection in CLIENTS:
                    connection.send(('COMMAND C++' + get_server_time() + ' ' + msg[9:] + ' dolaczyl do chatu!').encode())
            elif str(msg).startswith('Python OPEN'):
                for connection in CLIENTS:
                    connection.send(('COMMAND Python' + get_server_time() + ' ' + msg[12:] + ' dolaczyl do chatu!').encode())
            elif str(msg).startswith('C# OPEN'):
                for connection in CLIENTS:
                    connection.send(('COMMAND C#' + get_server_time() + ' ' + msg[8:] + ' dolaczyl do chatu!').encode())
            elif str(msg).startswith('COMMAND'):
                for connection in CLIENTS:
                    channel = str(msg.split(' ')[1])
                    connection.send(('COMMAND ' + channel + get_server_time() + msg[len(channel)+8:]).encode())
            threading_lock.release()
    CLIENTS.remove(client)
    client.close()


s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 8888))
s.listen(5)

while True:
    client, addr = s.accept()
    print('Nowe polaczenie z ', addr)
    start_new_thread(client_thread, (client,))
    CLIENTS.append(client)

s.close()
