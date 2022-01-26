
import random
import string
import socket
import threading
import json
import time
import os

#assign base variable values in case we can't load settings later.
class ServerSettings:
    addr = '127.0.0.1'
    port = 5050
    mhdr = 20
    uhdr = 30
    format = 'utf-8'
    connections = []
class MessageBuffer:
    msg = []
    msgID = 0


#constants
SREAD = 'read'
SSAVE = 'save'
SETTINGS_FILE = 'server_settings.cfg'
DISCONNECT_MSG = '!DISCONNECT'

#other variables




def main():
    consoleRPT('Startup','Initializing','START')
    settings(SREAD)
    SADDR = (ServerSettings.addr,ServerSettings.port)
    
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(SADDR)

    server.listen()
    consoleRPT('Server Listening',f'{ServerSettings.addr}:{ServerSettings.port}','LISTENING')

    relayThread = threading.Thread(target=msg_relay)
    relayThread.start()
    
    inputThread = threading.Thread(target=handle_input)
    inputThread.start() 

    while True:
        conn,addr = server.accept()
        client_thread = threading.Thread(target=handle_client,args=(conn,addr))
        client_thread.start()
        ServerSettings.connections.append([conn,addr])
        consoleRPT(f'From: {addr}',f'Total Connections: {len(ServerSettings.connections)}','NEW CONNECTION')

    server.close()




def settings(task):
    if task.lower() == SSAVE:
        try:
            with open(SETTINGS_FILE,'w') as sset:
                ssettings = {"server": ServerSettings.addr, "port": ServerSettings.port}
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
                consoleRPT(f'settings({task})',f'Completed: {ServerSettings.addr}:{ServerSettings.port}','LOAD SETTINGS')
        except:
            consoleRPT(f'settings({task})',f'Failed to load file [{SETTINGS_FILE}]: settings({task})','ERROR')
            consoleRPT(f'settings({task})',f'Using defaults: {ServerSettings.addr}:{ServerSettings.port}','LOAD DEFAULTS')
    else:
        consoleRPT('settings()',f'Invalid Argument: settings({task})','ERROR')
        quit()

def consoleRPT(name,desc,etype):
    print(f'[{etype.upper()}] {name} : {desc}')

def msg_relay():
    while True:
        if MessageBuffer.msg:
            send_msg = MessageBuffer.msg.pop()
            for active in ServerSettings.connections:
                conn,addr = active
                message = send_msg[3].encode(ServerSettings.format)
                msg_length = len(message)
                send_length = str(msg_length).encode(ServerSettings.format)
                send_length += b' ' * (ServerSettings.mhdr - len(send_length))
                user_length = send_msg[2].encode(ServerSettings.format)
                user_length += b' ' * (ServerSettings.uhdr - len(user_length))
                conn.send(send_length+user_length)
                conn.send(message)
                        
        


def handle_client(conn,addr):
    consoleRPT(f'handle_client({addr})',f'','NEW CONNECTION')
    connected = True
    
    while connected:
        msg_length = conn.recv(ServerSettings.mhdr+ServerSettings.uhdr).decode(ServerSettings.format)
        if msg_length:
            username = msg_length[ServerSettings.mhdr:].strip()
            #print('testing',msg_length)
            msg_length = int(msg_length[:ServerSettings.mhdr].strip())
            msg = conn.recv(msg_length).decode(ServerSettings.format)
            consoleRPT(f'handle_client({addr})',f'Msg:[{username}] {msg}','RECV')
            if msg == DISCONNECT_MSG:
                connected=False
                ServerSettings.connections.remove([conn,addr])
                consoleRPT(f'handle_client({addr})',f'{msg} :: Total Connections: {len(ServerSettings.connections)}','CLIENT DISCONNECT')

            MessageBuffer.msgID += 1
            MessageBuffer.msg.append([MessageBuffer.msgID,addr,username,msg])
    conn.close()

def handle_input():
    while True:
        inText = input(':')
        if inText.lower() == 'quit':
            os._exit(1)
        elif inText.lower() == 'connections':
            consoleRPT(f'Active Connections',f'{len(ServerSettings.connections)}','INFO')
        elif inText.lower() == 'purge':
            ServerSettings.connections = []
            consoleRPT(f'Active Connections',f'{len(ServerSettings.connections)}','INFO')

if __name__ == '__main__':
    main()

