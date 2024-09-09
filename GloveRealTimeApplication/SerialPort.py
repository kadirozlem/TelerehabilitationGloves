import time

import serial
from threading import Thread
import serial.tools.list_ports
from tkinter import *

import Configuration

def now():
    return time.time()

class SerialPort:
    def __init__(self, ReadValue, Port=Configuration.Microcontroller.port,Baudrate=Configuration.Microcontroller.baudrate, Error=None):
        try:
            self.ser = ReadLine(serial.Serial(Port, Baudrate, timeout=None))
        except IOError as a:
            print("Program stopped because of Serial Port Error")
            self.run = False
            raise Exception("Serial Port Error")
        self.port = Port
        self.ReadValue = ReadValue
        self.error_count = 0
        self.data_count = 0
        self.error = self.error_func if Error == None else Error
        self.run = True
        self.thread = Thread(target=self.ReadSerial)
        self.thread.start()

    def error_func(self, val):
        self.error_count += 1
        if self.error_count % 10 == 0:
            print("Error count: " + str(self.error_count))
            print(self.port)

    def ReadSerial(self):
        while self.run:
            try:
                timestamp = now()
                val = self.ser.readline().decode('utf-8').strip()
                if val != '':
                    #print(val)
                    #if val[0] == "!" and val[-1] == "#":
                    self.data_count+=1
                    self.ReadValue(timestamp,val[1:-1])
                    #else:
                    #    self.error_func(val)

            except IOError as a:
                print("Program stopped because of Serial Port Error")
                self.run = False
            except Exception as a:
                self.error_func("Char error")

        self.ser.s.close()

    def Write(self,message):
        self.ser.s.write(message.encode('utf-8'))

    @staticmethod
    def GetPorts():
        arrPorts = []
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            arrPorts.append(port)
        return arrPorts

    def __del__(self):
        if self.run:
            self.ser.s.close()
        self.run = False
        del self

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]
                return r
            else:
                self.buf.extend(data)
