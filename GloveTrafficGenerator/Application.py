import datetime
import os
import re
import sys
from Config import Configuration


class GloveData:
    def __init__(self, calibration, data):
        self.CalibrationData = calibration
        self.TestData = data
        self.CalibrationLen =len(calibration)
        self.TestDataLen = len(data)


class Sample:
    def __init__(self, data):
        self.Timestamp = float(data[0])
        self.Cycle = int(data[1])
        self.Thumb = int(data[2])
        self.Index = int(data[3])
        self.Middle = int(data[4])
        self.Ring = int(data[5])
        self.Pinkie = int(data[6])
        self.Thumb_y = int(data[7])
        self.Index_y = int(data[8])
        self.Middle_y = int(data[9])
        self.Ring_y = int(data[10])
        self.Pinkie_y = int(data[11])

    def Message(self):
        return f"{self.Thumb};{self.Index};{self.Middle};{self.Ring};{self.Pinkie}"


class GloveAnalysis:
    Calibration_Postfix = "0_Calibration"
    Postfixes = ["1_Single_Thumb", "2_Single_Index", "3_Single_Middle", "4_Single_Ring", "5_Single_Pinkie", "6_Grasp",
                 "7_FourFinger_Grasp", "8_Thumb2Index", "9_Thumb2Middle", "10_Thumb2Ring", "11_Thumb2Pinkie"]
    Base_Directory = "../GloveCloudApplication/FingerPhasePredictor/Data/"
    Data_Directory = ""
    Data = None
    DataLength = 0
    Name = "GloveAnalysis"
    Postfix=""
    TestSubjectId=0
    StartTime=None


    @staticmethod
    def ReadCSVFile(directory, filename=None):
        path = directory + "/" + filename if filename is not None else directory
        with open(path) as file:
            lines = file.readlines()[1:]
            return [re.split(";", x.strip().replace("!", "")) for x in lines]
    @staticmethod
    def ReadAllData():
        GloveAnalysis.FindNextTest()
        print(f"TestSubject: {GloveAnalysis.TestSubjectId} - Postfix: {GloveAnalysis.Postfix}")

        if GloveAnalysis.Postfix!="":
            GloveAnalysis.Data_Directory = GloveAnalysis.Base_Directory+f"TestSubject{GloveAnalysis.TestSubjectId:02d}/"
            cal_data =[Sample(x).Message() for x in GloveAnalysis.ReadCSVFile(GloveAnalysis.Data_Directory,GloveAnalysis.GetTestFileName(GloveAnalysis.Calibration_Postfix))]
            data =[Sample(x).Message() for x in GloveAnalysis.ReadCSVFile(GloveAnalysis.Data_Directory,GloveAnalysis.GetTestFileName(GloveAnalysis.Postfix))]
            GloveAnalysis.Data = GloveData(cal_data,data)


    @staticmethod
    def GetTestFileName(postfix):
        search_key = postfix + ".csv"
        for filename in os.listdir(GloveAnalysis.Data_Directory):
            if filename.endswith(search_key):
                return filename
        return None

    @staticmethod
    def WriteFinishedTest():
        directory = Configuration.FileDirectory + Configuration.ModelName + "/"
        path = directory + "FinishedTest.csv"
        with open(path, "a") as f:
            f.writelines([f"{GloveAnalysis.TestSubjectId};{GloveAnalysis.Postfix};{GloveAnalysis.StartTime};{datetime.datetime.now().timestamp()};{GloveAnalysis.Data.CalibrationLen};{GloveAnalysis.Data.TestDataLen}\n"])
    @staticmethod
    def FindNextTest():
        directory = Configuration.FileDirectory+Configuration.ModelName+"/"
        path = directory+"FinishedTest.csv"
        os.makedirs(directory, exist_ok=True)
        if os.path.exists(path):
            lines = None
            with open(path,"r") as f:
                lines=f.readlines()
            lines.pop(0)
            tests={}
            for line in lines:
                splitted=line.split(";")
                testsubject=int(splitted[0])
                postfix = splitted[1]
                test = tests.get(testsubject,None)
                if test is None:
                    tests[testsubject] = test = []
                test.append(postfix)
            for testsubject in range(1,1+Configuration.TestSubjectCount):
                for postfix in GloveAnalysis.Postfixes:
                    test = tests.get(testsubject,None)
                    if test is None:
                        GloveAnalysis.TestSubjectId = testsubject
                        GloveAnalysis.Postfix = postfix
                        return
                    if postfix not in test:
                        GloveAnalysis.TestSubjectId = testsubject
                        GloveAnalysis.Postfix = postfix
                        return


        else:
            with open(path, "w") as f:
                f.writelines(["testsubject;postfix;starttime;endtime;callen,datalen\n"])
                GloveAnalysis.TestSubjectId=1
                GloveAnalysis.Postfix=GloveAnalysis.Postfixes[0]