
import socket
from sqlite3 import connect
import threading
import random
import time
import json
import string

import tkinter as tk
from tkinter import filedialog, Text
import os



#assign base variable values in case we can't load settings later.
class ServerSettings:
    addr = '127.0.0.1'
    port = 5050
    mhdr = 20
    uhdr = 30
    format = 'utf-8'
    username = 'USER_' + (''.join((random.choice(string.ascii_letters)+random.choice(string.digits)) for i in range(15)))
    client = ''
    connected = False

#constants
SREAD = 'read'
SSAVE = 'save'
SETTINGS_FILE = 'client_settings.cfg'
DISCONNECT_MSG = '!DISCONNECT'





def interface():
    pass

def main():
    iface = threading.Thread(target=interface)
    iface.start()

    settings(SREAD)
    SADDR = (ServerSettings.addr,ServerSettings.port)

    ServerSettings.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ServerSettings.client.connect(SADDR)
    ServerSettings.connected = True
    consoleRPT(f'Server',f'{ServerSettings.addr}:{ServerSettings.port}','CONNECTED')

    recv_thread = threading.Thread(target=recv)
    recv_thread.start()

    while ServerSettings.connected:
        msg = input(f"{ServerSettings.username} > ")
        if msg.lower() == 'quit':
            send(DISCONNECT_MSG)  
            ServerSettings.connected = False
        elif msg == '':
            pass
        else:
            send(msg)
    time.sleep(5)
    os._exit(1)

def send(msg):
    message = msg.encode(ServerSettings.format)
    msg_length = len(message)
    send_length = str(msg_length).encode(ServerSettings.format)
    send_length += b' ' * (ServerSettings.mhdr - len(send_length))
    user_length = ServerSettings.username.encode(ServerSettings.format)
    user_length += b' ' * (ServerSettings.uhdr - len(user_length))
    
    #print('Message:>>',f'[{len(send_length)}][{len(user_length)}]',send_length.decode(ServerSettings.format)+user_length.decode(ServerSettings.format))

    ServerSettings.client.send(send_length+user_length)
    ServerSettings.client.send(message)
    

def recv():
    while ServerSettings.connected:
        msg_length = ServerSettings.client.recv(ServerSettings.mhdr+ServerSettings.uhdr).decode(ServerSettings.format)
        if msg_length:
            username = msg_length[ServerSettings.mhdr:].strip()
            msg_length = int(msg_length[:ServerSettings.mhdr])
            msg = ServerSettings.client.recv(msg_length).decode(ServerSettings.format)
            if username != ServerSettings.username:
                print(f"\n[{username}]>>> {msg}")

def settings(task):
    if task.lower() == SSAVE:
        try:
            with open(SETTINGS_FILE,'w') as sset:
                ssettings = {"server": ServerSettings.addr, "port": ServerSettings.port, "username": ServerSettings.username}
                print('Dictionary:',ssettings)
                json.dump(ssettings,sset)
                consoleRPT(f'settings({task})',f'Completed: {ServerSettings.addr}:{ServerSettings.port}','SAVE SETTINGS')
        except:
            consoleRPT('settings()',f'Failed to save file [{SETTINGS_FILE}]: settings({task})','ERROR')
    elif task.lower() == SREAD:
        try:
            with open(SETTINGS_FILE,'r') as fset:
                fsettings = json.load(fset)
                ServerSettings.addr = fsettings['server']
                ServerSettings.port = fsettings['port']
                ServerSettings.username = fsettings['username']
                if ServerSettings.username == '':
                    ServerSettings.username = input("Enter a username: ")
                consoleRPT(f'settings({task})',f'Completed: {ServerSettings.addr}:{ServerSettings.port}','LOAD SETTINGS')
        except:
            consoleRPT(f'settings({task})',f'Failed to load file [{SETTINGS_FILE}]: settings({task})','ERROR')
            consoleRPT(f'settings({task})',f'Using defaults: {ServerSettings.addr}:{ServerSettings.port}','LOAD DEFAULTS')
    else:
        consoleRPT('settings()',f'Invalid Argument: settings({task})','ERROR')
        quit()

def consoleRPT(name,desc,etype):
    print(f'[{etype.upper()}] {name} : {desc}')

if __name__ == '__main__':
    main()


