import socket
import threading

IP = socket.gethostbyname(socket.gethostname()) #192.168.1.100
PORT = 5200
HEADER = 64
FORMAT = "utf-8"
NICKNAME_REQUEST = "!NICKNAME"
DISCONNECT_MESSAGE = "!DISCONNECT"
CHANGE_CHANNEL = "!CHANNEL"
PRIVATE_MESSAGE = "!PRIVATE"
ONLINE_MESSAGE = "!ONLINE"

def send_msg(msg, client):
    msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg)

def broadcast(msg, channel, nickname):
    for key, value in clients.items():
        if ((channel == "broadcast" or channel == value[2]) and key != nickname):
            send_msg(msg, value[0])

def handle_client(client, address):
    send_msg(NICKNAME_REQUEST, client)
    nickname_length = client.recv(HEADER).decode(FORMAT)
    nickname = client.recv(int(nickname_length)).decode(FORMAT)
    print(f"{nickname} connected from {address}")
    broadcast(f"{nickname} connected to the server\n", "broadcast", nickname)
    send_msg("Connected to the server\n", client)
    clients[nickname] = [client, address, channels[0]]
    print(f"{nickname} joined the lobby")
    broadcast(f"{nickname} joined the lobby\n", "lobby", nickname)
    while True:
        try:
            msg_length = client.recv(HEADER).decode(FORMAT)
            msg = client.recv(int(msg_length)).decode(FORMAT)
            if (msg == DISCONNECT_MESSAGE):
                print(f"{nickname} left the {clients[nickname][2]}")
                broadcast(f"{nickname} left the {clients[nickname][2]}\n", clients[nickname][2], nickname)
                send_msg(DISCONNECT_MESSAGE, client)
                print(f"{nickname} disconnected")
                broadcast(f"{nickname} disconnected\n", "broadcast", nickname)
                del clients[nickname]
                break
            elif (msg[:len(CHANGE_CHANNEL)] == CHANGE_CHANNEL):
                if (msg[len(CHANGE_CHANNEL):-1] in channels):
                    print(f"{nickname} left the {clients[nickname][2]}")
                    send_msg(f"You left the {clients[nickname][2]}\n", client)
                    broadcast(f"{nickname} left the {clients[nickname][2]}\n", clients[nickname][2], nickname)
                    clients[nickname][2] = msg[len(CHANGE_CHANNEL):-1]
                    print(f"{nickname} joined the {clients[nickname][2]}")
                    send_msg(f"You joined the {clients[nickname][2]}\n", client)
                    broadcast(f"{nickname} joined the {clients[nickname][2]}\n", clients[nickname][2], nickname)
                else:
                    send_msg("This channel does not exist\n", client)
                continue
            elif (msg[:len(PRIVATE_MESSAGE)] == PRIVATE_MESSAGE):
                if (msg.split(' ')[1] in clients.keys()):
                    print(f"<{nickname}> to <{msg.split(' ')[1]}> {msg[len(PRIVATE_MESSAGE) + 1 + len(msg.split(' ')[1]) + 1:-1]}")
                    send_msg(f"<<{nickname}>> {msg[len(PRIVATE_MESSAGE) + 1 + len(msg.split(' ')[1]) + 1:]}", clients[msg.split(' ')[1]][0])
                    send_msg(f"to <<{msg.split(' ')[1]}>> {msg[len(PRIVATE_MESSAGE) + 1 + len(msg.split(' ')[1]) + 1:]}", client)
                else:
                    send_msg("This person is not online\n", client)
                continue
            elif (msg == ONLINE_MESSAGE):
                online_clients = ""
                for key in clients:
                    online_clients += key + ", "
                online_clients = online_clients[:-2] + "\n"
                send_msg(online_clients, client)
                continue
            broadcast(f"<{nickname}> {msg}", clients[nickname][2], "")
            print(f"<{nickname}> {msg}", end="")
        except Exception as e:
            print(e)
            del clients[nickname]
            client.close()
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
print("server is starting")
server.listen()
clients = {}
channels = ["lobby", "first channel", "second channel", "afk"]

while True:
    client, address = server.accept()
    thread = threading.Thread(target=handle_client, args=(client, address))
    thread.start()
    print(f"{threading.activeCount() - 1} active connections")