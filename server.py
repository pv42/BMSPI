import urllib
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
    elif code == 403:
        return b"HTTP/1.1 403 Forbidden\r\n" + \
               b"Content-Type:text/html; charset=utf-8\r\n" + \
               b"Cache-Control: no-store, no-cache\r\n" + \
               b"Pragma: no-cache\r\n" + \
               bytes("Content-Length:{}\r\n".format(length), "utf-8") + \
               b"\r\n"


class WebServer(Thread):
    def __init__(self, bms):
        super().__init__()
        self.bms = bms
        self.connection = None

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind((OWN_IP, OWN_PORT))
            server_socket.listen(1)
        except Exception as ex:
            print("Could not start web server: failed to bind port 80")
            print("Try to run this as root and make sure you have no other webserver running")
            return
        while True:
            connection, address = server_socket.accept()
            print("Connection from " + str(address))
            WebServerConnection(connection, self.bms).start()


USER_LEVEL_NONE = 0
USER_LEVEL_READ = 1
USER_LEVEL_FULL = 2


class WebServerConnection(Thread):

    def __init__(self, connection, battery_mangement_system):
        super().__init__()
        self.connection = connection
        self.user_level = USER_LEVEL_NONE
        self.bms = battery_mangement_system

    def run(self):
        while True:
            data = self.connection.recv(BUFFER_SIZE).decode("utf-8")
            if not data:
                continue
            print(data)
            lines = data.split("\n")
            line0 = lines[0].split()
            if len(line0) != 3:
                print("invalid request")
                continue

            print("HTTP:" + str(line0))
            if line0[0] == "GET":
                if line0[1] == "/":
                    self.send_http(site_creator.create_login(False))
                elif line0[1] == "/main":
                    if self.user_level > USER_LEVEL_NONE:
                        self.send_http(site_creator.create_main(self.bms.last_data, self.bms.configuration.email,
                                                                self.bms.configuration.data_reading,
                                                                self.bms))
                    else:
                        self.send_http(site_creator.create403(), 403)
                elif line0[1] == "/email":
                    if self.user_level > USER_LEVEL_NONE:
                        self.send_http(site_creator.create_email(self.bms.configuration.email))
                    else:
                        self.send_http(site_creator.create403(), 403)
                elif line0[1] == "/stop":
                    if self.user_level > USER_LEVEL_NONE:
                        self.bms.should_run = False
                        self.send_http(site_creator.create_redirect("main"))
                    else:
                        self.send_http(site_creator.create403(), 403)
                elif line0[1] == "/start":
                    if self.user_level > USER_LEVEL_NONE:
                        self.bms.should_run = True
                        self.send_http(site_creator.create_redirect("main"))
                    else:
                        self.send_http(site_creator.create403(), 403)

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
                        self.user_level = USER_LEVEL_FULL
                        self.send_http(site_creator.create_redirect("main"))
                    else:
                        self.send_http(site_creator.create_login(True))
                elif line0[1] == "/email":
                    if self.user_level == USER_LEVEL_NONE:
                        self.send_http(site_creator.create403(), 403)
                        continue
                    chunks = data.split("\r\n\r\n")
                    if len(chunks) < 2:
                        continue
                    post_data = chunks[1]
                    post = {}
                    enabled = False
                    for att in post_data.split("&"):
                        if "=" in att:
                            [k, v] = att.split("=")
                            post[k] = v
                            if k == "enabled":
                                enabled = True
                            else:
                                self.bms.configuration.email[k] = urllib.parse.unquote(v)
                    if enabled:
                        self.bms.configuration.email["enabled"] = True
                    else:
                        self.bms.configuration.email["enabled"] = False
                    self.bms.configuration.save_to_file()
                    self.send_http(site_creator.create_email(self.bms.configuration.email))
                else:
                    self.send_http(site_creator.create404(), 404)
            else:
                print("unknown request")

    def send_http(self, data, status_code=200):
        self.connection.send(http_head(status_code, len(data)) + bytes(data, "utf-8"))
        # print((http_head(status_code, len(data)) + bytes(data, "utf-8")).decode("utf-8"))
