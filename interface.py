from sqlite3 import connect
import tkinter as tk
from tkinter import filedialog, Text







root = tk.Tk()

canvas = tk.Canvas(root, height=700,width=700,bg="#263D42")
canvas.pack()

canvasFrame = tk.Frame(root,bg="#263D42")
canvasFrame.place(relwidth=0.97,relheight=0.9, relx=.01, rely=.01 )

textFrame = tk.Frame(root,bg="black")
textFrame.place(relwidth=0.87,relheight=0.9, relx=.01, rely=.01 )

cmdFrame = tk.Frame(root,bg="#263D42")
cmdFrame.place(relwidth=0.10, relheight=0.9, relx=.89, rely=.01 )

inputFrame = tk.Frame(root,bg="black")
inputFrame.place(relwidth=.98, relheight=0.04, relx=.01, rely=.915)

connectButton = tk.Button(cmdFrame, text="Connect", padx=10, pady=5, fg="white", bg="#263D42", width=6)
connectButton.pack(side="top")
    

inputBox = tk.Entry(inputFrame, width=101, bg="black", fg="white")
inputBox.pack(side='left')

sendButton = tk.Button(inputFrame, text="Send", padx=10, pady=5, fg="white", bg="#263D42", width=6)
sendButton.pack(side='right')




root.mainloop()

