# Importing required libraries
import socket
import tkinter as tk
from tkinter import *
import threading
import time

# function to close the gui and server once called
def quit(root):
    print('[CLOSED] Server has been closed')
    server.close()
    root.destroy()

# function to update count on the GUI every second
def update(Label1,root):
    # updates count
    global USER_STATUS
    if USER_STATUS == True:
        PRINT_UI = count
        Label1.config(text = str(PRINT_UI))
    else:
        Label1.config(text = "0")
    root.after(1000, lambda: update(Label1, root))

# function to update the active usernames on the GUI every second
def show_names(Label2,root):
    # updates active users in server
    if USER_STATUS == True:
        Label2.config(text="\t".join(map(str, CLIENTS)))
    else:
        Label2.config(text = "No Client Connected")
    root.after(1000, lambda: show_names(Label2, root))

# main GUI build for the server
def tkinter_display():
    # Root, On top of root is Screen
    root = tk.Tk()
    root.title("Server")

    screen = tk.Canvas(root, height= 700, width= 700)
    screen.pack()

    # GUI Title
    title1 = tk.Label(screen, text="File Transfer system")
    title1.pack(pady=20)
    title2 = tk.Label(screen, text="Server")
    title2.pack(pady=5)

    # GUI Active usernames and Total number of users 
    title_label1 = tk.Label(screen,text = "Active Usernames in this Session ->")
    title_label1.pack(pady=20, padx=200)
    Label1 = tk.Label(screen)
    Label1.pack(pady=20)

    title_label2 = tk.Label(screen, text = "Name of Users in this Session ->")
    title_label2.pack(pady=20, padx=200)   
    Label2 = tk.Label(screen)
    Label2.pack(pady=20)

    update(Label1,root)
    show_names(Label2,root)

    button_quit = tk.Button(screen, text='Exit Program', command =lambda: quit(root))
    button_quit.pack(pady=50)

    root.mainloop()

# Server class for server functionalities
class Server():
    # Server code
    def __init__(self,client,addr):
        self.client = client
        self.addr = addr
        # self.bclient= bclient
        self.thread1 = None
        self.thread2 = None
        self.polling = False
        
    # function to check the username of the incoming clients
    def usernameChecker(self):
        FLAG = False
        try:
            # the following loop runs till the client enetrs an unused username
            while not FLAG:
                username = self.client.recv(BUFFER).decode(FORMAT)
                print(f'Username sent from the client is {username}')
                if (username in CLIENTS):
                    message = 'Username Exists and is Active'
                    self.client.send(message.encode(FORMAT))
                    continue
                FLAG = True

            if username not in CLIENTS:
                # add client username and it's address to the clients dictionary
                CLIENTS[username] = self.addr
                self.polling = True
                print(f'{username} added to the list')
                self.client.send('[ADDED] Added to the username list at the server.'.encode(FORMAT))
                # info = 'cc '+username +' '+self.addr[1]
                # print(info)
                # self.bclient.send(info.encode(FORMAT)+self.addr)
                # print('Sent the username to the backup server for storage')
                
            global USER_STATUS
            global count

            USER_STATUS =True
            count += 1

            return USER_STATUS,username
        
        except:
            print(f'[ERROR] Error at username at server side..')
            server.close()
    
    # function to check and apply file transfer and lexicon checking
    def file_transfer(self,client):
        try:
            # Open server lexicon
            f = open('server.txt', "r")
            serverlexicon = f.read()
            LEXICON_LIST = serverlexicon.split()

            output = ""
            print ('[WAITING] Awaiting command from client..')
            print('[WAITING] What is the filename')

            # filename asked
            filename = client.recv(BUFFER).decode(FORMAT)
            while filename == 'POLL' or filename == '':
                print('POLL')
                filename = client.recv(BUFFER).decode(FORMAT)

            print('filename is :',filename)

            # contents of user supplied text comapred to the lexcion present in server
            data = client.recv(BUFFER).decode(FORMAT)
            while data == 'POLL' or data == '':
                print('POLL')
                data = client.recv(BUFFER).decode(FORMAT)
            
            print('data is :',data)

            for input_word in data.split():
                if input_word in LEXICON_LIST:
                    out = f"[{input_word}] "
                    output += out
                else:
                    output += f"{input_word} "

            print('op is : ',output)
            # sends the updated file back to the client
            client.send(output.encode(FORMAT))


        except Exception as e:
            print(e)
            print('[ERROR] Error at the file transactions section at Server')
    
    # delete clients and their threads once disconnected
    def delete_clients(self,username):
        global count
        global USER_STATUS
        # delete the key and its corresponding value in the dictionary
        del CLIENTS[username]
        count -=1
        self.thread1.join()
        USER_STATUS = False
    
    # main server function that handles incoming messages from clients    
    def recieve(self):
        global count
        global USER_STATUS
        # check for username
        USER_STATUS,username = self.usernameChecker()

        print(f'[CONNECTED] Connected to {self.addr} and the username is:{username} and the count is {count}')
        
        threading.Thread(target= self.poll, args=()).start()

        try:
            # while user is active the following while loop works
            while USER_STATUS:


                message = self.client.recv(BUFFER).decode(FORMAT)

                if message == 'SENDGET':
                    self.file_transfer(self.client)
                    continue
                
                if message== 'END':
                    self.delete_clients(username)
                    continue
                
                if message == 'HELLO':
                    print(message)
                    continue

                if message == 'POLL':
                    print(message)
                    
  
        except:
            pass
    
    def poll(self):
        # while user is active the following while loop works
        self.polling = True
        while self.polling:
            time.sleep(5)
            self.client.send('POLL'.encode(FORMAT))

    def start(self):
        # Forking a thread for each client
        threading.Thread(target= self.recieve, args=()).start()

 


# Main program
if __name__ == '__main__':
    
    # Global constants
    BUFFER = 1024
    PORT = 5050
    BACKUP_PORT = 6060
    HOST = socket.gethostbyname(socket.gethostname())
    ADDR = (HOST,PORT)
    BACKUPADDR=(HOST,BACKUP_PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MSG = "[DISCONNECT] Disconnected."

    # Global variables
    CLIENTS = {}
    ADDRESSES = {}
    count = 0
    USER_STATUS = False
    BCLIENTS= {}

    try:
        
        # server creation
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        # server listens for incoming clients
        server.listen()

        print('[STARTING] server is starting at HOST: ',HOST +' and PORT: ', PORT)
        print('[LISTENING] Server is listening..')

        # create a new thread for the GUI
        threading.Thread(target = tkinter_display).start()

        # bclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print('[WAITING] Waiting to connect to the backup server..')

        # bclient.connect(BACKUPADDR)
        # print(f'[CONNECTED] Connected to backupserver with address : {BACKUPADDR}')

        while True:
            # Handles connection from incoming clients
            client,addr = server.accept()
            print(client)
            print(addr)
            client.send("Greetings from the Server! Now type your username to enter!".encode(FORMAT))
            # save client and client address to the ADDRESS dictionary 
            ADDRESSES[client] = addr
            Server(client, addr).start()
    
    except socket.error as e:
        print('[ERROR] Server could not be established at main')
        server.close()