import socket
import threading

clients = []

def broadcast(message):
    # Send the message to all clients, including the sender
    for client in clients:
        try:
            client.send(message)
        except:
            client.close()
            clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                broadcast(message)  # Broadcast to all clients
        except:
            # If there's any error, remove the client
            client_socket.close()
            clients.remove(client_socket)
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))  # Bind to any IP and port 12345
    server.listen()

    print("Server started, waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
