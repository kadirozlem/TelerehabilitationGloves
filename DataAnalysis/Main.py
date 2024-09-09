import json
import math
import os
import re

import os
import shutil
import statistics
from dataclasses import dataclass
import numpy as np

import pandas as pd
from scipy.signal import savgol_filter
# Import colorama
from colorama import init, Fore, Style

from FileOperations import FileOperations
from Charts import Charts
from Configuration import Configuration

# initialize
init()


class Print:
    ErrorBuffer = []

    @staticmethod
    def WriteErrors():
        while len(Print.ErrorBuffer) > 0:
            Print.Red(Print.ErrorBuffer.pop(0))

    @staticmethod
    def AddError(txt):
        Print.ErrorBuffer.append(txt)

    @staticmethod
    def Red(txt):
        print(Fore.RED + txt + Style.RESET_ALL)

    @staticmethod
    def White(txt):
        print(Fore.WHITE + txt + Style.RESET_ALL)

    @staticmethod
    def Blue(txt):
        print(Fore.BLUE + txt + Style.RESET_ALL)

    @staticmethod
    def Green(txt):
        print(Fore.GREEN + txt + Style.RESET_ALL)


class RequestTime:
    TotalResponseTime = []
    TotalResponseTimeHeaders = []

    def __init__(self, arr):
        self.index = arr[1]
        self.RequestTimestamp = float(arr[2])
        self.isWAN = False

    def AddResult(self, arr):
        self.Result = arr[2]
        self.AddedQueue = float(arr[7])
        self.ProcessStarted = float(arr[8])
        self.ProcessTime = float(arr[9])
        self.WorkerTotal = float(arr[10])
        self.ResponseTimestamp = float(arr[-1])
        self.TotalResponseTime = self.ResponseTimestamp - self.RequestTimestamp

        self.ResultReceivedSocket = self.WorkerTotal - (self.AddedQueue + self.ProcessStarted + self.ProcessTime)
        if len(arr) > 8:
            self.isWAN = True
            self.UserEmitterReqRes = float(arr[7])
            self.Network = (self.TotalResponseTime - self.UserEmitterReqRes) / 2
            self.UserEmitterToWorker = (self.UserEmitterReqRes - self.WorkerTotal) / 2
            self.Latency = self.Network + self.UserEmitterToWorker + self.AddedQueue
        else:
            self.Network = (self.TotalResponseTime - self.WorkerTotal) / 2
            self.Latency = self.Network + self.AddedQueue

        self.ExecutionTime = self.ProcessTime
        self.QueuingDelay = self.ProcessStarted
        self.ResponseTime = self.TotalResponseTime

        if self.Result != "-1" and self.TotalResponseTime < 0:
            a = 1

    def GetHeader(self):
        if self.isWAN:
            return [
                "UB",  # User Broker (User Emitter)
                "BS",  # Broker Socket (Worker)
                "SQ",  # Socket to Queue
                "QP",  # Queue Wait Time
                "PT",  # Process Time
                "PS",  # Process to Socket
                "SB",  # Socket Broker
                "BU"  # Broker User
            ]
        else:
            return [
                "US",  # User to Socket (Worker)
                "SQ",  # Socket to Queue
                "QP",  # Queue Wait Time
                "PT",  # Process Time
                "PS",  # Process to Socket
                "SB"  # Socket to User
            ]

    def GetValues(self):
        if self.isWAN:
            return [self.Network, self.UserEmitterToWorker, self.AddedQueue, self.ProcessStarted, self.ProcessTime,
                    self.ResultReceivedSocket, self.UserEmitterToWorker, self.Network]
        else:
            return [self.Network, self.AddedQueue, self.ProcessStarted, self.ProcessTime, self.ResultReceivedSocket,
                    self.Network]


