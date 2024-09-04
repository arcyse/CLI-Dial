import socket
import threading

'''
YOU CAN SEND PYTHON OBJECT BY SERIALIZING THROUGH:
A) PICKLE
OR
B) SOCKETIO
'''

'''
TO DO CLIENT-TO-CLIENT COMMUNICATION, USE A GLOBAL LIST OF MESSAGES AND UPDATE BY SENDING TO ALL CLIENTS
'''
# Define fixed-length header of 64 bytes which describes the length of the message:
HEADER = 64
PORT = 5050
#SERVER = "192.168.56.1" #local IPv4 address (ipconfig)
SERVER = socket.gethostbyname(socket.gethostname()) # You can use public IP address for it to work across the internet
ADDR = (SERVER, PORT) # Unique address to bind socket to
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

# Create socket:
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Thread function to handle client-server communication:
def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        # Wait to receive message from client:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f'{addr} sent: {msg}')
            if msg == DISCONNECT_MESSAGE:
                connected = False
            conn.send("Msg received".encode(FORMAT))
    
    conn.close()
    print(f'[CONNECTION CLOSED] {addr} disconnected.')

# Start server:
def start():
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        # Wait for new connections (socket + address):
        conn, addr = server.accept()
        # When new connection occurs, handle it with new thread:
        thread = threading.Thread(target=handle_client, args=(conn,addr))
        thread.start()
        print('[SERVER] Active connections: ' + str(threading.active_count() - 1))


print('[SERVER] Server is starting...')
start()