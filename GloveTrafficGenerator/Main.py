import logging
import sys
from threading import Thread, Timer, Event
from enum import Enum
import time
import datetime
import socketio
from Application import GloveAnalysis
import json
import os
from Config import *
import requests
import geocoder
import re

if len(sys.argv)>1:
    Configuration.ModelName = sys.argv[1]

GloveAnalysis.ReadAllData()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
if GloveAnalysis.Data is None:
    print("All tests is finished!")
    exit()

def now():
    return datetime.datetime.now().timestamp()


class SetInterval:
    def __init__(self, increment, tick_event):
        self.tick_event = tick_event
        self.next_t = time.time()
        self.i = 0
        self.done = False
        self.increment = increment
        self._run()

    def _run(self):
        self.tick_event()
        self.next_t += self.increment
        self.i += 1
        if not self.done:
            Timer(self.next_t - time.time(), self._run).start()

    def stop(self):
        self.done = True


class ResultWriter:
    ThreadTimeInfo = {}
    ThreadInformations = {}
    ResourceInfo = {}

    def __init__(self,application):
        ResultWriter.Obj = self
        self.directory = Configuration.FileDirectory+Configuration.ModelName +"/"+ datetime.datetime.today().strftime(
            '%Y_%m_%d___%H_%M_%S')+ f"__TS{application.TestSubjectId:02d}_{application.Postfix}" + Configuration.FilePostfix +("_Short" if Configuration.ShortTest else "") + "/"
        os.makedirs(self.directory, exist_ok=True)
        self.timer = SetInterval(Configuration.FileWritePeriod, self.TimerEvent)

    def TimerEvent(self):
        self.WriteData()
        self.WriteResourceInfo()
        self.WriteThreadInformations()

    def WriteData(self):
        temp_dict = ResultWriter.ThreadTimeInfo
        ResultWriter.ThreadTimeInfo = {}
        for i in temp_dict:
            filename = self.directory + str(i) + ".csv"
            answ = os.path.exists(filename)
            with open(filename, "a" if answ else "w") as f:
                f.writelines(temp_dict[i])

    def WriteResourceInfo(self):
        temp_dict = ResultWriter.ResourceInfo
        ResultWriter.ResourceInfo = {}
        for i in temp_dict:
            filename = self.directory + "resource__" + re.sub('[^0-9a-zA-Z]+', '_', i) + ".json"
            answ = os.path.exists(filename)
            with open(filename, "a" if answ else "w") as f:
                f.writelines(temp_dict[i])

    def WriteThreadInformations(self):
        temp_dict = ResultWriter.ThreadInformations
        ResultWriter.ThreadInformations = {}
        for i in temp_dict:
            filename = self.directory + str(i) + "_ThreadInformation.csv"
            answ = os.path.exists(filename)
            with open(filename, "a" if answ else "w") as f:
                f.writelines(temp_dict[i])

    @staticmethod
    def AddThreadTimeInformation(thread_no, record):
        timeInfo = ResultWriter.ThreadTimeInfo.get(thread_no)
        if timeInfo is None:
            ResultWriter.ThreadTimeInfo[thread_no] = [record + "\n"]
        else:
            timeInfo.append(record + "\n")

    @staticmethod
    def AddResourceInformation(url, info):
        resourceInfo = ResultWriter.ResourceInfo.get(url)
        if resourceInfo is None:
            ResultWriter.ResourceInfo[url] = [json.dumps(info) + "\n"]
        else:
            resourceInfo.append(json.dumps(info) + "\n")

    @staticmethod
    def AddThreadInformation(thread_no, record):
        threadInfo = ResultWriter.ThreadInformations.get(thread_no)
        if threadInfo is None:
            ResultWriter.ThreadInformations[thread_no] = [record + "\n"]
        else:
            threadInfo.append(record + "\n")


