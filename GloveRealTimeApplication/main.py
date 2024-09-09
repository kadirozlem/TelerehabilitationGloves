#
import random
import threading
import tkinter
import tkinter.messagebox
import platform
from tkinter import *
import tkinter.font as font

import Configuration
# import SerialPort
import datetime
import logging
import os
import time
from threading import Thread, Timer, Event
from dataclasses import dataclass
import socketio

import SerialPort

if platform.system() == "Darwin":
    from tkmacosx import Button

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Labels:
    Opening = "0"
    Opened = "1"
    Closing = "2"
    Closed = "3"
    Calibration = "9"


@dataclass
class LabelColors:
    Opening = "yellow"
    Opened = "green2"
    Closing = "orange"
    Closed = "red2"
    Calibration = 9


TestOptions = [
    "LR",
    "DT",
    "kNN",
    "MLP",
    "RF",
    "XGB"
]


class SetInterval():
    def __init__(self, increment, tick_event):
        self.tick_event = tick_event
        self.next_t = time.time() + increment
        self.i = 0
        self.done = False
        self.increment = increment
        Timer(self.next_t - time.time(), self._run).start()

    def _run(self):
        self.tick_event()
        self.next_t += self.increment
        self.i += 1
        if not self.done:
            Timer(self.next_t - time.time(), self._run).start()

    def stop(self):
        self.done = True

    def getTime(self):
        return self.i * self.increment


def now():
    return time.time()


class ResultWriter:

    def __init__(self, name):
        self.Data = []
        self.directory = Configuration.FileOperation.FileDirectory + Configuration.FileOperation.TestName + "/"
        self.filename = datetime.datetime.today().strftime(
            '%Y_%m_%d___%H_%M_%S_') + Configuration.FileOperation.TestName + "_" + name + ".csv"
        os.makedirs(self.directory, exist_ok=True)
        with open(self.directory + self.filename, "w") as f:
            f.writelines(["timestamp;cycle;thumb;index;middle;ring;pinkie;thumb_y;index_y;middle_y;ring_y;pinkie_y\n"])
        self.Timer = SetInterval(Configuration.FileOperation.WritePeriod, self.TimerEvent)

    def TimerEvent(self):
        self.WriteData()

    def WriteData(self):
        arr = self.Data
        self.Data = []
        filename = self.directory + self.filename
        with open(filename, "a") as f:
            f.writelines(arr)

    def AddData(self, record):
        self.Data.append(record)


