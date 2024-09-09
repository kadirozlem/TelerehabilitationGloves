from enum import Enum
from dataclasses import dataclass


class ServerInformation:
    def __init__(self, ip, worker_port, resource_port, thread_count, is_secure,token):
        self.CloudIP = ip
        self.IP = ip
        self.WorkerPort = worker_port
        self.ResourcePort = resource_port
        self.ThreadCount = thread_count
        self.IsSecure = is_secure
        self.Token = token

    def GetWorkerURL(self):
        return self.GetURLScheme() + self.IP + ":" + self.WorkerPort

    def GetResourceUrl(self, ip = None):
        if ip is None:
            ip= self.IP
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


class TestType(Enum):
    Cloud = 1  # Start test for cloud

    def getName(test_type):
        if test_type == TestType.Cloud:
            return "Cloud"


@dataclass
class Configuration:
    TestSubjectCount = 12
    SendAllDataTimes = 1
    FileWritePeriod = 5
    TestDataLength = 300 #18000
    ShortTest= False
    SamplingPeriod = 0.020
    FileDirectory = "./Results/"
    FilePostfix = "Test"
    ApplicationTestType = TestType.Cloud
    Token = "pkQmpguDVt8UISt5LeQv0TIEdM1MM3svt8WK6jOWiwmShVjkyZlQTU9FYY3WqwJL"
    ModelName="DT"


Configuration.Servers = [
    #ServerInformation(ip='164.92.168.129', worker_port='27592', resource_port='17796', thread_count=1, is_secure=False)
    #ServerInformation(ip='127.0.0.1', worker_port='27592', resource_port='17796', thread_count=1, is_secure=False, token="pkQmpguDVt8UISt5LeQv0TIEdM1MM3svt8WK6jOWiwmShVjkyZlQTU9FYY3WqwJL")
    ServerInformation(ip='164.92.168.129', worker_port='27592', resource_port='17796', thread_count=1, is_secure=False, token="pkQmpguDVt8UISt5LeQv0TIEdM1MM3svt8WK6jOWiwmShVjkyZlQTU9FYY3WqwJL")
]
