import socket
import threading
import sys
import termios
import tty

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                print(message.decode('utf-8'), end='', flush=True)  # Print received characters in real-time
        except:
            print("Connection lost")
            client_socket.close()
            break

def get_single_character():
    # Capture a single character without waiting for Enter
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))  # Change 'localhost' to server IP if needed

    # Start a thread to receive messages from the server
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    print("Connected to the server. Start typing:")

    # Capture each character and send it to the server
    while True:
        char = get_single_character()  # Capture one character at a time
        client_socket.send(char.encode('utf-8'))  # Send each character immediately

if __name__ == "__main__":
    start_client()
