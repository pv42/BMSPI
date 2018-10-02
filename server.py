from threading import Thread
import socket
import site_creator

OWN_IP = "127.0.0.1"
OWN_PORT = 80
BUFFER_SIZE = 2048

passwords = {"admin": "toor"}


def read_file(name):
    fh = open("www/" + name, "rb")
    return fh.read()


def http_head(code, length):
    if code == 200:
        return b"HTTP/1.1 200 OK\r\n" + \
               b"Content-Type:text/html; charset=utf-8\r\n" + \
               b"Cache-Control: no-store, no-cache\r\n" + \
               b"Pragma: no-cache\r\n" + \
               bytes("Content-Length:{}\r\n".format(length), "utf-8") + \
               b"\r\n"
    elif code == 404:
        return b"HTTP/1.1 404 Not Found\r\n" + \
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
                    self.send_http(site_creator.create_login(False))
                else:
                    self.send_http(site_creator.create404(), 404)
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
                        self.send_http(site_creator.create_main([0, 0, 0, 0, 0, 0, 0, 0], None))
                    else:
                        self.send_http(site_creator.create_login(True))
            else:
                print("unknown request")

    def send_http(self, data, status_code=200):
        self.connection.send(http_head(status_code, len(data)) + bytes(data, "utf-8"))
        print((http_head(status_code, len(data)) + bytes(data, "utf-8")).decode("utf-8"))