class InformationBox:
    def __init__(self, window, index, label, default_value, max_value=None, unit="", sensor_font=35):
        self.window = window
        self.index = index
        self.labelText = label
        self.sensor_font = sensor_font
        self.SensorVariable = None
        self.unit = unit
        self.SetMaxValue(max_value)
        self.SetValue(default_value)
        self.CalculateBoundarySize()
        self.CreateFrame()
        self.CreateLabel()
        self.CreateSensorLabel()

    def SetMaxValue(self, max_val):
        self.max_value = max_val
        self.post_fix = self.unit + " / " + str(self.max_value) + self.unit if max_val is not None else self.unit
        self.Update()

    def SetValue(self, value):
        self.value = value
        if isinstance(self.value, float):
            self.text = "{:.2f}".format(self.value) + self.post_fix
        else:
            self.text = str(self.value) + self.post_fix
        self.Update()

    def Update(self):
        if self.SensorVariable is not None:
            self.SensorVariable.set(self.text)

    def CalculateBoundarySize(self):
        self.width = int((Configuration.Window.width - Configuration.Window.padding * (
                Configuration.Window.columncount + 1)) / Configuration.Window.columncount)

        self.y = int(int((self.index / Configuration.Window.columncount)) * (
                Configuration.Window.info_box_height + Configuration.Window.padding) + Configuration.Window.padding)
        self.x = int((self.index % Configuration.Window.columncount) * (
                self.width + Configuration.Window.padding) + Configuration.Window.padding)

        if self.window.max_used_height <= self.y + Configuration.Window.info_box_height:
            self.window.max_used_height = self.y + Configuration.Window.info_box_height

    def CreateFrame(self):
        self.frame = Frame(self.window, height=Configuration.Window.info_box_height, width=self.width)
        self.frame.pack_propagate(0)
        self.frame.place(x=self.x, y=self.y)

    def CreateLabel(self):
        self.label = Label(self.frame, text=self.labelText, justify=CENTER)
        self.label['font'] = font.Font(size=13)
        self.label.configure(background="#DDFFFF")
        # self.label.place(x=0, y=0)
        self.label.pack(fill=X, expand=1)

    def ChangeLabelColor(self, label):
        if label == Labels.Calibration:
            self.label.configure(background="#DDFFFF")
        elif label == Labels.Opening:
            self.label.configure(background=LabelColors.Opening)
        elif label == Labels.Opened:
            self.label.configure(background=LabelColors.Opened)
        elif label == Labels.Closing:
            self.label.configure(background=LabelColors.Closing)
        elif label == Labels.Closed:
            self.label.configure(background=LabelColors.Closed)

    def CreateSensorLabel(self):
        self.SensorVariable = StringVar()
        self.SensorVariable.set(self.text)
        self.Sensor = Label(self.frame, textvariable=self.SensorVariable, justify=CENTER)
        self.Sensor['font'] = font.Font(size=self.sensor_font)
        self.Sensor.pack(fill=X, expand=1)
        # self.Sensor.place(x=self.x, y=self.y+Configuration.Window.info_box_label_height)


class ServerInformation:

    def __init__(self, ip, worker_port, resource_port, is_secure, token):
        self.CloudIP = ip
        self.IP = ip
        self.WorkerPort = worker_port
        self.ResourcePort = resource_port
        self.IsSecure = is_secure
        self.Token = token

    def GetWorkerURL(self):
        return self.GetURLScheme() + self.IP + ":" + self.WorkerPort

    def GetResourceUrl(self, ip=None):
        if ip is None:
            ip = self.IP
        return self.GetURLScheme() + ip + ":" + self.ResourcePort

    def GetURLScheme(self):
        if self.IsSecure:
            return "https://"
        return "http://"

    # Socket URL
    def GetSocketUrl(self, ip, isPatient=False):
        if isPatient:
            return self.GetURLScheme() + ip + ":" + self.WorkerPort + ("?DeviceType=4")
        else:
            return self.GetURLScheme() + ip + ":" + self.WorkerPort + ("?DeviceType=0")

    def GetUserPackage(self, ip, filename):
        return self.GetURLScheme() + ip + ":" + self.WorkerPort + "/GetUserPackage?filename=" + filename
@dataclass
class Status:
    Stop = 1
    Calibrate = 2
    Predict = 3
