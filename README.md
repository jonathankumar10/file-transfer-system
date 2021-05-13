# file-transfer-system

Objectives:
You will write a client/server system that will check for commonly misspelled words in a block of text. The system will 
be demonstrated with a server and three client processes. Each client process will connect to the server over a socket 
connection and register a username at the server. The server should be able to handle all three clients simultaneously 
and display the names of the connected clients in real time. 
Two or more clients may not use the same username simultaneously. Should the server detect a concurrent conflict in 
username, the client’s connection should be rejected, and the client’s user should be prompted to input a different 
name.
A client will connect to the server over a socket and upload a user-supplied text file. The server will have a lexicon of 
commonly misspelled words that it will read from a file upon startup. The server will scan the user-supplied text file 
uploaded by the client and check each word against the lexicon. Any word in the user-supplied text file found in the 
lexicon will be surrounded by brackets. When the server is finished identifying words, the text file will be returned to 
the client and the connection will be closed.
For example, assume a text file with this text was uploaded to the server:
the quck brown fox jumpz over the lazy dg
If the server had a lexicon with the following contents:
quck jumpz dg
The server should return a a text file with the following contents:
the [quck] brown fox [jumpz] over the lazy [dg]
Words in the lexicon will be delimited with white space and character case should be ignored. The files should be 
plain .txt files and the contents may be created and examined with any basic text editor (for instance, Notepad on 
Windows or TextEdit on macOS).
Each client will have the ability to make additions to the server’s lexicon. The client GUI will present the user with the 
ability to enter words for inclusion into the lexicon. What GUI components are used to facilitate this are left to the 
developer’s discretion.
Words entered by the user will be placed into a queue and presented on the client’s GUI. Every 60 seconds, the server 
will poll each client’s queue. If the queue is not empty, the server should retrieve the contents of the queue and add 
those to its lexicon. 
Once the client has been polled, the contents of the queue should be purged. The server should remove any duplicate 
entries in the lexicon. Subsequent comparison between user-supplied text files and the lexicon should reflect the 
updated contents of the lexicon.
The functionality of the client and server are summarized as follows.
The system will maintain a backup server (B) that will be prepared to assume the responsibilities of the primary server 
(P) if the primary server fails. B will have a copy of P's initial lexicon and lexicon updates that are applied at P should be 
pushed and applied to B. The updates to B will originate from P, not from the clients (e.g., B may not poll clients for 
updates while P is active).
In the event that P becomes unavailable, clients (C) should recognize that P is not available, connect to B, and resume
their normal operation. The mechanism used for C and B to recognize that P is unavailable is left to the developer's
discretion, but it may not involve a push notification from P to either C or B (a server does not know that it's about to
crash).
The sequence is illustrated as follows. At time t1, the system is operating normally. C are uploading text files for spell
check, P is polling clients for updates to the lexicon, and P is pushing applicable updates to B.
At time t2, P crashes. B and C have yet to recognize that P is not responding.
At time t3, B and C have recognized that P is not available. C have connected to B, and B has assumed P's 
responsibilities. C is now uploading text files for spell check and B is polling clients for updates to the lexicon.
For the purposes of this lab, P is not expected to resume operation.

Client:
Startup
1. Prompt the user to input a username.
2. Connect to the server over a socket and register the username.
a. When the client is connected, the user should be notified of the active connection.
b. If the provided username is already in use, the client should disconnect and prompt the user to input a 
different username.
3. Simultaneously handle ‘File Upload’ and ‘Lexicon Additions’ until manually killed by the user.
File Upload
1. Upload the user-supplied text file to the server and notify the user of upload completion.
2. Wait until the server has completed checking the file for spelling errors.
3. Receive the updated text file from the server and notify the user that the spell check sequence has completed.
4. Return to Step 1 of ‘File Upload’ until manually terminated by the user.
Lexicon Additions
1. Present the user with the ability to enter additions to the lexicon via the GUI.
2. Place the entered text into a queue. There should not be an upper bound on the size of the queue.
3. When polled by the server, the client should indicate that a poll was received and print the contents of the 
queue retrieved by the server (if any).
4. After polling, the client should clear the contents of the queue (if any).
5. Return to Step 1 of ‘Lexicon Additions’ until manually terminated by the user.
On Primary Server Failure
1. Clients should recognize that the primary server is not responding and print a notification to their GUIs.
2. Connect to the backup server and notify the user of the switch to a backup.
3. Resume 'File Upload' and 'Lexicon Additions' until manually terminated by the user.


Primary Server:
The server should support three concurrently connected clients. The server should indicate which of those clients are 
presently connected on its GUI. The server will execute the following sequence of steps:
Startup
1. Startup and listen for incoming connections.
2. Print that a client has connected, and:
a. If the client’s username is available (e.g., not currently being used by another client), fork a thread to 
handle that client; or,
b. If the username is in use, reject the connection from that client.
3. Simultaneously handle ‘Spell Check’ and ‘Polling’ until manually killed by the user.
Spell Check
1. Receive a user-supplied text file from the client.
2. Check all words in the user-supplied text file against the lexicon and identify matches.
3. Return the updated file to the client.
4. Return to Step 1 of ‘Spell Check’ until manually killed by the user.
Polling
1. Every 60 seconds, poll clients for the status of their queues.
2. Retrieve contents from queue, if any.
3. Compare retrieved contents against present contents of lexicon and remove duplicates, if any.
4. Apply retrieved contents to lexicon.
5. Send updates to the lexicon to the backup server.
6. Turn to Step 1 of ‘Polling’ until manually killed by the user.


Backup Server:
Startup
1. Startup and listen for an incoming connection from the primary server.
2. Print that the primary server has connected.
3. Accept and apply updates received from the server to local copy of lexicon.
On Primary Server Failure
1. Notify the user that the primary server is not available.
2. Listen for incoming connections from clients.
3. Assume the responsibilities of 'Spell Check' and 'Polling' until manually killed by the user.