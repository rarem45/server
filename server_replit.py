import socket
import threading

SERVER_IP = "0.0.0.0"
PORT = 12345
clients = []

def handle_client(sock, addr):
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            msg = data.decode()
            print(f"{addr[0]}:{addr[1]} -> {msg}")
    except:
        pass
    finally:
        sock.close()
        clients.remove((sock, addr))
        print(f"{addr[0]}:{addr[1]} disconnected")

def accept_clients():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_IP, PORT))
    s.listen(5)
    print(f"Server listening on {SERVER_IP}:{PORT}")
    while True:
        client_socket, addr = s.accept()
        print(f"Client connected: {addr[0]}:{addr[1]}")
        clients.append((client_socket, addr))
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    accept_clients()