class TestScreen:
    Keylist = {}

    def __init__(self):
        self.isKeyPressedDict = {}
        self.ActiveStatus = Labels.Calibration
        self.IsStarted = False
        self.Timer = None
        self.ResultWriter = None
        self.SocketConnected = False
        self.VisualizationConnected = False
        self.CloudConnected = False
        self.CloudProcessIsReady = False
        self.Status = Status.Stop
        self.CloudServer = ServerInformation(ip=Configuration.Cloud.ip,
                                                      worker_port=Configuration.Cloud.worker_port,
                                                      resource_port=Configuration.Cloud.resource_port,
                                                      is_secure=Configuration.Cloud.is_secure,
                                                      token=Configuration.Cloud.token)

        self.Title = "Real Time T-IoT Glove System"
        self.window = Tk(className="Real Time T-IoT Glove System")
        self.window.title("Real Time T-IoT Glove System")
        self.window.geometry(self.GetGeometry())
        # self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.tk_setPalette(background='white')
        self.window.max_used_height = 0
        self.SampleCount = 0
        self.frame = Frame(self.window)
        self.frame.pack()
        self.InitInformationBoxes()
        self.InitButtons()
        self.err = False
        if Configuration.Operations.SerialPort:
            self.MicroController = SerialPort.SerialPort(self.DataReceived)
        if Configuration.Operations.Visualization:
            th = threading.Thread(target=self.ConnectToVisualizationSocket)
            th.start()

        # self.InitStatusLists()
        # self.InitSerialPort()

    def InitInformationBoxes(self):
        self.InfoBox_Thumb = InformationBox(self.window, 0, "Thumb", "123", None)
        self.InfoBox_Index = InformationBox(self.window, 1, "Index", "212", None)
        self.InfoBox_Middle = InformationBox(self.window, 2, "Middle", "333", None)
        self.InfoBox_Ring = InformationBox(self.window, 3, "Ring", "234", None)
        self.InfoBox_Pinkie = InformationBox(self.window, 4, "Pinkie", "112", None)
        self.InfoBox_Cloud = InformationBox(self.window, 5, "Cloud", "-", None)
        self.InfoBox_Patient = InformationBox(self.window, 6, "Patient", "-", None)
        self.InfoBox_Status = InformationBox(self.window, 7, "Status", "-", None)
        self.InfoBox_SampleCount = InformationBox(self.window, 8, "Value Count", "0", None)
        self.InfoBox_Duration = InformationBox(self.window, 9, "Duration", "0", None, "s")

    def InitButtons(self):
        padding_count = 2

        # Finger Button
        self.Btn_Thumb = Button(self.window, text="Thumb", width=Configuration.Window.button_width,
                                height=Configuration.Window.button_height, command=lambda: self.SetActiveFinger(0))
        self.Btn_Thumb.pack()
        self.Btn_Thumb.place(x=Configuration.Window.padding,
                             y=self.window.max_used_height + Configuration.Window.padding * padding_count)

        self.Btn_Index = Button(self.window, text="Index", width=Configuration.Window.button_width,
                                height=Configuration.Window.button_height, command=lambda: self.SetActiveFinger(1))
        self.Btn_Index.pack()
        self.Btn_Index.place(**(self.CalculateNextElementPosition(self.Btn_Thumb, padding_small=False)))

        self.Btn_Middle = Button(self.window, text="Middle", width=Configuration.Window.button_width,
                                 height=Configuration.Window.button_height, command=lambda: self.SetActiveFinger(2))
        self.Btn_Middle.pack()
        self.Btn_Middle.place(**(self.CalculateNextElementPosition(self.Btn_Index, padding_small=False)))

        self.Btn_Ring = Button(self.window, text="Ring", width=Configuration.Window.button_width,
                               height=Configuration.Window.button_height, command=lambda: self.SetActiveFinger(3))
        self.Btn_Ring.pack()
        self.Btn_Ring.place(**(self.CalculateNextElementPosition(self.Btn_Middle, padding_small=False)))

        self.Btn_Pinkie = Button(self.window, text="Pinkie", width=Configuration.Window.button_width,
                                 height=Configuration.Window.button_height, command=lambda: self.SetActiveFinger(4))
        self.Btn_Pinkie.pack()
        self.Btn_Pinkie.place(**(self.CalculateNextElementPosition(self.Btn_Ring, padding_small=False)))

        self.FingerLabels = [self.InfoBox_Thumb, self.InfoBox_Index, self.InfoBox_Middle, self.InfoBox_Ring,
                             self.InfoBox_Pinkie]
        self.FingerButtons = [self.Btn_Thumb, self.Btn_Index, self.Btn_Middle, self.Btn_Ring, self.Btn_Pinkie]
        self.ActiveFingers = [False, False, False, False, False]
        self.FingerStatus = [Labels.Calibration] * 5
        # Finger Button
        self.Btn_Closing = Button(self.window, text="Closing", width=Configuration.Window.button_width,
                                  height=Configuration.Window.button_height)
        self.Btn_Closing.pack()
        self.Btn_Closing.place(x=Configuration.Window.padding,
                               y=self.window.max_used_height + Configuration.Window.padding * padding_count + 50)

        self.Btn_Opening = Button(self.window, text="Opening", width=Configuration.Window.button_width,
                                  height=Configuration.Window.button_height)
        self.Btn_Opening.pack()
        self.Btn_Opening.place(**(self.CalculateNextElementPosition(self.Btn_Closing, padding_small=False)))

        self.Option_Variable = StringVar(self.window)
        self.Option_Variable.set(TestOptions[0])
        self.Test_Option = OptionMenu(self.window, self.Option_Variable, *TestOptions, command=self.TestOptionChanged)
        self.Test_Option.config(height=Configuration.Window.option_height, width=Configuration.Window.option_width - 1)
        self.Test_Option.pack()
        self.Test_Option.place(**(self.CalculateNextElementPosition(self.Btn_Opening, padding_small=False)))

        self.Btn_Start = Button(self.window, text="Start", width=Configuration.Window.button_width,
                                height=Configuration.Window.button_height, bg="green2", command=self.StartButtonPressed)
        self.Btn_Start.pack()
        self.Btn_Start.place(**(self.CalculateNextElementPosition(self.Test_Option, padding_small=False)))

        # size = self.CalculateNextElementPosition(self.Btn_Opening, PaddingCount=16, padding_small=False)
        # self.Btn_Start.place(x=size['x'] + 10, y=size['y'])

        self.Btn_Stop = Button(self.window, text="Stop", width=Configuration.Window.button_width,
                               height=Configuration.Window.button_height, bg="red2", command=self.StopButtonPressed)
        self.Btn_Stop["state"] = "disabled"
        self.Btn_Stop.pack()
        self.Btn_Stop.place(**(self.CalculateNextElementPosition(self.Btn_Start, padding_small=False)))

        self.Btn_Opening.bind("<ButtonPress>", self.OpeningButtonPressed)
        self.Btn_Opening.bind("<ButtonRelease>", self.OpeningButtonReleased)
        self.Btn_Closing.bind("<ButtonPress>", self.ClosingButtonPressed)
        self.Btn_Closing.bind("<ButtonRelease>", self.ClosingButtonReleased)

    def OpeningButtonPressed(self, event=None):
        self.ActiveStatus = Labels.Opening
        self.Btn_Opening.configure(activebackground=LabelColors.Opening)
        self.Btn_Opening.configure(bg=LabelColors.Opening)
        self.Btn_Closing.configure(bg="white")
        self.ArrangeFingerStatus()

    def OpeningButtonReleased(self, event=None):
        self.ActiveStatus = Labels.Opened
        self.Btn_Opening.configure(bg=LabelColors.Opened)
        self.Btn_Closing.configure(bg="white")
        self.ArrangeFingerStatus()

    def ClosingButtonPressed(self, event=None):
        self.ActiveStatus = Labels.Closing
        self.SampleCount += 1
        self.Btn_Closing.configure(activebackground=LabelColors.Closing)
        self.Btn_Closing.configure(bg=LabelColors.Closing)
        self.Btn_Opening.configure(bg="white")
        self.ArrangeFingerStatus()
        self.InfoBox_SampleCount.SetValue(self.SampleCount)

    def ClosingButtonReleased(self, event=None):
        self.ActiveStatus = Labels.Closed
        self.Btn_Closing.configure(bg=LabelColors.Closed)
        self.Btn_Opening.configure(bg="white")
        self.ArrangeFingerStatus()

    def StartButtonPressed(self, event=None):
        if Configuration.Operations.Patient:
            th = threading.Thread(target=self.ConnectToSocketAsPatient)
            th.start()
        if Configuration.Operations.Cloud:
            th = threading.Thread(target=self.ConnectToCloud)
            th.start()
            self.InfoBox_Status.SetValue("Wait")

        self.Btn_Stop['state'] = "normal"
        self.Btn_Start['state'] = "disabled"
        self.Test_Option['state'] = "disabled"
        self.SampleCount = 0
        if self.Timer is not None:
            self.Timer.stop()

        self.Timer = SetInterval(1, self.TimerEvent)
        self.ResultWriter = ResultWriter(self.Option_Variable.get())
        self.IsStarted = True
        self.InfoBox_SampleCount.SetValue(self.SampleCount)


    def StopButtonPressed(self, event=None):
        self.Btn_Start['state'] = "normal"
        self.Btn_Stop['state'] = "disabled"
        self.Test_Option['state'] = "normal"
        self.Status = Status.Stop

        if Configuration.Operations.Cloud:
            self.CloudProcessIsReady = False
            self.cloud_sio.disconnect()
            self.InfoBox_Cloud.SetValue("Disconnected")
            self.InfoBox_Status.SetValue("Finished")

        if Configuration.Operations.Patient:
            self.sio_patient.disconnect()
            self.InfoBox_Patient.SetValue("Disconnected")




        if self.Timer is not None:
            self.Timer.stop()
            self.Timer = None

        self.IsStarted = False
        if self.ResultWriter is not None:
            self.ResultWriter.Timer.stop()
            self.ResultWriter.WriteData()
            self.ResultWriter = False

    def ButtonReleased(self, event):
        print("btn released")

    def close(self):
        if Configuration.Operations.SerialPort:
            self.MicroController.run = False

        self.window.destroy()

    def loop(self):
        self.window.bind('<KeyPress>', self.keyPressed)
        self.window.bind('<KeyRelease>', self.keyRealesed)

        self.window.mainloop()

    def ArrangeButtonColor(self):
        for i in range(len(self.ActiveFingers)):
            if self.ActiveFingers[i]:
                self.FingerButtons[i].configure(bg="green2")
            else:
                self.FingerButtons[i].configure(bg="white")

    def ArrangeFingerStatus(self):
        for i in range(len(self.ActiveFingers)):
            if self.ActiveFingers[i]:
                self.FingerStatus[i] = self.ActiveStatus
            elif self.FingerStatus[i] == Labels.Calibration:
                self.FingerStatus[i] = Labels.Opened
        self.ChangeFingersColor()

    def ChangeFingersColor(self):
        for i in range(len(self.FingerStatus)):
            self.FingerLabels[i].ChangeLabelColor(self.FingerStatus[i])
        if self.SocketConnected:
            msg = ";".join(self.FingerStatus)
            self.sio.emit("finger_status", msg)

    def SetActiveFinger(self, finger_index):
        self.ActiveFingers[finger_index] = not self.ActiveFingers[finger_index]
        self.ArrangeButtonColor()

    def keyPressed(self, event):
        if not TestScreen.Keylist.get(event.char):
            TestScreen.Keylist[event.char] = True
            if event.char >= '1' and event.char <= '5':
                finger_index = ord(event.char) - ord("1")
                self.SetActiveFinger(finger_index)
            if event.char == '"':
                self.ActiveFingers = [False] * 5
                self.ArrangeButtonColor()

            if event.char == '6':
                self.ActiveFingers = [True] * 5
                self.ArrangeButtonColor()

            if event.char == 'q' or event.char == 'Q':
                self.ClosingButtonPressed()
            if event.char == 'e' or event.char == 'E':
                self.OpeningButtonPressed()
            if event.char == 's' or event.char == 'S':
                if not self.IsStarted:
                    self.StartButtonPressed()
            if event.char == 'f' or event.char == 'F':
                if self.IsStarted:
                    self.StopButtonPressed()

    def TestOptionChanged(self, event):
        selected = self.Option_Variable.get()

        if selected == "0_Calibration":
            self.ActiveFingers = [False, False, False, False, False]
        if selected == "1_Single_Thumb":
            self.ActiveFingers = [True, False, False, False, False]
        if selected == "2_Single_Index":
            self.ActiveFingers = [False, True, False, False, False]
        if selected == "3_Single_Middle":
            self.ActiveFingers = [False, False, True, False, False]
        if selected == "4_Single_Ring":
            self.ActiveFingers = [False, False, False, True, False]
        if selected == "5_Single_Pinkie":
            self.ActiveFingers = [False, False, False, False, True]
        if selected == "6_Grasp":
            self.ActiveFingers = [True, True, True, True, True]
        if selected == "7_FourFinger_Grasp":
            self.ActiveFingers = [False, True, True, True, True]
        if selected == "8_Thumb2Index":
            self.ActiveFingers = [True, True, False, False, False]
        if selected == "9_Thumb2Middle":
            self.ActiveFingers = [True, False, True, False, False]
        if selected == "10_Thumb2Ring":
            self.ActiveFingers = [True, False, False, True, False]
        if selected == "11_Thumb2Pinkie":
            self.ActiveFingers = [True, False, False, False, True]
        self.ArrangeButtonColor()

    def keyRealesed(self, event):
        TestScreen.Keylist[event.char] = False
        if event.char == 'q' or event.char == 'Q':
            self.ClosingButtonReleased()
        if event.char == 'e' or event.char == 'E':
            self.OpeningButtonReleased()

    def TimerEvent(self):
        if self.Timer is not None:
            self.InfoBox_Duration.SetValue(self.Timer.i)

    def GetGeometry(self):
        return str(Configuration.Window.width) + "x" + str(Configuration.Window.height)

    def CreateSample(self, timestamp, sample):
        return str(timestamp) + ";" + str(self.SampleCount) + ";" + sample + ";" + (";".join(self.FingerStatus) + "\n")

    def DataReceived(self, timestamp, sample):
        data = sample.split(";")
        self.SampleCount+=1
        if len(data) != 5:
            print('Error: ' + data)
            return
        if self.CloudProcessIsReady:
            if self.Timer.i > Configuration.Operations.PredictTime:
                if self.Status !=Status.Predict:
                    self.Status = Status.Predict
                    self.InfoBox_Status.SetValue("Predict")

                msg=str(self.SampleCount)+"|0;"+sample
                self.cloud_sio.emit("sensor_data",msg)
            elif self.Timer.i > Configuration.Operations.CalibrationTime:
                if self.Status !=Status.Calibrate:
                    self.Status = Status.Calibrate
                    self.InfoBox_Status.SetValue("Calibrate")

                msg=str(self.SampleCount)+"|1;"+sample
                self.cloud_sio.emit("sensor_data",msg)

        if self.MicroController.data_count % Configuration.Window.refresh_count == 0:
            self.InfoBox_Thumb.SetValue(data[0])
            self.InfoBox_Index.SetValue(data[1])
            self.InfoBox_Middle.SetValue(data[2])
            self.InfoBox_Ring.SetValue(data[3])
            self.InfoBox_Pinkie.SetValue(data[4])
        if self.VisualizationConnected:
            # msg = ";".join(self.data[0:5])
            self.sio.emit("sensor", sample)

    def CalculateNextElementPosition(self, element, PaddingCount=1, padding_small=False):
        self.window.update_idletasks()
        padding = Configuration.Window.small_padding if padding_small else Configuration.Window.btn_padding
        x = element.winfo_x() + element.winfo_width() + padding * PaddingCount
        y = element.winfo_y()
        return {"x": x, "y": y}

    def ConnectToVisualizationSocket(self):
        if self.vis_err:
            return
        sio = socketio.Client()
        self.vis_sio = sio
        this = self

        @sio.on("connect")
        def connect():
            #self.window.title(self.Title + " (Connected)")
            self.VisualizationConnected = True

        @sio.on('disconnected')
        def disconnected():
            self.VisualizationConnected = False


        while True:
            try:
                sio.connect('http://127.0.0.1:25368?Directory=Home')
                break
            except Exception as e:
                time.sleep(1)
                print(e)

    def ConnectToCloud(self):

        sio = socketio.Client()
        self.cloud_sio = sio

        @sio.on("connect")
        def connect():
            self.CloudConnected = True
            self.InfoBox_Cloud.SetValue("Connected")
            logger.info('[Cloud] ' +  "DeviceConnected;" + str(now()))
            # Send user index
            sio.emit("app_info", (0, "DT", self.CloudServer.Token))
            logger.info('[Cloud] ' + " connected")

        @sio.on("application_disconnected")
        def application_disconnected(status):
            logger.info('[Cloud] ' + "ApplicationDisconnected;" + str(now()))
            self.cloud_err = True

        @sio.on("process_ready")
        def process_ready(message):
            res = message.split(";")
            if int(res[0]):
                self.CloudProcessIsReady = True
                self.InfoBox_Status.SetValue("Ready")
                logger.info('[Cloud] ' + "ProcessReady;" + str(now()))
                self.InfoBox_Status.SetValue("Ready")

            else:
                logger.error('[Cloud] ' + " faced an error. Message: " + res[1])
                sio.disconnect()
                self.StopThread(err=True)
                self.cloud_err = True

        @sio.on("test")
        def test(info):
            print("Test message" + self.i)

        @sio.on('disconnected')
        def disconnected():
            self.CloudConnected = False
            self.InfoBox_Cloud.SetValue("Disconnected")
            logger.info('[Cloud] ' + self.i + 'th User disconnected.')

        self.cloud_url = self.CloudServer.GetSocketUrl(self.CloudServer.IP)
        while True:
            try:
                # sio.connect('http://192.168.2.59:3000')
                sio.connect(self.cloud_url)
                sio.emit("temp", "kadir")
                break
            except Exception as e:
                logger.error('[Cloud] ' + self.cloud_url + " connection err")
                time.sleep(1)

    def ConnectToSocketAsPatient(self):
        if self.err:
            return
        sio = socketio.Client()
        self.sio_patient = sio
        self.ActuateWindow = 5
        self.finger_buffers = [[Labels.Calibration]*self.ActuateWindow for i in range(5)]
        @sio.on("connect")
        def connect():
            self.PatientConnected = True
            self.sio_patient.emit("app_info", self.CloudServer.Token)

            logger.info("[Patient] Connected;" + str(now()))
            self.InfoBox_Patient.SetValue("Connected")
            # Send user index

        @sio.on("test")
        def test(info):
            print("Test message" + self.i)

        @sio.on("process_ready")
        def process_ready(message):
            res = message.split(";")
            if int(res[0]):
                logger.info('[Patient] ' + "ProcessReady;" + str(now()))

        # Message -> 'data_index;result;added_queue;process_started;process_finished;response_time'
        @sio.on("result")
        def result(message):
            res = message.split(";")
            if int(res[0])%50 ==0:
                print('[Patient] Result: ' +message )
            changed=False
            if self.Timer.i > Configuration.Operations.Actuate:
                finger_data = res[1:6]
                for i in range(len(finger_data)):
                    finger_buffer = self.finger_buffers[i]
                    finger_buffer.pop(0)
                    current_val = finger_data[i]
                    all_is_same = True
                    for val in finger_buffer:
                        if val != current_val:
                            all_is_same = False
                    finger_buffer.append(finger_data[i])

                    if all_is_same and current_val !=self.FingerStatus[i]:
                        self.FingerStatus[i] = current_val
                        changed=True

                if changed:
                    self.ChangeFingersColor()





        @sio.on('disconnected')
        def disconnected():
            logger.info("[Patient] disconnected.")
            self.InfoBox_Patient.SetValue("Disconnected")


        self.patient_url = self.CloudServer.GetSocketUrl(self.CloudServer.IP, isPatient=True)
        while True:
            try:
                # sio.connect('http://192.168.2.59:3000')
                sio.connect(self.patient_url)
                break
            except Exception as e:
                logger.error(self.patient_url + " connection err")
                time.sleep(1)


def main():
    test = TestScreen()
    test.loop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
