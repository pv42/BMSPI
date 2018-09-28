import datetime
import time

from MCP3008 import MCP3008

FILE_TO_WRITE = "data.cvs"


def read_data():
    adc = MCP3008()
    value = {}
    for num in range(0, 7):
        value[num] = adc.read(num) / 1023.0 * 3.3
        print("Anliegende Spannung: %.2f" % value[num])
    return value


def write_data(data, time):
    file = open(FILE_TO_WRITE, "a")
    data_string = ""
    for d in data:
        data_string = data_string + d + ";"
    file.write(time + ";" + data + "\n")
    file.close()


def write_head():
    file = open(FILE_TO_WRITE, "w")
    file.write("TIME;DATA0;DATA1;DATA2;DATA3;DATA4;DATA5;DATA6;DATA7;")
    file.close()


def main():
    write_head()
    while True:
        ctime = datetime.datetime.now()
        data = read_data()
        write_data(ctime, data)
        time.sleep(10)