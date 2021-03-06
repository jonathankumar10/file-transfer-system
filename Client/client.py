# Importing required libraries
import socket
import tkinter as tk
from tkinter import *
import threading
from queue import Queue
import time
    
def user_label(VALUE):
    # configures userlabel
    username_label = Label1.config(text=VALUE)

# function to delete the contents of label
def del_user_entry1():
    return Button1.pack_forget(), Entry1.pack_forget()

# function to delete the contents of label
def del_user_entry2():
    return Button1.pack_forget(), Entry1.pack_forget()

# function to trigger buttons
def user_entry(Button, intvalue):
    Button.wait_variable(intvalue)
    username_entry = Entry1.get()
    Entry1.delete(0, 'end')
    return username_entry

def queue_maker(username):
    # creates queue object if a usernmae is not present to retrieve the data from
    if username in USERNAME_CLIENT:
        if LEXICON_QUEUES.get(username):
            client_queue = LEXICON_QUEUES.get(username)
        else:
            print('Username not in queue so a queue object is created.')
            client_queue = Queue()
            LEXICON_QUEUES[username] = client_queue

    return client_queue

# Client class for server functionalities
class Client():
    def __init__(self,host):
        self.host = host
        self.client = None
        self.USER_STATUS = False
        self.un = ''

    # function to close the gui once called
    def quitbutton(self):
        global root
        self.client.send('END'.encode(FORMAT))
        print('[CLOSED] Client has been closed')
        self.client.close()
        root.destroy()

    # function to check the username of the client
    def usernamecheck(self):
        try:
            while not self.USER_STATUS:
                username = user_entry(Button1, int_var)
                self.un = username
                print(f'[SENT] Username: {username} sent to the server')
                self.client.send(username.encode(FORMAT))
            
                response = self.client.recv(BUFFER).decode(FORMAT)
                if response == 'Username Exists and is Active':
                    print(f'[USERNAME TAKEN] {response}')
                    Label1.config(text ='Username Exists and is Active' )
                    continue

                # User_status is set to true if the username is accepted and the client has gained entry post username checking
                self.USER_STATUS = True
            
            USERNAME_CLIENT.append(username)
            queue_maker(username)

            return (self.USER_STATUS , username)

        except:
            print(f'[ERROR] Error at username at server side..')
            self.client.close()

    # function to send file 
    def file_send(self):
        try:
            while True:
                # sends filename
                user_label('Enter name of the file: ')
                filename = user_entry(Button1, int_var)
                
                self.client.send(filename.encode(FORMAT))
                print('filename is : ', filename)

                f = open(filename, "rb")
                print('Sending file to server...')
                user_label('Sending file to server...')
                data = f.read(BUFFER)
                print('data from client is: ',data)
                if not data:
                    break
                else:
                    # sends contents of file
                    self.client.send(data)
                    print(f'Sent {data!r}')
                    data = f.read(BUFFER)
                
                # response or the spell checked data from server to client
                response = self.client.recv(BUFFER).decode(FORMAT)
                while response == 'POLL':
                    print(response)
                    response = self.client.recv(BUFFER).decode(FORMAT)
                
                self.file_write(response)
                

        except Exception as e:
            print('[ERROR] Error at Client at file transfer', e)

    # function to recieve file
    def file_write(self,response):
        while response == 'Username Exists and is Active' or response == '':
            print(response)
            response = self.client.recv(BUFFER).decode(FORMAT)
        print('response is :' ,response)
        f = open('response.txt', "w")
        f.write(response)
        user_label('Recieved file from server...')
        del_user_entry2()
        f.close()

        print('Done sending')
    
    # function to push lexicon values to a queue object present in a dictionary
    def lexicon_additions(self,username):
        global LEXICON_FLAG
        user_label('Enter your choice of words for lexicon..')
        lexicon = user_entry(Button1, int_var)
        if username in USERNAME_CLIENT:
            if username in LEXICON_QUEUES.keys():
                # this loop basically stores username as keys and queue object as values for LEXICON_QUEUES dictionary
                lexicon_val = LEXICON_QUEUES[username]
                lexicon_val.put(lexicon)
                LEXICON_QUEUES[username] = lexicon_val
                print(
                    f'LEXICON_QUEUES is {LEXICON_QUEUES} and the username is {LEXICON_QUEUES.keys()}, the content is {LEXICON_QUEUES[username]} and the length is {LEXICON_QUEUES[username].qsize()}')
            else:
                print("Recipient Doesn't Exist")
        return LEXICON_QUEUES

    # function to send lexicon updates to server        
    def lexicon_update(self,username):
        global LEXICON_QUEUES
        while True:
            # if username present in lexicon dictionary keys
            if username in LEXICON_QUEUES.keys():
                time.sleep(60)
                if LEXICON_QUEUES:
                    print('Queue is not empty')
                    # get the values from queue object
                    a = LEXICON_QUEUES[username].get()
                    mes = 'PONG '+a
                    # send to server
                    self.client.send(mes.encode(FORMAT))
                else:
                    print('Queue is now emptied')
                    continue


    # function to recieve messages    
    def listener(self, INIT):
        try:
            print(INIT)
            if INIT == True:
                self.client.send('POLL'.encode(FORMAT))
                INIT =False
            while self.USER_STATUS:
                message = self.client.recv(BUFFER).decode(FORMAT)
                if message == 'POLL':
                    print(message)
                    self.client.send('POLL'.encode(FORMAT))
                    continue

                else:
                    self.file_write(message)

        except ConnectionResetError:
            print('Main server is down!!')
            user_label('Main server is down!!')
            self.client.close()
            self.connection(6060)

    
    # function to send messages
    def handle(self,username):
        while self.USER_STATUS != False:

            user_label("Type the word 'SENDGET' to initialize file upload and type 'LEXICON' for lexicon update...")
            choice = user_entry(Button1, int_var)

            if choice == 'SENDGET':
                self.client.send(choice.encode(FORMAT))
                self.file_send()
                continue
            
            if choice == 'LEXICON':
                LEXICON_FLAG = True
                self.lexicon_additions(username)
                continue
            
            if choice == 'END':
                self.USER_STATUS = False
                break
    
    def start(self):
        # Function to ask for the username
        self.USER_STATUS, username= self.usernamecheck()

        if self.USER_STATUS:
            print(f"Client {username} Has been connected")
            threading.Thread(target= self.handle, args=(username)).start()
            threading.Thread(target= self.listener, args=([True])).start()
            threading.Thread(target= self.lexicon_update, args=(username)).start()

    def connection(self, port):
        ADDR = (self.host,port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[WAITING] Waiting to connect to the server..')

        self.client.connect(ADDR)
        print(f'[CONNECTED] Connected to {ADDR}..')

        self.client.send(self.un.encode(FORMAT))

if __name__ == '__main__':
    
    # Global constants
    BUFFER = 1024
    HOST = socket.gethostbyname(socket.gethostname())
    FORMAT = 'utf-8'
    DISCONNECT_MSG = "[DISCONNECT] Disconnected."

    #Global variables
    LEXICON_QUEUES = {}  # handles usernames and their lexicon inputs
    USERNAME_CLIENT = []  # for username checking and handling

    client = Client(HOST)

    try:

        # main GUI of the client with functions called from Client class
        root = tk.Tk()
        root.title("Client")

        int_var = tk.IntVar()

        # Root, On top of root is Screen
        screen = tk.Canvas(root, height= 700, width= 700)
        screen.pack()

        label1 = tk.Label(screen, text="File Transfer system")
        label1.pack(padx=100,pady=4)
        label2 = tk.Label(screen, text="Client")
        label2.pack(padx=100,pady=4)

        Label1 = tk.Label(screen)
        Label1.pack(padx=100,pady=4)
        Label2 = tk.Label(screen)
        Label2.pack(padx=100,pady=4)

        client.connection(5050)

        first_message = client.client.recv(BUFFER).decode(FORMAT)
        user_label(first_message)

        Entry1 = tk.Entry(screen)
        Entry1.pack(side=TOP, expand=True, fill=BOTH)

        Button1 = tk.Button(screen, text='Enter',command=lambda: int_var.set(1))
        Button1.pack(side=TOP, expand=True, fill=BOTH)

        button_quit = tk.Button(screen, text='Exit Program', command = client.quitbutton)
        button_quit.pack(side=TOP, expand=True, fill=BOTH)

        client.start()

        root.mainloop()

    except socket.error as e:
        print('[ERROR] Client could not be established at main')
        print(str(e))