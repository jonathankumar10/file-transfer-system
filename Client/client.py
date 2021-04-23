# Importing required libraries
import socket
import tkinter as tk
from tkinter import *
import threading

def quitbutton():
    client.send('END'.encode(FORMAT))
    print('[CLOSED] Client has been closed')
    root.destroy()
    
def user_label(VALUE):
    # configures userlabel
    username_label = Label1.config(text=VALUE)

def del_user_entry1():
    return Button1.pack_forget(), Entry1.pack_forget()

def del_user_entry2():
    return Button1.pack_forget(), Entry1.pack_forget()

def user_entry(Button, intvalue):
    Button.wait_variable(intvalue)
    username_entry = Entry1.get()
    Entry1.delete(0, 'end')
    return username_entry

class Client():
    
    def usernamecheck(self,client):
        
        USER_STATUS = False
        try:
            while not USER_STATUS:
                username = user_entry(Button1, int_var)
                print(f'[SENT] Username: {username} sent to the server')
                client.send(username.encode(FORMAT))
            
                response = client.recv(BUFFER).decode(FORMAT)
                print(response == 'Username Exists and is Active')
                if response == 'Username Exists and is Active':
                    print(f'[USERNAME TAKEN] {response}')
                    # Label1 = tk.Label(screen, text='Username Taken & Active')
                    Label1.config(text ='Username Exists and is Active' )
                    continue
                USER_STATUS = True

            return (USER_STATUS , username)

        except:
            print(f'[ERROR] Error at username at server side..')
            client.close()
        
    def file_transfer(self,client):
        try:
            while True:
                # sends filename
                user_label('Enter name of the file: ')
                filename = user_entry(Button1, int_var)
                
                client.send(filename.encode(FORMAT))
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
                    client.send(data)
                    print(f'Sent {data!r}')
                    data = f.read(BUFFER)
                
            # response or the spell checked data from server to client
                response = client.recv(BUFFER).decode(FORMAT)
                print('response is :' ,response)
                f = open(filename, "w")
                f.write(response)
                user_label('Recieved file from server...')
                del_user_entry2()
                f.close()

                print('Done sending')
                break

        except Exception as e:
            print('[ERROR] Error at Client at file transfer', e)


if __name__ == '__main__':
    
    # Global constants
    BUFFER = 1024
    PORT = 5050
    HOST = socket.gethostbyname(socket.gethostname())
    ADDR = (HOST,PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MSG = "[DISCONNECT] Disconnected."

    try:

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

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[WAITING] Waiting to connect to the server..')

        client.connect(ADDR)
        print(f'[CONNECTED] Connected to {ADDR}..')

        first_message = client.recv(BUFFER).decode(FORMAT)
        user_label(first_message)

        Entry1 = tk.Entry(screen)
        Entry1.pack(side=TOP, expand=True, fill=BOTH)

        Button1 = tk.Button(screen, text='Enter',command=lambda: int_var.set(1))
        Button1.pack(side=TOP, expand=True, fill=BOTH)

        # Function to ask for the username
        USER_STATUS, username= Client().usernamecheck(client)
        print(f'{USER_STATUS} and {username}')

        button_quit = tk.Button(screen, text='Exit Program', command = quitbutton)
        button_quit.pack(side=TOP, expand=True, fill=BOTH)

        if USER_STATUS:
            user_label(f"Client {username} Has been connected")

            while USER_STATUS != False:

                user_label("Type the word 'SENDGET' to initialize file upload...")
                choice = user_entry(Button1,int_var)
                client.send(choice.encode(FORMAT))

                if choice == 'SENDGET':
                    Client().file_transfer(client)
                    USER_STATUS = False

        root.mainloop()

    except socket.error as e:
        print('[ERROR] Client could not be established at main')
        print(str(e))