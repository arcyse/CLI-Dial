import socket
import threading
import sys
import os
import time
import platform
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
RESET = '\033[0m'

# XOR Encryption/Decryption
def xor_encrypt_decrypt(data, key):
    key = int(key)
    if key < 0 or key > 255:
        print(f"{YELLOW}Warning: The provided XOR key {key} is out of the valid range (0-255). Adjusting to {key % 256}.{RESET}")
        key = key % 256  # Ensure key is within 0-255
    return bytearray([b ^ key for b in data])

# AES Encryption/Decryption with padding
def aes_encrypt(data, key):
    key = key.ljust(32)[:32]  # Ensure the key is 32 bytes long (256 bits)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    padded_data = pad(data, AES.block_size)
    return cipher.encrypt(padded_data)

def aes_decrypt(data, key):
    key = key.ljust(32)[:32]  # Ensure the key is 32 bytes long (256 bits)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    decrypted_data = cipher.decrypt(data)
    return unpad(decrypted_data, AES.block_size)

def get_timestamp():
    return datetime.now().strftime('%H:%M:%S')

def handle_client(client_socket, encryption_method, key, client_id, is_server, termination_flag):
    if encryption_method == 'xor':
        key = int(key)
        if key < 0 or key > 255:
            print(f"{YELLOW}Warning: The provided XOR key {key} is out of the valid range (0-255). Adjusting to {key % 256}.{RESET}")
            key = key % 256  # Ensure key is within 0-255

    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            if encryption_method == 'xor':
                message = xor_encrypt_decrypt(encrypted_message, key).decode('utf-8')
            else:
                message = aes_decrypt(encrypted_message, key).decode('utf-8')

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

def send_messages(sock, encryption_method, key, client_id, is_server):
    screen_cleared = False
    termination_flag = not is_server  # flag=True if client (initiator)

    adjustment_message_printed = False
    if encryption_method == 'xor':
        key = int(key)
        if key < 0 or key > 255:
            if not adjustment_message_printed:
                print(f"{YELLOW}Warning: The provided XOR key {key} is out of the valid range (0-255). Adjusting to {key % 256}.{RESET}")
                adjustment_message_printed = True
            key = key % 256  # Ensure key is within 0-255

    while True:
        try:
            if not screen_cleared:
                time.sleep(2)  # Delay for 2 seconds before clearing the screen
                clear_screen()
                print(f"{YELLOW}The chat is now {GREEN}Live!{RESET}")
                screen_cleared = True

            message = input().strip()

            if message.lower() == 'exit':
                confirm = input(f"{YELLOW}Are you sure you want to end the chat? ({PURPLE}yes{RESET}{YELLOW}/{RESET}{PURPLE}no{RESET}{YELLOW}):{RESET}").strip().lower()
                if confirm == 'yes':
                    clear_screen()
                    print(f"{GREEN}Exiting...{RESET}")
                    encrypted_message = 'close'.encode('utf-8')
                    encrypted_message = xor_encrypt_decrypt(encrypted_message, key) if encryption_method == 'xor' else aes_encrypt(encrypted_message, key)
                    sock.send(encrypted_message)
                    sock.close()
                    sys.exit(0)
                else:
                    print(f"{YELLOW}Continuing chat...{RESET}")
                    continue

            elif message.lower() == 'close':
                confirm = input(f"{YELLOW}Are you sure you want to end the chat? ({PURPLE}yes{RESET}{YELLOW}/{RESET}{PURPLE}no{RESET}{YELLOW}):{RESET}").strip().lower()
                if confirm == 'yes':
                    clear_screen()
                    print(f"{GREEN}Exiting...{RESET}")
                    encrypted_message = 'close'.encode('utf-8')
                    encrypted_message = xor_encrypt_decrypt(encrypted_message, key) if encryption_method == 'xor' else aes_encrypt(encrypted_message, key)
                    sock.send(encrypted_message)
                    sock.close()
                    sys.exit(0)
                else:
                    print(f"{YELLOW}Continuing chat...{RESET}")
                    continue

            encrypted_message = message.encode('utf-8')
            encrypted_message = xor_encrypt_decrypt(encrypted_message, key) if encryption_method == 'xor' else aes_encrypt(encrypted_message, key)
            sys.stdout.write('\033[F')  # Move cursor up one line
            print(f"{GREEN}[{get_timestamp()}] You:{RESET} {message}")

            sock.send(encrypted_message)
        except KeyboardInterrupt:
            clear_screen()
            print(f"{YELLOW}Interrupted. Exiting...{RESET}")
            encrypted_message = 'close'.encode('utf-8')
            encrypted_message = xor_encrypt_decrypt(encrypted_message, key) if encryption_method == 'xor' else aes_encrypt(encrypted_message, key)
            sock.send(encrypted_message)
            sock.close()
            sys.exit(0)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    clear_screen()
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Server listening on IP {ip_address} and port 9999...")

    try:
        client_socket, addr = server.accept()
        client_id = addr[0]  # Get client IP address
        print(f"Accepted connection from {addr}")

        encryption_method = input(f"{YELLOW}Choose encryption method (xor/aes): {RESET}").strip().lower()
        key = input(f"{YELLOW}Enter key: {RESET}")

        time.sleep(2)
        print(f"{YELLOW}The chat is now {GREEN}Live!{RESET}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket, encryption_method, key, client_id, True, False))
        client_handler.start()

        send_messages(client_socket, encryption_method, key, client_id, True)
    except KeyboardInterrupt:
        clear_screen()
        print(f"{RED}Server interrupted. Exiting...{RESET}")
    finally:
        server.close()

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = input(f"{YELLOW}Enter server IP address: {RESET}")
    client.connect((ip, 9999))  # Connect to server IP

    client_id = 'Client'  # placeholder identifier for the client

    encryption_method = input(f"{YELLOW}Choose encryption method (xor/aes): {RESET}").strip().lower()
    key = input(f"{YELLOW}Enter key: {RESET}")

    receive_thread = threading.Thread(target=handle_client, args=(client, encryption_method, key, client_id, False, True))
    receive_thread.daemon = True
    receive_thread.start()

    try:
        send_messages(client, encryption_method, key, client_id, False)
    except KeyboardInterrupt:
        clear_screen()
        print(f"{RED}Client interrupted. Exiting...{RESET}")
    finally:
        client.close()

if __name__ == "__main__":
    mode = input(f"{YELLOW}Enter 's' to start as server or 'c' to connect as client: {RESET}").strip().lower()
    if mode == 's':
        start_server()
    elif mode == 'c':
        connect_to_server()
    else:
        print(f"{YELLOW}Invalid option. Exiting...{RESET}")