class CloudTester(Thread):
    ThreadCount = 0
    ClosedThreads = 0
    threads = []
    resource_threads = {}

    def __init__(self, i, server, application, modelname):
        Thread.__init__(self)
        self.i = i
        self.Server = server
        self.SamplingPeriod = Configuration.SamplingPeriod
        self.FogProcessIsReady = False
        self.FogConnected = False
        self.Application = application
        self.Data = GloveAnalysis.Data
        self.ModelName = modelname
        self.data_index = 0
        self.err = False
        self.RequestTimeList = []
        self.FileName = None
        self.StopCriteria = self.Data.CalibrationLen + Configuration.TestDataLength if Configuration.ShortTest else self.Data.TestDataLen
        ResultWriter.AddThreadInformation(i, "Feature;Value")
        ResultWriter.AddThreadInformation(i, "ApplicationName;" + self.Application.Name)
        ResultWriter.AddThreadInformation(i, "ModelName;" + Configuration.ModelName)
        ResultWriter.AddThreadInformation(i, "DeviceURL;" + self.Server.GetWorkerURL())
        ResultWriter.AddThreadInformation(i, "ThreadIndex;" + self.i)
        ResultWriter.AddThreadInformation(i, "TestSubjectId;" + str(GloveAnalysis.TestSubjectId))
        ResultWriter.AddThreadInformation(i, "TestPostfix;" + GloveAnalysis.Postfix)
        ResultWriter.AddThreadInformation(i, "CalibrationDataLength;" + str(self.Data.CalibrationLen))
        ResultWriter.AddThreadInformation(i, "TestDataLength;" + str(Configuration.TestDataLength))
        ResultWriter.AddThreadInformation(i, "TestDataRepeatCount;" + str(Configuration.SendAllDataTimes))
        GloveAnalysis.StartTime =str(now())
        ResultWriter.AddThreadInformation(i, "ThreadCreated;" + GloveAnalysis.StartTime)


    def run(self):
        ResultWriter.AddThreadInformation(self.i, "ThreadStarted;" + str(now()))
        self.StartResourceThread()
        self.ConnectToSocketAsPatient()
        self.ConnectToSocket()
        self.CheckFogDeviceIsReady()
        self.StartOperation()

    def StartResourceThread(self):
        if self.err:
            return
        if CloudTester.resource_threads.get(self.Server.IP) is None:
            resource_url = self.Server.GetResourceUrl()
            CloudTester.resource_threads[self.Server.IP] = ResourceInformation(resource_url)
            CloudTester.resource_threads[self.Server.IP].start()
            ResultWriter.AddThreadInformation(self.i, "WorkerResourceThreadStarted;" + str(now()))
        else:
            logger.error("Thread No: " + self.i + " faced an error at Worker Resource Device Connection!")



    def ConnectToSocket(self):
        if self.err:
            return
        sio = socketio.Client()
        self.sio = sio

        @sio.on("connect")
        def connect():
            self.FogConnected = True
            ResultWriter.AddThreadInformation(self.i, "DeviceConnected;" + str(now()))
            # Send user index
            sio.emit("app_info", (self.i,Configuration.ModelName,self.Server.Token))
            logger.info(self.i + " connected")

        @sio.on("application_disconnected")
        def application_disconnected(status):
            ResultWriter.AddThreadInformation(self.i, "ApplicationDisconnected;" + str(now()))
            self.err = True

        @sio.on("process_ready")
        def process_ready(message):
            res = message.split(";")
            if int(res[0]):
                self.FogProcessIsReady = True
                ResultWriter.AddThreadInformation(self.i, "ProcessReady;" + str(now()))

            else:
                ResultWriter.AddThreadInformation(self.i, "ProcessCannotReady;" + str(now()))
                logger.error("Thread No: " + self.i + " faced an error. Message: " + res[1])
                sio.disconnect()
                self.StopThread(err=True)
                self.err = True

        @sio.on("test")
        def test(info):
            print("Test message" + self.i)

        @sio.on('filename')
        def filename(file):
            self.filename = file

            ResultWriter.AddThreadInformation(self.i, "Filename;" + self.filename)

        @sio.on('disconnected')
        def disconnected():
            ResultWriter.AddThreadInformation(self.i, "SocketDisconnected;" + str(now()))
            logger.info(self.i + 'th User disconnected.')
        self.url =self.Server.GetSocketUrl(self.Server.IP)
        while True:
            try:
                # sio.connect('http://192.168.2.59:3000')
                sio.connect(self.url)
                sio.emit("temp", "kadir")
                break
            except Exception as e:
                logger.error(self.url + " connection err")
                time.sleep(1)

    def ConnectToSocketAsPatient(self):
        if self.err:
            return
        sio = socketio.Client()
        self.sio_patient = sio

        @sio.on("connect")
        def connect():
            self.FogConnected = True
            ResultWriter.AddThreadInformation(self.i, "PatientConnected;" + str(now()))
            # Send user index
            sio.emit("app_info", self.Server.Token)
            logger.info(self.i + " patient connected")


        @sio.on("test")
        def test(info):
            print("Test message" + self.i)

        # Message -> 'data_index;result;added_queue;process_started;process_finished;response_time'
        @sio.on("result")
        def result(message):
            received_time = now()
            csvline = "result;" + message + ";" + str(received_time)
            ResultWriter.AddThreadTimeInformation(self.i, csvline)
            res = message.split(";")
            data_index = int(res[0])
            if self.i == '0' and data_index % 50 == 0:
                for i in range(len(self.RequestTimeList)):
                    request_time = self.RequestTimeList[i]
                    if data_index == request_time[0]:
                        total_time = received_time - request_time[1]
                        new_info = f"remain: {res[0]}/{self.StopCriteria}\nTotalTime: {total_time*1000:.2f}  -  AddedQueue: {float(res[6])*1000:.2f}  -  ProcessStarted: {float(res[7])*1000:.2f}  -  ProcessFinished: {float(res[8])*1000:.2f}  -  ResponseTime: {float(res[9])*1000:.2f}"
                        logger.info(new_info)
                        self.RequestTimeList.pop(i)
                        break
            if data_index == 0:
                ResultWriter.AddThreadInformation(self.i, "FirstResponseReceived;" + str(received_time))


        @sio.on('disconnected')
        def disconnected():
            ResultWriter.AddThreadInformation(self.i, "PatientSocketDisconnected;" + str(now()))
            logger.info(self.i + 'th Patient disconnected.')
        self.patient_url =self.Server.GetSocketUrl(self.Server.IP,isPatient=True)
        while True:
            try:
                # sio.connect('http://192.168.2.59:3000')
                sio.connect(self.patient_url)
                sio.emit("temp", "kadir")
                break
            except Exception as e:
                logger.error(self.patient_url + " connection err")
                time.sleep(1)

    def StopThread(self, err = False):
        CloudTester.ClosedThreads += 1
        ResultWriter.AddThreadInformation(self.i, "TheadStopped;" + str(now()))
        self.err=True
        # if CloudTester.ClosedThreads >= CloudTester.ThreadCount:
        #     ResultWriter.Obj.TimerEvent()
        #     print("Finished")
        #     os._exit(1)
        #
        # sys.exit()
        if not err:
            Timer(Configuration.FileWritePeriod, self.SaveRequestFile).start()

    def SaveRequestFile(self):
        r = requests.get(self.Server.GetSocketUrl(self.Server.IP) + "/GetUserPackage?filename=" + self.filename)
        with open(ResultWriter.Obj.directory + self.filename, 'wb') as f:
            f.write(r.content)

        if CloudTester.ClosedThreads >= CloudTester.ThreadCount:
            ResultWriter.Obj.TimerEvent()
            print("Finished")
            os._exit(1)

        sys.exit()

    def CheckFogDeviceIsReady(self):
        if self.err:
            return
        logger.info(self.i + " wait device is ready!")

        while not self.FogProcessIsReady:
            if self.err:
                self.StopThread(err=True)

            time.sleep(0.2)

        logger.info(self.i + "th device is ready!")

    def SendData(self):
        if self.err:
            self.interval.stop()
            self.sio.disconnect()
            self.StopThread()
        message = None
        data_index = self.data_index
        self.data_index += 1

        if data_index < self.Data.CalibrationLen:
            message = str(data_index) + "|1;" + str(self.Data.CalibrationData[data_index])
        else:
            message = str(data_index) + "|0;" + str(
                self.Data.TestData[(data_index - self.Data.CalibrationLen) % self.Data.TestDataLen])


        request_time = now()
        self.sio.emit("sensor_data", message)

        csv_line = "request;" + str(data_index) + ";" + str(request_time)
        ResultWriter.AddThreadTimeInformation(self.i, csv_line)

        if self.i == '0' and data_index % 50 == 0:
            self.RequestTimeList.append((data_index, request_time))

        if self.data_index > self.StopCriteria:
            self.interval.stop()
            interval = SetInterval(1000,self.StopOperations)
            interval.stop()
            #self.StopThread()
    def StopOperations(self):
        GloveAnalysis.WriteFinishedTest()
        self.StopThread()
    def StartOperation(self):
        if self.err:
            return
        ResultWriter.AddThreadInformation(self.i, "FirstDataSent;" + str(now()))
        self.interval = SetInterval(self.SamplingPeriod, self.SendData)


class ResourceInformation(Thread):
    def __init__(self, url):
        Thread.__init__(self)
        self.url = url



    def run(self):
        sio = socketio.Client()
        self.sio = sio

        @sio.on("connect")
        def connect():
            self.FogConnected = True
            sio.emit('register_resource', True)
            logger.info('Resource Information for ' + self.url + " connected")

        @sio.on("resource_info")
        def resource_info(info):
            ResultWriter.AddResourceInformation(self.url, info)

        @sio.on('disconnected')
        def disconnected():
            logger.info(self.i + 'th User disconnected.')

        while True:
            try:
                sio.connect(self.url)
                break
            except Exception as e:
                logger.error("Resource Information connection err")
                time.sleep(1)


def Main():
    rw = ResultWriter(GloveAnalysis)
    index = 0
    for server in Configuration.Servers:
        for i in range(server.ThreadCount):
            thread = CloudTester(str(index), server, GloveAnalysis, Configuration.ApplicationTestType)
            thread.start()
            CloudTester.threads.append(thread)
            index += 1

    CloudTester.ThreadCount = len(CloudTester.threads)


if __name__ == "__main__":
    Main()
