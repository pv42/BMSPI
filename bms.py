import datetime
import time
import smtplib

from MCP3008 import MCP3008

FILE_TO_WRITE = "data.cvs"
INTERVAL = 10


def read_data():
    adc = MCP3008()
    value = {}
    for num in range(0, 8):
        value[num] = adc.read(num) / 1023.0 * 3.3
        print("Voltage %d: %.2f" % (num ,value[num]))
    return value


def write_data(data, time):
    file = open(FILE_TO_WRITE, "a")
    data_string = ""
    for d in data:
        data_string = data_string + str(d) + ";"
    file.write(time.strftime("%d.%m.%Y %H:%M:%S") + ";" + data_string + "\n")
    file.close()


def write_head():
    file = open(FILE_TO_WRITE, "w")
    file.write("TIME;DATA0;DATA1;DATA2;DATA3;DATA4;DATA5;DATA6;DATA7;")
    file.close()

def send_mail():
    try:
        smtp = smtplib.SMTP('gmail.com')
        msg = """From: Riot <riot.games.de.lol@gmail.com>
To: pv42 <pv42.97@gmail.com>
Subject: testbms

this is a text email
"""
        smtp.sendmail("riot.games.de.lol@gmail.com", ["pv42.97@gmail.com"],msg)
        print("Mail send")
    except Exeception:
        print(ex) 
        print("Error sending mail")

def main():
    write_head()
    send_mail();
    while True:
        ctime = datetime.datetime.now()
        data = read_data()
        write_data(data, ctime)
        time.sleep(INTERVAL)

main()
