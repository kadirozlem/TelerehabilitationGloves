from dataclasses import dataclass


@dataclass(frozen=True)
class Microcontroller:
    port = "COM14"
    UserArduinoForCap = True
    baudrate = 115200



@dataclass(frozen=True)
class MPR121:
    Base_Capacitance = 0
    Config1 = 0x10  # 0x10
    Config2 = 0x64  # 0x64


@dataclass(frozen=True)
class FileOperation:
    WritePeriod = 5
    FileDirectory = "./testresult/"
    TestName = "TestSubject12"


@dataclass(frozen=True)
class Operations:
    SerialPort = False
    WriteFile = False
    Visualization = False
    Cloud = False
    IMU = False


@dataclass(frozen=True)
class Visualization:
    Ip = '127.0.0.1'
    Port = '25368'

@dataclass(frozen=True)
class Window:
    refresh_count = 5
    columncount = 5
    width = 1200
    height = 510
    padding = 20
    small_padding = 8
    info_box_height = 80
    info_box_label_height = 25
    button_width = 220
    four_button_width = 279
    button_height = 30
    btn_padding = 15
    button_font = ('Lucida Grande', 13, 'bold')
