import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import time

SERVER = "192.168.1.100"
PORT = 5200
HEADER = 64
FORMAT = "utf-8"
NICKNAME_REQUEST = "!NICKNAME"
DISCONNECT_MESSAGE = "!DISCONNECT"
CHANGE_CHANNEL = "!CHANNEL"
PRIVATE_MESSAGE = "!PRIVATE"
ONLINE_MESSAGE = "!ONLINE"

class Client:
    def __init__(self, ip, port):
        ask_nickname = tkinter.Tk()
        ask_nickname.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=ask_nickname)

        self.gui_done = False
        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()
        time.sleep(0.1)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((ip, port))
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def gui_loop(self):
        self.root = tkinter.Tk()
        self.root.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.root, text="Chat", bg="lightgray")
        self.chat_label.config(font=("Arial", 14))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.root)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.root, text="Message", bg="lightgray")
        self.msg_label.config(font=("Arial", 14))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.root, height=5)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.root, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.disconnect_button = tkinter.Button(self.root, text="Disconnect", command=self.stop)
        self.disconnect_button.config(font=("Arial", 12))
        self.disconnect_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.root.mainloop()

    def write(self):
        msg = self.input_area.get('1.0', 'end')
        if (msg[:4] == "/go "):
            self.send_msg(CHANGE_CHANNEL + msg[4:])
        elif (msg[:7] == "/online"):
            self.send_msg(ONLINE_MESSAGE)
        elif (msg[:6] == "/tell "):
            self.send_msg(PRIVATE_MESSAGE + " " + msg[6:])
        else:
            self.send_msg(msg)
        self.input_area.delete("1.0", "end")

    def stop(self):
        self.send_msg(DISCONNECT_MESSAGE)
        self.root.quit()

    def send_msg(self, msg):
        msg = msg.encode(FORMAT)
        msg_length = len(msg)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b" " * (HEADER - len(send_length))
        self.server.send(send_length)
        self.server.send(msg)

    def receive(self):
        while True:
            try:
                msg_length = self.server.recv(HEADER).decode(FORMAT)
                msg = self.server.recv(int(msg_length)).decode(FORMAT)
                if (msg == NICKNAME_REQUEST):
                    self.send_msg(self.nickname)
                elif (msg == DISCONNECT_MESSAGE):
                    print("Disconnecting")
                    self.server.close()
                    break
                else:
                    if self.gui_done:
                        print(msg, end="")
                        self.text_area.config(state="normal")
                        self.text_area.insert("end", msg)
                        self.text_area.yview("end")
                        self.text_area.config(state="disabled")
            except Exception as e:
                print(e)
                self.root.quit()
                break

client = Client(SERVER, PORT)