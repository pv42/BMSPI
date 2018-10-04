import time
import smtplib
import json
from os.path import isfile

from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from MCP3008 import MCP3008
from server import WebServer

FILE_TO_WRITE = "data.cvs"
INTERVAL = 10  # seconds
MAX_DATA = 2


class BatteryManagementSystem:

    def read_data(self):
        adc = MCP3008()
        value = {}
        for num in range(0, 8):
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
        file.write("TIME;DATA0;DATA1;DATA2;DATA3;DATA4;DATA5;DATA6;DATA7;")
        file.close()

    def send_mail(self):
        msg = MIMEMultipart()
        msg['FROM'] = self.get_email_credentials()["sender"]
        msg['TO'] = self.get_email_credentials()["receiver"]
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
            smtps_connection = smtplib.SMTP_SSL(self.get_email_credentials()["server"])
            print(self.get_email_credentials()["username"], self.get_email_credentials()["password"])
            smtps_connection.set_debuglevel(True)
            smtps_connection.login(self.get_email_credentials()["username"], self.get_email_credentials()["password"])
            # smtps_connection.sendmail(self.get_email_credentials()["sender"],
            #                          [self.get_email_credentials()["receiver"]], msg.as_string())
            smtps_connection.quit()
            print("Mail send")
        except Exception as ex:
            print(ex)
            print("Error sending mail")
            exit()

    def __init__(self):
        self.configuration = Configuration()
        self.last_data = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.current_count = 0
        self.write_head()

    def get_email_credentials(self):
        return self.configuration.email_configuration.credentials

    def loop(self):
        current_time = datetime.now()
        data = self.read_data()
        self.write_data(data, current_time)
        if self.current_count >= MAX_DATA:
            self.send_mail()
            self.write_head()
            print("Reset")
        time.sleep(INTERVAL)


class Configuration:
    def __init__(self):
        self.email_configuration = EmailConfiguration()


class EmailConfiguration:
    def __init__(self):
        if not isfile("email_credentials.json"):
            fp = open("email_credentials.json", "w")
            self.credentials["sender"] = "sender@server.cc"
            self.credentials["server"] = "smtp.server.cc"
            self.credentials["password"] = "hunter2"
            self.credentials["username"] = "username"
            self.credentials["receiver"] = "receiver@server2.cc"
            json.dump(self.credentials, fp)
            fp.close()
            print("Please enter the credentials in the email_credentials.json file")
        else:
            self.credentials = json.load(open("email_credentials.json", "r"))


bms = BatteryManagementSystem()
server = WebServer()
server.start()
while True:
    bms.loop()
