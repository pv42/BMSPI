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

FILE_TO_WRITE = "data.cvs"
INTERVAL = 10  # seconds
MAX_DATA = 100

if not isfile("credentials.json"):
    credentials = {}
    fp = open("credentials.json", "w")
    credentials["sender"] = "sender@server.cc"
    credentials["server"] = "smtp.server.cc"
    credentials["password"] = "hunter2"
    credentials["username"] = "username"
    credentials["receiver"] = "receiver@server2.cc"
    json.dump(credentials, fp)
    print("Please enter the credentials in the credentials.json file")
else:
    credentials = json.load(open("credentials.json", "r"))
last_data = [-1, -1, -1, -1, -1, -1, -1, -1]
current_count = 0


def read_data():
    global current_count, last_data
    adc = MCP3008()
    value = {}
    for num in range(0, 8):
        value[num] = adc.read(num) / 1023.0 * 3.3
        print("Voltage %d (set %d): %.2f" % (num, current_count, value[num]))
    last_data = value
    current_count = current_count + 1
    return value


def write_data(data, current_time):
    file = open(FILE_TO_WRITE, "a")
    data_string = ""
    for d in data:
        data_string = data_string + str(d) + ";"
    file.write(current_time.strftime("%d.%m.%Y %H:%M:%S") + ";" + data_string + "\n")
    file.close()


def write_head():
    file = open(FILE_TO_WRITE, "w")
    file.write("TIME;DATA0;DATA1;DATA2;DATA3;DATA4;DATA5;DATA6;DATA7;")
    file.close()


def send_mail():
    global credentials
    msg = MIMEMultipart()
    msg['FROM'] = credentials["sender"]
    msg['TO'] = credentials["receiver"]
    msg['Date'] = formatdate(localtime=True)
    msg['SUBJECT'] = "BMS PI"
    file = open(FILE_TO_WRITE, "rb")
    msg.attach(MIMEText("Hello pv42,\n this is the automated BMS report.\nThe last data set was {}".format(last_data)))
    part = MIMEApplication(file.read(), Name="data.cvs")
    file.close()
    part['Content-Disposition'] = 'attachment; filename="%s"' % "data.cvs"
    msg.attach(part)

    try:
        smtps = smtplib.SMTP_SSL(credentials["server"])
        smtps.set_debuglevel(True)
        smtps.login(credentials["username"], credentials["password"])
        smtps.sendmail(credentials["sender"], [credentials["receiver"]], msg.as_string())
        smtps.quit()
        print("Mail send")
    except Exception as ex:
        print(ex)
        print("Error sending mail")
        exit()


def main():
    write_head()
    while True:
        ctime = datetime.now()
        data = read_data()
        write_data(data, ctime)
        if current_count >= MAX_DATA:
            send_mail()
            write_head()
            print("Reset")
        time.sleep(INTERVAL)


main()
