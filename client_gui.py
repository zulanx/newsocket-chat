
from pickle import OBJ
import socket
import threading
import random
import time
import json
import string

import tkinter as tk
from tkinter import DISABLED, END, filedialog, Text
import os
from tkinter.font import NORMAL

#create GUI Class

class GUI: 
    addr = '127.0.0.1'
    port = 5050
    mhdr = 20
    uhdr = 30
    format = 'utf-8'
    username = 'USER_' + (''.join((random.choice(string.ascii_letters)+random.choice(string.digits)) for i in range(10)))
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    connected = False

    SREAD = 'read'
    SSAVE = 'save'
    SETTINGS_FILE = 'client_settings.cfg'
    DISCONNECT_MSG = '!DISCONNECT'


    def __init__(self):
        self.goAhead()

        self.root = tk.Tk()
        self.root.title('Crappy GUI CHAT')
        self.canvas = tk.Canvas(self.root, height=700,width=700,bg="#263D42")
        self.canvas.pack()

        self.canvasFrame = tk.Frame(self.root,bg="#263D42")
        self.canvasFrame.place(relwidth=0.97,relheight=0.9, relx=.01, rely=.01 )

        self.textFrame = tk.Frame(self.root,bg="black")
        self.textFrame.place(relwidth=0.87,relheight=0.9, relx=.01, rely=.01 )

        self.cmdFrame = tk.Frame(self.root,bg="#263D42")
        self.cmdFrame.place(relwidth=0.10, relheight=0.9, relx=.89, rely=.01 )

        self.inputFrame = tk.Frame(self.root,bg="black")
        self.inputFrame.place(relwidth=.98, relheight=0.04, relx=.01, rely=.915)

        self.chatBox = tk.Text(self.textFrame, width=1,height=1,bg="black", fg="white")
        self.chatBox.insert(END,f'Hello, {self.username}!\n\n')
        self.chatBox.place(relwidth=1,relheight=1)

        self.connectButton = tk.Button(self.cmdFrame, text="Connect", padx=10, pady=5, fg="white", bg="#263D42", width=6)
        self.connectButton.pack(side="top")
            

        self.inputBox = tk.Entry(self.inputFrame, width=101, bg="black", fg="white")
        self.inputBox.pack(side='left')
        self.inputBox.config(cursor="arrow")

        self.sendButton = tk.Button(self.inputFrame, text="Send", padx=10, pady=5, fg="white", bg="#263D42", width=6, command=lambda : self.send_button(self.inputBox.get()))
        self.sendButton.pack(side='right')


         #maybe add login?

        
        
        
        self.inputBox.focus()

        self.root.mainloop()
       

    def goAhead(self):
        self.settings(self.SREAD)
        SADDR = (self.addr,self.port)

        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect(SADDR)
        self.connected = True
        self.consoleRPT(f'Server',f'{self.addr}:{self.port}','CONNECTED')

        recv_thread = threading.Thread(target=self.recvmsg)
        recv_thread.start()

    
    def settings(self,task):
        if task.lower() == self.SSAVE:
            try:
                with open(self.SETTINGS_FILE,'w') as sset:
                    ssettings = {"server": self.addr, "port": self.port, "username": self.username}
                    print('Dictionary:',ssettings)
                    json.dump(ssettings,sset)
                    self.consoleRPT(f'settings({task})',f'Completed: {self.addr}:{self.port}','SAVE SETTINGS')
            except:
                self.consoleRPT('settings()',f'Failed to save file [{self.SETTINGS_FILE}]: settings({task})','ERROR')
        elif task.lower() == self.SREAD:
            try:
                with open(self.SETTINGS_FILE,'r') as fset:
                    fsettings = json.load(fset)
                    self.addr = fsettings['server']
                    self.port = fsettings['port']
                    self.username = fsettings['username']
                    if self.username == '':
                        self.username = 'USER_' + (''.join((random.choice(string.ascii_letters)+random.choice(string.digits)) for i in range(10)))
                    self.consoleRPT(f'settings({task})',f'Completed: {self.addr}:{self.port}','LOAD SETTINGS')
            except:
                self.consoleRPT(f'settings({task})',f'Failed to load file [{self.SETTINGS_FILE}]: settings({task})','ERROR')
                self.consoleRPT(f'settings({task})',f'Using defaults: {self.addr}:{self.port}','LOAD DEFAULTS')
        else:
            self.consoleRPT('settings()',f'Invalid Argument: settings({task})','ERROR')
            os._exit(1)
        print('username len: ',len(self.username),f'\n{self.username}')
    def send_button(self,sndmsg):
        if sndmsg.lower() == 'quit':
            sendIT = threading.Thread(target=self.sendmsg,args=((self.DISCONNECT_MSG,)))
            sendIT.start()
            self.connected = False
            time.sleep(1)
            os._exit(1)
        elif sndmsg == '':
            pass
        else:
            self.chatBox.config(state=DISABLED)
            self.inputBox.delete(0,END)
            self.inputBox.focus()
            sendIT = threading.Thread(target=self.sendmsg,args=((sndmsg,)))
            sendIT.start()



    def sendmsg(self,sndmsg):

            message = sndmsg.encode(self.format)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.format)
            send_length += b' ' * (self.mhdr - len(send_length))
            user_length = self.username.encode(self.format)
            user_length += b' ' * (self.uhdr - len(user_length))
        
            #print('Message:>>',f'[{len(send_length)}][{len(user_length)}]',send_length.decode(self.format)+user_length.decode(self.format))

            self.client.send(send_length+user_length)
            self.client.send(message)

    
    def recvmsg(self):
        while self.connected:
            msg_length = self.client.recv(self.mhdr+self.uhdr).decode(self.format)
            if msg_length:

                username = msg_length[self.mhdr:].strip()
                msg_length = int(msg_length[:self.mhdr])
                msg = self.client.recv(msg_length).decode(self.format)
                #if username != self.username:
                #    print(f"\n[{username}]>>> {msg}")   
                self.chatBox.config(state=NORMAL)
                self.chatBox.insert(END,f'[{username}]> {msg}\n')
                self.chatBox.config(state=DISABLED)
                self.chatBox.see(END)
                print(f"\n[{username}]>>> {msg}")
 

    def consoleRPT(self,name,desc,etype):
        print(f'[{etype.upper()}] {name} : {desc}')


def main():
    gFace = GUI()

if __name__ == '__main__':
    main()


