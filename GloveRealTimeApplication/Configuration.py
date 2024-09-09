from dataclasses import dataclass
import platform

@dataclass(frozen=True)
class Microcontroller:
    port = "/dev/tty.usbmodem11101"
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
    SerialPort = True
    WriteFile = False
    Visualization = False
    Cloud = True
    Patient = False
    IMU = False
    CalibrationTime = 2
    PredictTime = 12
    Actuate = 15


@dataclass(frozen=True)
class Visualization:
    Ip = '127.0.0.1'
    Port = '25368'

if platform.system() == "Darwin":
    @dataclass(frozen=True)
    class Window:
        refresh_count = 5
        columncount = 5
        width = 1200
        height = 380
        padding = 20
        small_padding = 8
        info_box_height = 80
        info_box_label_height = 25
        button_width = 215
        button_height = 30
        btn_padding = 20
        option_width = 20
        option_height = 2
else:
    @dataclass(frozen=True)
    class Window:
        refresh_count = 5
        columncount = 5
        width = 1200
        height = 380
        padding = 20
        small_padding = 8
        info_box_height = 80
        info_box_label_height = 25
        button_width = 30
        button_height = 2
        btn_padding = 15
        option_width = 30
        option_height = 2


@dataclass(frozen=True)
class Cloud:
    ip = '164.92.168.129'
    #ip='192.168.2.125'
    worker_port = '27592'
    resource_port = '17796'
    is_secure = False
    token = "pkQmpguDVt8UISt5LeQv0TIEdM1MM3svt8WK6jOWiwmShVjkyZlQTU9FYY3WqwJL"