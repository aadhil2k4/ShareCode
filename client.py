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

    # Ask for the access type (readonly/edit)
    access_type = input("Enter your access type (readonly/edit): ")
    client_socket.send(access_type.encode('utf-8'))

    if access_type == "readonly":
        print("You have readonly access. You cannot edit.")
        while True:
            # Just block the terminal to prevent any typing in readonly mode
            pass  # Do nothing, prevent input capture
    else:
        print("You have edit access. Start typing:")

        # Capture each character and send it to the server (only if edit access)
        while True:
            char = get_single_character()  # Capture one character at a time

            if char == '\x7f':  # Handle backspace
                client_socket.send(char.encode('utf-8'))  # Send backspace character
            else:
                client_socket.send(char.encode('utf-8'))  # Send each character immediately

if __name__ == "__main__":
    start_client()
