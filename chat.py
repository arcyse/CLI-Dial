#pip install cryptography
#pip install cryptodome
#pip install pycrytpo


import socket
import threading
import sys
import os
import platform
from datetime import datetime

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
RESET = '\033[0m'

# XOR Encryption/Decryption
def xor_encrypt_decrypt(data, key):
    return bytearray([b ^ key for b in data])

def get_timestamp():
    return datetime.now().strftime('%H:%M:%S')

def handle_client(client_socket, key, client_id, is_server, termination_flag):
    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            message = xor_encrypt_decrypt(encrypted_message, key).decode('utf-8')
            if message == 'close':
                if is_server:
                    print(f"\n{YELLOW}Remote has closed the connection. You may end the chat by{RESET} {PURPLE}exit{RESET}")
                else:
                    if termination_flag:
                        print(f"\n{YELLOW}You ended the connection.{RESET}")
                break
            else:
                print(f"\n{RED}[{get_timestamp()}] Remote:{RESET} {message}")
        except ConnectionResetError:
            break

    client_socket.close()

def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def send_messages(sock, key, client_id, is_server):
    screen_cleared = False
    termination_flag = not is_server  # flag=True if client (initiator)

    while True:
        try:
            if not screen_cleared:
                clear_screen()
                print(f"{YELLOW}The chat is now {GREEN}Live!{RESET}")
                screen_cleared = True

            message = input().strip()
            
            if message.lower() == 'exit':
                confirm = input(f"{YELLOW}Are you sure you want to end the chat? ({PURPLE}yes{RESET}/{PURPLE}no{RESET}): {RESET}").strip().lower()
                if confirm == 'yes':
                    clear_screen()
                    print(f"{GREEN}Exiting...{RESET}")
                    sock.send(xor_encrypt_decrypt('close'.encode('utf-8'), key))
                    sock.close()
                    sys.exit(0)
                else:
                    print(f"{YELLOW}Continuing chat...{RESET}")
                    continue

            elif message.lower() == 'close':
                confirm = input(f"{YELLOW}Are you sure you want to close the chat? ({PURPLE}yes{RESET}/{PURPLE}no{RESET}): {RESET}").strip().lower()
                if confirm == 'yes':
                    clear_screen()
                    print(f"{GREEN}Exiting...{RESET}")
                    sock.send(xor_encrypt_decrypt('close'.encode('utf-8'), key))
                    sock.close()
                    sys.exit(0)
                else:
                    print(f"{YELLOW}Continuing chat...{RESET}")
                    continue

            encrypted_message = xor_encrypt_decrypt(message.encode('utf-8'), key)
            sys.stdout.write('\033[F')  # Move cursor up one line
            print(f"{GREEN}[{get_timestamp()}] You:{RESET} {message}")

            sock.send(encrypted_message)
        except KeyboardInterrupt:
            clear_screen()
            print(f"{YELLOW}Interrupted. Exiting...{RESET}")
            sock.send(xor_encrypt_decrypt('close'.encode('utf-8'), key))
            sock.close()
            sys.exit(0)

def start_server(key):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    clear_screen()
    print("Server listening on port 9999...")

    try:
        client_socket, addr = server.accept()
        client_id = addr[0]  # Get client IP address
        print(f"Accepted connection from {addr}")

        print(f"{YELLOW}The chat is now {GREEN}Live!{RESET}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket, key, client_id, True, False))
        client_handler.start()

        send_messages(client_socket, key, client_id, True)
    except KeyboardInterrupt:
        clear_screen()
        print(f"{RED}Server interrupted. Exiting...{RESET}")
    finally:
        server.close()

def connect_to_server(key):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9999))  # server IP here else localhost 

    client_id = 'Client'  # placeholder identifier for the client
    receive_thread = threading.Thread(target=handle_client, args=(client, key, client_id, False, True))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        send_messages(client, key, client_id, False)
    except KeyboardInterrupt:
        clear_screen()
        print(f"{RED}Client interrupted. Exiting...{RESET}")
    finally:
        client.close()

if __name__ == "__main__":
    key = 123 # Sample key for XOR encryption 0-255
    mode = input("Enter 's' to start as server or 'c' to connect as client: ").strip().lower()
    if mode == 's':
        start_server(key)
    elif mode == 'c':
        connect_to_server(key)
    else:
        print("Invalid option. Exiting...")
