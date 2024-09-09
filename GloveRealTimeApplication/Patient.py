from dataclasses import dataclass

import socketio
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Configuration:
    Actuate=15

    @dataclass(frozen=True)
    class Cloud:
        # ip = '164.92.168.129'
        ip = '192.168.2.125'
        worker_port = '27592'
        resource_port = '17796'
        is_secure = False
        token = "pkQmpguDVt8UISt5LeQv0TIEdM1MM3svt8WK6jOWiwmShVjkyZlQTU9FYY3WqwJL"


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
class Labels:
    Opening = "0"
    Opened = "1"
    Closing = "2"
    Closed = "3"
    Calibration = "9"

def now():
    return time.time()

class Patient:
    def __init__(self):
        self.err = False
        self.FingerStatus = [Labels.Calibration]*5
        self.CloudServer = ServerInformation(ip=Configuration.Cloud.ip,
                                             worker_port=Configuration.Cloud.worker_port,
                                             resource_port=Configuration.Cloud.resource_port,
                                             is_secure=Configuration.Cloud.is_secure,
                                             token=Configuration.Cloud.token)

    def ConnectToSocketAsPatient(self):
        if self.err:
            return
        sio = socketio.Client()
        self.sio_patient = sio
        self.ActuateWindow = 5
        self.finger_buffers = [[Labels.Calibration] * self.ActuateWindow for i in range(5)]
        self.Time = None

        @sio.on("connect")
        def connect():
            self.PatientConnected = True
            self.sio_patient.emit("app_info", self.CloudServer.Token)

            logger.info("[Patient] Connected;" + str(now()))
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
            if self.Time is None:
                self.Time = now()
            res = message.split(";")
            if int(res[0]) % 50 == 0:
                #print('[Patient] Result: ' + message)
                pass
            changed = False
            if now()-self.Time > Configuration.Actuate:
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

                    if all_is_same and current_val != self.FingerStatus[i]:
                        self.FingerStatus[i] = current_val
                        changed = True


                if changed:
                    print('[Patient] FingerStatus: ' + str(self.FingerStatus))



        @sio.on('disconnected')
        def disconnected():
            logger.info("[Patient] disconnected.")

        self.patient_url = self.CloudServer.GetSocketUrl(self.CloudServer.IP, isPatient=True)
        while True:
            try:
                # sio.connect('http://192.168.2.59:3000')
                sio.connect(self.patient_url)
                break
            except Exception as e:
                logger.error(self.patient_url + " connection err")
                time.sleep(1)


Patient().ConnectToSocketAsPatient()
while True:
    time.sleep(1)