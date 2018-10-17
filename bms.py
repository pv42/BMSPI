import os
import time
import smtplib
import json
from os.path import isfile

from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from threading import Thread

from MCP3008 import MCP3008
from server import WebServer

VERSION = "0.01.133"

FILE_TO_WRITE = "current_data.cvs"
CONFIG_FILENAME = "config/bms_config.json"


class BatteryManagementSystem(Thread):

    def __init__(self):
        super().__init__()
        self.version = VERSION
        self.configuration = Configuration()
        self.last_data = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.current_count = 0
        self.write_head()
        self.should_run = True
        self.is_running = False

    def read_data(self):
        adc = MCP3008()
        value = [0] * self.configuration.data_reading["number_of_channels"]
        for num in range(0, self.configuration.data_reading["number_of_channels"]):
            value[num] = adc.read(num) / 1023.0 * 3.3
            print("Voltage %d (set %d): %.2f" % (num, self.current_count, value[num]))
        adc.close()
        self.last_data = value
        self.current_count = self.current_count + 1
        return value

    @staticmethod
    def write_data(data, current_time):
        file = open(FILE_TO_WRITE, "a")
        data_string = ""
        for d in data:
            data_string = data_string + str(d) + ";"
        file.write(current_time.strftime("%d.%m.%Y %H:%M:%S") + ";" + data_string + "\n")
        file.close()

    @staticmethod
    def write_head():
        file = open(FILE_TO_WRITE, "w")
        file.write("TIME;DATA0;DATA1;DATA2;DATA3;DATA4;DATA5;DATA6;DATA7;\n")
        file.close()

    def send_mail(self):
        msg = MIMEMultipart()
        msg['FROM'] = self.configuration.email["sender"]
        msg['TO'] = self.configuration.email["receiver"]
        msg['Date'] = formatdate(localtime=True)
        msg['SUBJECT'] = "BMS PI"
        file = open(FILE_TO_WRITE, "rb")
        msg.attach(MIMEText(
            "Hello pv42,\n this is the automated BMS report.\nThe last data set was {}".format(self.last_data)
        ))
        part = MIMEApplication(file.read(), Name="data.cvs")
        file.close()
        part['Content-Disposition'] = 'attachment; filename="%s"' % "data.cvs"
        msg.attach(part)

        try:
            smtps_connection = smtplib.SMTP_SSL(self.configuration.email["server"])
            print(self.get_email_credentials()["username"], self.get_email_credentials()["password"])
            smtps_connection.set_debuglevel(True)
            smtps_connection.login(self.get_email_credentials()["username"], self.get_email_credentials()["password"])
            # smtps_connection.sendmail(self.get_email_credentials()["sender"],
            #                          [self.get_email_credentials()["receiver"]], msg.as_string())
            smtps_connection.quit()
            print("Mail send")
        except Exception as ex:
            print()
            print("Error sending mail (ex:{})".format(ex))
            exit()

    def run(self):
        while True:
            if self.should_run:
                self.is_running = True
                while self.should_run:
                    self.loop()
                self.is_running = False
                self.on_stop()
            time.sleep(1)

    def loop(self):
        current_time = datetime.now()
        data = self.read_data()
        self.write_data(data, current_time)
        if self.current_count >= self.configuration.data_reading["dates_per_file"]:
            if self.configuration.email["enabled"]:
                self.send_mail()
            self.write_head()
            print("Reset")
        for i in range(self.configuration.data_reading["measure_timeout"]):
            if not self.should_run:
                return
            time.sleep(1)

    def get_email_credentials(self):
        return self.configuration.email["credentials"]

    def on_stop(self):
        if self.configuration.email["enabled"]:
            self.send_mail()
        os.rename(FILE_TO_WRITE, "data/" + str(datetime.now()).replace(":", "-") + ".cvs")


class Configuration:
    def load_from_file(self):
        fp = open(CONFIG_FILENAME, "r")
        data = json.load(fp)
        self.web_credentials = data["web_credentials"]
        self.data_reading = data["data_reading"]
        self.email = data["email"]
        fp.close()

    def save_to_file(self):
        fp = open(CONFIG_FILENAME, "w")
        data = {"web_credentials": self.web_credentials,
                "data_reading": self.data_reading,
                "email": self.email}
        json.dump(data, fp)
        fp.close()

    def __init__(self):
        self.web_credentials = None
        self.data_reading = None
        self.email = None
        if not isfile(CONFIG_FILENAME):
            print("Creating config file \"" + CONFIG_FILENAME + "\" ...")
            self.web_credentials = {
                "username": "admin",
                "password": "toor"
            }
            self.data_reading = {
                "number_of_channels": 8,
                "measure_timeout": 10,
                "dates_per_file": 360
            }
            self.email = {
                "enabled": False,
                "sender": "exsender@gmail.com",
                "receiver": "exreceiver@gmail.com",
                "server": "smtp.gmail.com:465",
                "credentials": {
                    "username": "",
                    "password": ""
                }
            }
            self.save_to_file()
        else:
            self.load_from_file()


bms = BatteryManagementSystem()
server = WebServer(bms)

bms.start()
server.start()
