import logging
import time
import datetime
from threading import Thread

import socketio

import gait_analysis
from FingerPhase import GloveAnalysis
from collections import deque
from config import Configuration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def now():
    return datetime.datetime.now().timestamp()


class SensorData:
    def __init__(self, userid,data_index, data, socket_received, added_queue ):
        self.userid = userid
        self.data = data
        self.data_index=data_index
        self.socket_received = float(socket_received)
        self.added_queue =added_queue
        self.process_started=None
        self.process_finished=None

    def  PrepareResponse(self, result):
        added_queue=self.added_queue-self.socket_received
        process_started = self.process_started-self.added_queue
        process_finished = self.process_finished -self.process_started
        return f"{self.userid}|{self.socket_received}|{self.data_index};{result};{added_queue};{process_started};{process_finished}"

class SingleThreadProcess:
    def __init__(self):
        self.ServerConnected = False
        self.ProcessActive = False
        self.users = {}
        self.queue = deque()
        self.ConnectToServer()

    def ConnectToServer(self):
        sio = socketio.Client()
        self.sio = sio

        @sio.on("connect")
        def connect():
            self.ServerConnected = True
            logger.info("FingerPhasePredictor connected")

        @sio.on("new_user")
        def new_user(message):
            userid, socketid, model = message.split("|")
            try:
                self.users = {}
                self.users[userid] = GloveAnalysis(model)
                sio.emit("process_ready", f"{userid}|1")
                logger.info(f"A user connected: UserId: {socketid}")
            except:
                sio.emit("process_ready", f"{userid}|0;AppNotCreate")
                logger.info(f"A user connected: UserId: {socketid}")



        @sio.on("user_disconnected")
        def user_disconnected(userid):
            self.users.pop(userid, None)
            logger.info('User disconnected: '+userid)

        #sensor data -> userid|dataIndex|data|socket_received
        @sio.on("sensor_data")
        def sensor_data(data):
            user_id, dataIndex, data, socket_received = data.split('|')
            added_queue = now()
            self.queue.appendleft(SensorData(user_id, dataIndex, data, socket_received, added_queue))
            self.CheckProcess() #new version
        while True:
            try:
                sio.connect(Configuration.SOCKET_URL)
                sio.emit("Test", "FingerPhasePredictor")
                break
            except Exception as e:
                logger.error("Connection error")
                time.sleep(1)

    def processCopy(self):
        while True:
            while len(self.queue) > 0:
                record = self.queue.pop()
                record.process_started = now()
                app = self.users.get(record.userid)
                if app is not None:
                    result = app.Predict(record.data)
                    record.process_finished = now()
                    self.sio.emit("result", record.PrepareResponse(result))
                else:
                    data_splitted = record.data.split(";")
                    postfix= ";"+data_splitted[2] if len(data_splitted)>2 else ""
                    record.process_finished = now()
                    self.sio.emit("result",record.PrepareResponse("-1"+postfix))

            time.sleep(0.001)

    def process(self):
        while len(self.queue) > 0:
            record = self.queue.pop()
            record.process_started = now()
            app = self.users.get(record.userid)
            if app is not None:
                result = app.Predict(record.data)
                record.process_finished = now()
                self.sio.emit("result", record.PrepareResponse(result))
            else:
                data_splitted = record.data.split(";")
                postfix= ";"+data_splitted[2] if len(data_splitted)>2 else ""
                record.process_finished = now()
                self.sio.emit("result",record.PrepareResponse("-1"+postfix))
        self.ProcessActive=False


    def CheckProcess(self):
        if not self.ProcessActive:
            self.ProcessActive = True
            thread = Thread(target=single.process)
            thread.start()
            thread.join()




if __name__ == '__main__':
    GloveAnalysis.Initiate()
    single = SingleThreadProcess()
    #thread = Thread(target=single.process)
    #thread.start()
    #thread.join()