class CloudAnalysis:
    TestTypes = [
        "LR", "DT", "kNN", "MLP", "RF", "XGB"
    ]

    TestResults = {

    }

    @staticmethod
    def WriteTestResults(name="TestResults"):
        os.makedirs('./Cache/', exist_ok=True)
        json.dump(CloudAnalysis.TestResults, open('./Cache/' + name + '.json', "w"))

    @staticmethod
    def ReloadTestResult(name="TestResults"):
        if os.path.exists('./Cache/' + name + '.json'):
            CloudAnalysis.TestResults = json.load(open('./Cache/' + name + '.json'))
            return True
        return False

    @staticmethod
    def CheckFiles(functionName):
        counter = 1
        typeLength = len(CloudAnalysis.TestTypes)

        for testType in CloudAnalysis.TestTypes:
            print("########################################")
            print(testType + " Analysis Started.")
            print("[" + str(counter) + "/" + str(typeLength) + "]: " + testType)
            # Execute Function
            print('Data Analysis Started')
            functionName(testType+"/")
            counter += 1

    @staticmethod
    def CheckThreadInformationExists(directory):

        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)
        counter = 1
        for folder in folders:
            print(f"[{counter}/{folder_count}]: {folder}", end="\r")
            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)

            TimeInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" in x]
            if len(TimeInformation) == 0:
                Print.Red(test_path)
            counter += 1

    @staticmethod
    def CheckTimeInformationExists(directory):
        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)
        counter = 1
        for folder in folders:
            print(f"[{counter}/{folder_count}]: {folder}", end="\r")
            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)
            TimeInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" not in x]
            if len(TimeInformation) == 0:
                Print.Red(test_path)
            counter += 1

    @staticmethod
    def CheckTimeInformationSize(directory):
        limit = 100
        if directory.endswith("/Full/"):
            limit = 17000
        not_res_limit = 200
        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)

        counter = 1
        for folder in folders:

            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)
            TimeInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" not in x]
            if len(TimeInformation) != 0:
                responded_request, candidate_request, requests = CloudAnalysis.ReadTimeInformationFile(test_path,
                                                                                                     TimeInformation[0])
                if responded_request < limit:
                    Print.AddError("Small file: " + str(responded_request) + "/" + str(limit))
                    Print.AddError("Path: " + test_path + "/" + TimeInformation[0])
                if candidate_request > not_res_limit:
                    Print.AddError("To much Non request file: " + str(candidate_request) + "/" + str(
                        candidate_request + responded_request))
                    Print.AddError("Path: " + test_path + "/" + TimeInformation[0])
            else:
                Print.AddError("Time information is not found " + test_path)
            if len(requests) > 0:
                write_directory = FileOperations.PreprocessedResults + test_path + "/"
                # requests = [x for x in requests if hasattr(x, 'Result')]
                print(f"[{counter}/{folder_count}]: Size: {len(requests)} -- {folder}")
                requests.sort(key=lambda x: x.index)
                header = requests[0].GetHeader()
                FileOperations.WriteDataToCSV([x.GetValues() for x in requests if x.Result == "-1"], header,
                                              write_directory, "calibration")
                FileOperations.WriteDataToCSV([x.GetValues() for x in requests if x.Result != "-1"], header,
                                              write_directory, "predict")
                FileOperations.WriteDataToCSV([x.GetValues() for x in requests], header, write_directory, "full")
            else:
                print(f"[{counter}/{folder_count}]: {folder}")

            counter += 1

    @staticmethod
    def ReadTimeInformationFile(directory, file):
        samples = FileOperations.ReadCSVFile(directory, file)
        candidate = {}
        requests = []

        for sample in samples:
            try:
                if sample[0] == "request":
                    candidate[sample[1]] = RequestTime(sample)
                else:
                    request = candidate.get(sample[1])
                    if request is None:
                        print("Response cannot found!")
                        print(directory + file + "    Index:" + sample[1])
                        print()
                    else:
                        request.AddResult(sample)
                        del candidate[sample[1]]
                    requests.append(request)
            except:
                pass

        return (len(requests), len(candidate), requests)

    @staticmethod
    def DrawTimeInformationEachTestGroup(directory):
        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)

        counter = 1
        test_results = []
        labels = []
        for folder in folders:

            test_path = directory + folder+"/"
            files = FileOperations.GetFiles(test_path)
            TimeInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" not in x]
            if len(TimeInformation) != 0:
                responded_request, candidate_request, requests = CloudAnalysis.ReadTimeInformationFile(test_path,
                                                                                                     TimeInformation[0])

            else:
                Print.AddError("Time information is not found " + test_path)
            if len(requests) > 0:
                # requests = [x for x in requests if hasattr(x, 'Result')]
                print(f"[{counter}/{folder_count}]: Size: {len(requests)} -- {folder}")
                requests.sort(key=lambda x: x.index)
                # header = requests[0].GetHeader()

                values = [x.TotalResponseTime for x in requests if x.Result != "-1"]
                test_results.append(values)
                labels.append(counter)
                # Print.AddError(str(len(values))+";"+test_path)
            else:
                print(f"[{counter}/{folder_count}]: {folder}")

            counter += 1

        write_directory = FileOperations.ProcessedResults + "GroupTimeInfo/"
        test_names = directory.replace('/Full/', "").split('/')
        Charts.BoxPlot(test_results, labels, "Sample number", "Total Time [s]", write_directory,
                       test_names[-2] + "_" + test_names[-1])

   
    @staticmethod
    def CheckAndRemoveAll():
        print("Checking and removing is started!")
        for name in CloudAnalysis.TestTypes:
            print(name)
            CloudAnalysis.CheckAndRemoveDuplicateTests(name+"/")
    @staticmethod
    def CheckAndRemoveDuplicateTests(directory):
        err = False
        foldernames = FileOperations.GetFolderNames(directory)
        folders = []
        for testsample in range(1, 13):
            for testno in range(1, 12):
                testnames = []
                for fn in foldernames:
                    arr = fn.split("__")[2].split("_")
                    if arr[0] == f"TS{testsample:02d}" and arr[1] == str(testno):
                        testnames.append(fn)

                if len(testnames) == 0:
                    print(f"Test Sample {testsample} - Test No {testno} not found!")
                    err = True
                elif len(testnames) > 1:
                    print(f"Test Sample {testsample} - Test No {testno} are duplicated!")
                    testnames.sort()
                    lastname = testnames.pop(-1)
                    for tn in testnames:
                        shutil.rmtree(FileOperations.ResultDirectory+ directory+tn, ignore_errors=True)
                        print("Removed: "+tn)
                    print(lastname)
                    print()
                    err = True
                else:
                    folders.append(testnames[0])
        if err:
            return

    

    @staticmethod
    def AddAllDataToDictionary(directory):
        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)

        counter = 1
        test_results = []
        for folder in folders:
            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)
            TimeInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" not in x]
            if len(TimeInformation) != 0:
                responded_request, candidate_request, requests = CloudAnalysis.ReadTimeInformationFile(test_path,
                                                                                                     TimeInformation[0])

            else:
                Print.AddError("Time information is not found " + test_path)
            if len(requests) > 0:
                print(f"[{counter}/{folder_count}]: Size: {len(requests)} -- {folder}")
                requests.sort(key=lambda x: x.index)

                values = [getattr(x, Configuration.AttributeName) * 1000 for x in requests if x.Result != "-1"][
                         Configuration.StartIndex:Configuration.StartIndex + Configuration.FullDataSize]
                test_results.extend(values)
            else:
                print(f"[{counter}/{folder_count}]: {folder}")

            counter += 1

        test_names = directory.split('/')
        CloudAnalysis.TestResults[test_names[0]] = test_results

    @staticmethod
    def ProcessResourceRecord(record, start_time):
        timestamp = record["timestamp"]
        process_time = timestamp - start_time if start_time is not None else 0
        cpu_usage = record["cpu_percentage"]["total"]["usage"]
        memory_usage = (record["totalmem"] - record["freemem"]) / record["totalmem"] * 100
        total_memory = record["totalmem"]
        rx = record["network_bandwidth"]["RX"]["Bytes"] / 1000 * 8
        tx = record["network_bandwidth"]["TX"]["Bytes"] / 1000 * 8
        bandwidth = rx + tx

        return [timestamp, process_time, cpu_usage, memory_usage, total_memory, rx, tx, bandwidth]

    @staticmethod
    def ReadResourceData(directory, filename=None):
        folders = FileOperations.GetFolderNames(directory)
        folder_count = len(folders)
        # Print.AddError(str(folder_count)+"  :"+directory)
        # return
        counter = 1
        test_results = []
        for folder in folders:
            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)

            ResourceInformation = [x for x in files if
                                   x.endswith('.json') and x.startswith("resource") and (
                                           filename is None or x == filename)]
            if len(ResourceInformation) != 0:
                headers = ['timestamp', 'ProcessTime', 'CPU_Usage', 'Memory_Usage', 'Total_Memory', 'RX', 'TX',
                           'Bandwidth']
                search_index = headers.index(Configuration.AttributeName)
                processed_records = []
                records = FileOperations.ReadJsonFile(test_path, ResourceInformation[0])
                start_time = None
                for record in records:
                    if start_time is None:
                        start_time = record['timestamp']
                    processed_record = CloudAnalysis.ProcessResourceRecord(record, start_time)[search_index]

                    processed_records.append(processed_record)

                if len(processed_records) > 0:
                    print(f"[{counter}/{folder_count}]: Size: {len(processed_records)} -- {folder}")
                    test_results.extend(
                        processed_records[Configuration.ResourceStartIndex:Configuration.ResourceEndIndex])
                else:
                    print(f"[{counter}/{folder_count}]: {folder}")
                counter += 1


            else:
                Print.AddError("Resource information is not found " + test_path)
                counter += 1
        return test_results

    @staticmethod
    def AddAllResourceDataToDictionary():
        for test in CloudAnalysis.TestTypes:
            CloudAnalysis.TestResults[test]=CloudAnalysis.ReadResourceData(test+"/")

    @staticmethod
    def AddArbitrationTimeToDictionary(directory):

        folders = FileOperations.GetFolderNames(directory)

        counter = 1
        test_results = []
        for folder in folders:

            test_path = directory + folder
            files = FileOperations.GetFiles(test_path)
            ThreadInformation = [x for x in files if x.endswith('.csv') and "ThreadInformation" in x]
            if len(ThreadInformation) != 0:
                thread_infos = FileOperations.ReadCSVFile(test_path, ThreadInformation[0])
                thread_started = process_ready = None
                error= False
                for info in thread_infos:
                    if info[0] == "ThreadStarted":
                        thread_started = float(info[1])
                    if info[0] == "ProcessReady":
                        process_ready = float(info[1])
                        break
                    if info[0] =="SocketConnectError":
                        error =True
                        break
                if not error:
                    diff =process_ready - thread_started
                    test_results.append((diff) * 1000)
                    if diff>1:
                        a=1
                else:
                    Print.AddError("Thread information is not found " + test_path)

                counter += 1

        test_names = directory.split('/')
        CloudAnalysis.TestResults[test_names[0]]=test_results


    @staticmethod
    def PlotResponseTime():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Response Time [ms]"
        directory = FileOperations.ProcessedResults + "ResponseTime/"
        filename = "ResponseTime"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim_box=(0,70)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_Mean_SimpleBox",
                                showBoxPlot=True, func=statistics.mean,ylim=ylim_box,labels=CloudAnalysis.TestTypes)

    @staticmethod
    def PlotExecutionTime():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Execution Time [ms]"
        directory = FileOperations.ProcessedResults + "ExecutionTime/"
        filename = "ExecutionTime"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim_box = (0, 7)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_Mean_SimpleBox",
                                showBoxPlot=True, func=statistics.mean, ylim=ylim_box,labels=CloudAnalysis.TestTypes)

    @staticmethod
    def PlotLatencyTime():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Latency [ms]"
        directory = FileOperations.ProcessedResults + "Latency/"
        filename = "Latency"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim_box = (0, 30)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_Mean_SimpleBox",
                                showBoxPlot=True, func=statistics.mean, ylim=ylim_box,labels=CloudAnalysis.TestTypes)

    @staticmethod
    def PlotQueuingDelayTime():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Queuing Delay [ms]"
        directory = FileOperations.ProcessedResults + "QueuingDelay/"
        filename = "QueuingDelay"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim_box = (0,0.3)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_Mean_SimpleBox",
                                showBoxPlot=True, func=statistics.mean,ylim=ylim_box,labels=CloudAnalysis.TestTypes)

    @staticmethod
    def PlotJitter():
        CloudAnalysis.TestResults = {

        }
        y_title = "Jitter [ms]"
        directory = FileOperations.ProcessedResults + "Jitter/"
        filename = "Jitter"

        Configuration.AttributeName = "ResponseTime"

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim = (0, 4)


        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_StdDev_Simple",
                                func=statistics.stdev, ylim=ylim,legend_loc='upper left',labels=CloudAnalysis.TestTypes)
    @staticmethod
    def PlotCPUMemory_Usage():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Usage [%]"
        directory = FileOperations.ProcessedResults + "CPU_Memory_Usage/"
        filename = "CPU_Usage"
        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.AddAllResourceDataToDictionary()
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)
        CPU_Results = CloudAnalysis.TestResults

        CloudAnalysis.TestResults = {

        }
        filename = "Memory_Usage"
        Configuration.AttributeName = filename
        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.AddAllResourceDataToDictionary()
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)
        Memory_Results = CloudAnalysis.TestResults

        filename = "CPU_Memory_Usage"

        ylim_box = (0, 30)

        Charts.CPU_Memory_BoxSimple(CPU_Results, Memory_Results, None, y_title, directory, filename + "_Mean_SimpleBox",
                                showBoxPlot=True, func=statistics.mean, ylim=ylim_box,labels=CloudAnalysis.TestTypes)


    @staticmethod
    def Plot_Bandwidth():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Bandwidth [kbps]"
        directory = FileOperations.ProcessedResults + "Bandwidth/"
        filename = "Bandwidth"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.AddAllResourceDataToDictionary()
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim = (0, 160)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory,
                                          filename + "_Simple_Mean_Box",
                                          showBoxPlot=True, func=statistics.mean,ylim=ylim,labels=CloudAnalysis.TestTypes)

    @staticmethod
    def PlotArbitrationTime():
        CloudAnalysis.TestResults = {

        }
        y_title = "Mean Arbitration Time [ms]"
        directory = FileOperations.ProcessedResults + "ArbitrationTime/"
        filename = "ArbitrationTime"

        Configuration.AttributeName = filename

        if not CloudAnalysis.ReloadTestResult(Configuration.AttributeName):
            CloudAnalysis.CheckFiles(CloudAnalysis.AddArbitrationTimeToDictionary)
            CloudAnalysis.WriteTestResults(Configuration.AttributeName)

        ylim_box = (0,1000)

        Charts.BarChartWithBox(CloudAnalysis.TestResults, None, y_title, directory, filename + "_Mean_SimpleBox",
                                     showBoxPlot=True, func=statistics.mean,ylim=ylim_box,labels=CloudAnalysis.TestTypes)




