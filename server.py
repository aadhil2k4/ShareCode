import socket
import threading
import sys

clients = [] 
code_buffer = []  
server_running = True 

def broadcast(message, sender_socket=None):
    global code_buffer
    
    for client in clients:
        client_socket, access_type = client
        try:
            client_socket.send(''.join(code_buffer).encode('utf-8'))
        except:
            client_socket.close()
            clients.remove(client)

def handle_client(client_socket, addr, access_type):
    global code_buffer

    if access_type == "readonly":
        client_socket.send(b"You have readonly access.\n")
    else:
        client_socket.send(b"You have edit access.\n")

    client_socket.send(''.join(code_buffer).encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            if message == "^X": 
                print(f"Client {addr} disconnected with ^X.")
                client_socket.send(b"Disconnected from server.")
                client_socket.close()
                clients.remove((client_socket, access_type))
                break

            if access_type == "edit":
                for char in message:
                    if char == '\x7f':  
                        if code_buffer:  
                            code_buffer.pop() 
                    else:
                        code_buffer.append(char)
                
                broadcast(''.join(code_buffer).encode('utf-8'))

        except:
            client_socket.close()
            clients.remove((client_socket, access_type))
            break

def start_server():
    global server_running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12346)) 
    server.listen()

    print("Server started, waiting for connections...")

    def stop_server():
        global server_running
        while server_running:
            char = sys.stdin.read(1)
            if char == '\x18':  
                print("Stopping server and disconnecting all clients...")
                for client_socket, _ in clients:
                    client_socket.send(b"Server is shutting down.")
                    client_socket.close()
                server_running = False
                server.close()
                print("Server stopped.")
                break

    threading.Thread(target=stop_server).start()

    while server_running:
        try:
            client_socket, addr = server.accept()
            print(f"Connection from {addr}")

            client_socket.send(b"Enter your access type (readonly/edit): ")
            access_type = client_socket.recv(1024).decode('utf-8').strip()

            clients.append((client_socket, access_type))

            threading.Thread(target=handle_client, args=(client_socket, addr, access_type)).start()
        except:
            if not server_running:
                break

if __name__ == "__main__":
    start_server()
