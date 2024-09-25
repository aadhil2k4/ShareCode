import socket
import threading
import sys
import termios
import tty
import os
import subprocess

FILENAME = 'stored_code.py'

def clear_terminal():
    os.system('clear')

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                clear_terminal()
                print(message.decode('utf-8'), end='', flush=True)
        except:
            print("Connection lost")
            client_socket.close()
            break

def get_single_character():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def store_code(code):
    with open(FILENAME, 'w') as f:
        f.write(code)
    print(f"Code stored in {FILENAME}")

def run_code():
    try:
        result = subprocess.run(['python3', FILENAME], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Output:\n", result.stdout) 
        if result.stderr:
            print("Errors:\n", result.stderr) 
    except subprocess.CalledProcessError as e:
        print(f"Error running code: {e}")

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.195.9', 12346))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    access_type = input("Enter your access type (readonly/edit): ")
    client_socket.send(access_type.encode('utf-8'))

    clear_terminal()

    if access_type == "readonly":
        print("You have readonly access. You cannot edit.")
        while True:
            pass
    else:
        print("You have edit access. Start typing:")
        current_code = []  
        while True:
            char = get_single_character()

            if char == '\x7f': 
                if current_code:
                    current_code.pop()
                client_socket.send(char.encode('utf-8'))
            elif char == '\r':  
                client_socket.send('\r\n'.encode('utf-8'))
                current_code.append('\n')
            elif char == '$':  
                command = input("$")
                if command == "run":
                    store_code(''.join(current_code)) 
                    run_code()  
            else:
                client_socket.send(char.encode('utf-8'))
                current_code.append(char)

if __name__ == "__main__":
    start_client()
