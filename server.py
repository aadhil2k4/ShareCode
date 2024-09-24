import socket
import threading

clients = []  # Store connected clients and their access level
code_buffer = []  # Shared code document

def broadcast(message, sender_socket=None):
    # Send the message to all clients, including the sender
    for client in clients:
        client_socket, access_type = client
        try:
            client_socket.send(message)
        except:
            client_socket.close()
            clients.remove(client)

def handle_client(client_socket, addr, access_type):
    global code_buffer

    if access_type == "readonly":
        client_socket.send(b"You have readonly access.\n")
    else:
        client_socket.send(b"You have edit access.\n")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            # Handle edit access: Allow edits from 'edit' access clients
            if access_type == "edit":
                if message == '\x7f':  # Backspace ASCII code
                    if code_buffer:  # Only if there's something to delete
                        code_buffer.pop()  # Remove last character
                        broadcast(b"\b \b")  # Send backspace to all clients
                else:
                    code_buffer.append(message)
                    broadcast(message.encode('utf-8'))  # Broadcast to all clients

        except:
            # Remove client in case of an error
            client_socket.close()
            clients.remove((client_socket, access_type))
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))  # Bind to any IP and port 12345
    server.listen()

    print("Server started, waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")

        # Ask for access type (readonly or edit)
        client_socket.send(b"Enter your access type (readonly/edit): ")
        access_type = client_socket.recv(1024).decode('utf-8').strip()

        # Add the client to the clients list
        clients.append((client_socket, access_type))

        # Start a new thread to handle each client
        threading.Thread(target=handle_client, args=(client_socket, addr, access_type)).start()

if __name__ == "__main__":
    start_server()