if __name__ == '__main__':
    #CloudAnalysis.CheckFiles(CloudAnalysis.CheckTimeInformationExists)
    #CloudAnalysis.CheckFiles(CloudAnalysis.CheckThreadInformationExists)
    #CloudAnalysis.CheckFiles(CloudAnalysis.CheckTimeInformationSize)
    #CloudAnalysis.CheckFiles(CloudAnalysis.DrawTimeInformationEachTestGroup)
    #CloudAnalysis.CheckAndRemoveAll()
    #Configuration.AttributeName="CPU_Usage"
    # CloudAnalysis.AddAllResourceDataToDictionary()
    # if not CloudAnalysis.ReloadTestResult():
    #     CloudAnalysis.CheckFiles(CloudAnalysis.AddAllDataToDictionary, short=False)
    #     CloudAnalysis.WriteTestResults()
    CloudAnalysis.PlotLatencyTime()
    CloudAnalysis.PlotExecutionTime()
    CloudAnalysis.PlotQueuingDelayTime()
    CloudAnalysis.PlotResponseTime()
    CloudAnalysis.PlotJitter()
    CloudAnalysis.Plot_Bandwidth()
    CloudAnalysis.PlotArbitrationTime()
    CloudAnalysis.PlotCPUMemory_Usage()

    Print.WriteErrors()
