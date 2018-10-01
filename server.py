from threading import Thread
import socket

OWN_IP = "127.0.0.1"
OWN_PORT = 80
BUFFER_SIZE = 2048

passwords = {"admin": "toor"}


def read_file(name):
    fh = open("www/" + name, "rb")
    return fh.read()


def http_200(length):
    return b"HTTP/1.1 200 OK\r\n" + \
           b"Content-Type:text/html; charset=utf-8\r\n" + \
           b"Cache-Control: no-store, no-cache\r\n" + \
           b"Pragma: no-cache\r\n" + \
           bytes("Content-Length:{}\r\n".format(length), "utf-8") + \
           b"\r\n"


class WebServer(Thread):

    def __init__(self):
        super().__init__()
        self.connection = None

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((OWN_IP, OWN_PORT))
        server_socket.listen(1)
        self.connection, address = server_socket.accept()
        print("Connection from " + str(address))
        while True:
            data = self.connection.recv(BUFFER_SIZE).decode("utf-8")
            print(data)
            if not data: continue
            lines = data.split("\n")
            line0 = lines[0].split()
            if len(line0) != 3:
                print("invalid request")
                continue

            print("HTTP:" + str(line0))
            if line0[0] == "GET":
                if line0[1] == "/":
                    self.send_file("login.html")
            elif line0[0] == "POST":
                if line0[1] == "/":
                    chunks = data.split("\r\n\r\n")
                    if len(chunks) < 2:
                        continue
                    post_data = chunks[1]
                    pwd = ""
                    user = ""
                    for att in post_data.split("&"):
                        [k, v] = att.split("=")
                        print("k,v = ", k, ",", "v")
                        if k == "password":
                            pwd = v
                        elif k == "username":
                            user = v
                    if user in passwords and passwords[user] == pwd:
                        self.send_file("main.html")
                    else:
                        self.send_file("login_wrong.html")

            else:
                print("unknown request")

    def send_file(self, name):
        data = read_file(name)
        self.send_http(data)

    def send_http(self, data):
        self.connection.send(http_200(len(data)) + data)
        print((http_200(len(data)) + data).decode("utf-8"))
