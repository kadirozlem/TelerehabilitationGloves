import random
import re
import statistics
from functools import reduce

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
from sklearn import tree, metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from FileOperations import FileOperations
import pickle

from Helper import SectionTime


class Configuration:
    RandomState = 17
    Data ='./Data/'
    PreprocessedData = './PreprocessedData/'
    Model = './Model/'
    Results  = './Results/'
    TestName = 'FinalCloud/'
    SN_Cal_Start =50
    SN_Cal_End = 550
    SN_MinArrSize = 200
    Sample_Distance = 19
    Frequency = 50
    TrainRatio = 0.75
    OnlyMoveFingers=True
    ReloadPreprocessed = True
    BufferCount = 20
    FeatureCount = 23


class MachineLearning:
    Algorithms = {}

    @staticmethod
    def KNN(self):
        return KNeighborsClassifier()


class GloveDataSet:
    class FingerSample:
        def __init__(self, time, finger_x, finger_y):
            self.Time = time
            self.Finger_X = finger_x
            self.Finger_Y = finger_y

    class FingerTests:
        def __init__(self):
            self.Calibration = None
            self.Tests = []

        def Append(self, fingertest):
            if fingertest is not None:
                self.Tests.append(fingertest)

    class GloveTest:
        def __init__(self):
            self.Thumb = None
            self.Index = None
            self.Middle = None
            self.Ring = None
            self.Pinkie = None

    class Sample:
        def __init__(self, data, test):
            self.Test = test
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

        def GetTime(self):
            return self.Timestamp - self.Test.Samples[0].Timestamp

    class Test:
        def __init__(self, data, Thumb=False, Index=False, Middle=False, Ring=False, Pinkie=False, Calibration=False):
            self.Samples = [GloveDataSet.Sample(x, self) for x in data]
            self.Thumb = Thumb
            self.Index = Index
            self.Middle = Middle
            self.Ring = Ring
            self.Pinkie = Pinkie
            self.Calibration = Calibration

        def GetFingerData(self, name):
            test_arr = []
            for x in self.Samples:
                sample_time = x.GetTime()
                finger_x = getattr(x, name)
                finger_y = getattr(x, name + "_y")
                test_arr.append(GloveDataSet.FingerSample(sample_time, finger_x, finger_y))
            return test_arr

        def GetThumb(self, GetAll=not Configuration.OnlyMoveFingers):
            if self.Thumb or GetAll or self.Calibration:
                return self.GetFingerData("Thumb")
            return None

        def GetIndex(self, GetAll=not Configuration.OnlyMoveFingers):
            if self.Index or GetAll or self.Calibration:
                return self.GetFingerData("Index")
            return None

        def GetMiddle(self, GetAll=not Configuration.OnlyMoveFingers):
            if self.Middle or GetAll or self.Calibration:
                return self.GetFingerData("Middle")
            return None

        def GetRing(self, GetAll=not Configuration.OnlyMoveFingers):
            if self.Ring or GetAll or self.Calibration:
                return self.GetFingerData("Ring")
            return None

        def GetPinkie(self, GetAll=not Configuration.OnlyMoveFingers):
            if self.Pinkie or GetAll or self.Calibration:
                return self.GetFingerData("Pinkie")
            return None

    def __init__(self, directory):
        self.Directory = directory
        self.Filenames = self.GetFileNames()
        self.Calibration = GloveDataSet.Test(self.ReadData("0_Calibration"), Calibration=True)
        self.T1_SingleThumb = GloveDataSet.Test(self.ReadData("1_Single_Thumb"), Thumb=True)
        self.T2_SingleIndex = GloveDataSet.Test(self.ReadData("2_Single_Index"), Index=True)
        self.T3_SingleMiddle = GloveDataSet.Test(self.ReadData("3_Single_Middle"), Middle=True)
        self.T4_SingleRing = GloveDataSet.Test(self.ReadData("4_Single_Ring"), Ring=True)
        self.T5_SinglePinkie = GloveDataSet.Test(self.ReadData("5_Single_Pinkie"), Pinkie=True)
        self.T6_Grasp = GloveDataSet.Test(self.ReadData("6_Grasp"), Thumb=True, Index=True, Middle=True, Ring=True,
                                          Pinkie=True)
        self.T7_FourFingerGrasp = GloveDataSet.Test(self.ReadData("7_FourFinger_Grasp"), Index=True, Middle=True,
                                                    Ring=True, Pinkie=True)
        self.T8_Thumb2Index = GloveDataSet.Test(self.ReadData("8_Thumb2Index"), Thumb=True, Index=True)
        self.T9_Thumb2Middle = GloveDataSet.Test(self.ReadData("9_Thumb2Middle"), Thumb=True, Middle=True)
        self.T10_Thumb2Ring = GloveDataSet.Test(self.ReadData("10_Thumb2Ring"), Thumb=True, Ring=True)
        self.T11_Thumb2Pinkie = GloveDataSet.Test(self.ReadData("11_Thumb2Pinkie"), Thumb=True, Pinkie=True)
        self.AllData = [self.T1_SingleThumb,self.T2_SingleIndex, self.T3_SingleMiddle, self.T4_SingleRing, self.T5_SinglePinkie,
                        self.T5_SinglePinkie, self.T6_Grasp, self.T7_FourFingerGrasp, self.T8_Thumb2Index, self.T9_Thumb2Middle,
                        self.T10_Thumb2Ring, self.T11_Thumb2Pinkie]
    def GetFileNames(self):
        return FileOperations.GetFiles(self.Directory)

    def GetTestFileName(self, postfix):
        search_key = postfix + ".csv"
        for filename in self.Filenames:
            if filename.endswith(search_key):
                return filename
        return None

    def ReadData(self, test_postfix):
        filename = self.GetTestFileName(test_postfix)
        if filename is not None:
            return FileOperations.ReadCSVFile(self.Directory, filename)
        else:
            print(f"[ERROR] {test_postfix} is not found in {self.Directory}")
            return None

    def GetFingersData(self, name):
        tests = GloveDataSet.FingerTests()
        tests.Calibration = getattr(self.Calibration, "Get" + name)()
        tests.Append(getattr(self.T1_SingleThumb, "Get" + name)())
        tests.Append(getattr(self.T2_SingleIndex, "Get" + name)())
        tests.Append(getattr(self.T3_SingleMiddle, "Get" + name)())
        tests.Append(getattr(self.T4_SingleRing, "Get" + name)())
        tests.Append(getattr(self.T5_SinglePinkie, "Get" + name)())
        tests.Append(getattr(self.T6_Grasp, "Get" + name)())
        tests.Append(getattr(self.T7_FourFingerGrasp, "Get" + name)())
        tests.Append(getattr(self.T8_Thumb2Index, "Get" + name)())
        tests.Append(getattr(self.T9_Thumb2Middle, "Get" + name)())
        tests.Append(getattr(self.T10_Thumb2Ring, "Get" + name)())
        tests.Append(getattr(self.T11_Thumb2Pinkie, "Get" + name)())
        return tests

    def GetThumb(self):
        return self.GetFingersData("Thumb")

    def GetIndex(self):
        return self.GetFingersData("Index")

    def GetMiddle(self):
        return self.GetFingersData("Middle")

    def GetRing(self):
        return self.GetFingersData("Ring")

    def GetPinkie(self):
        return self.GetFingersData("Pinkie")

    def GetGloveData(self):
        glove = GloveDataSet.GloveTest()
        glove.Thumb = self.GetThumb()
        glove.Index = self.GetIndex()
        glove.Middle = self.GetMiddle()
        glove.Ring = self.GetRing()
        glove.Pinkie = self.GetPinkie()
        return glove


class ButterWorth:
    def __init__(self, N=3, Wn=0.01, init_value=0):
        self.b, self.a = signal.butter(N, Wn)
        self.X = [init_value] * len(self.b)
        self.Y = [init_value] * (len(self.a) - 1)

    def SlideX(self, val):
        self.X.insert(0, val)
        self.X.pop()

    def SlideY(self, val):
        self.Y.insert(0, val)
        self.Y.pop()

    def Calculate(self, val):
        self.SlideX(val)
        sumX = sum([self.X[i] * self.b[i] for i in range(len(self.b))])
        sumY = sum([self.Y[i] * self.a[i + 1] for i in range(len(self.a) - 1)])
        filtered_Y = (sumX - sumY) / self.a[0]
        self.SlideY(filtered_Y)

        return filtered_Y


class StandartNormalizer:
    def __init__(self):
        self.counter = 0
        self.Mean = None
        self.StandardDeviation = None
        self.CalibrationArray = []

    def AddCalibrationValue(self, value):
        self.CalibrationArray.append(value)
        return -1

    def CalculateParameters(self):
        if len(self.CalibrationArray) < Configuration.SN_MinArrSize:
            raise Exception("Calibration error size is not enough!")

        self.Mean = statistics.mean(self.CalibrationArray)
        self.StandardDeviation = statistics.stdev(self.CalibrationArray)
        self.CalibrationArray = None

    def GetValue(self, value):
        if self.Mean is None:
            self.CalculateParameters()

        return (float(value) - self.Mean) / self.StandardDeviation


class FeatureExtraction:
    def __init__(self, distance=Configuration.Sample_Distance):
        self.distance = distance
        self.filter = ButterWorth()
        self.Capacitance = [0] * (self.distance + 1)
        self.Velocity = [0] * (self.distance + 1)
        self.Acceleration = [0] * (self.distance + 1)
        self.Jerk = None
        self.Calibration_Sample_Count = 0
        self.IsNotCalibrated = True

        self.Normalizers = [StandartNormalizer(), StandartNormalizer(), StandartNormalizer(), StandartNormalizer()]

    def Get(self, raw_capacitance):
        # capacitance = self.filter.Calculate(raw_capacitance)
        capacitance = float(raw_capacitance)
        self.Capacitance.insert(0, capacitance)
        self.Capacitance.pop()

        velocity = (self.Capacitance[0] - self.Capacitance[self.distance]) / self.distance * Configuration.Frequency
        self.Velocity.insert(0, velocity)
        self.Velocity.pop()

        acceleration = (self.Velocity[0] - self.Velocity[self.distance]) / self.distance * Configuration.Frequency
        self.Acceleration.insert(0, acceleration)
        self.Acceleration.pop()

        jerk = (self.Acceleration[0] - self.Acceleration[self.distance]) / self.distance * Configuration.Frequency
        self.Jerk = jerk

        return [capacitance, velocity, acceleration, jerk]

    # User side arrange the calibration values.
    def GetNormalizedValue(self, raw_capacitance, cal=False):
        features = self.Get(raw_capacitance)
        normalized_values = []
        self.Calibration_Sample_Count += 1
        for i in range(len(features)):
            if cal:
                if self.Calibration_Sample_Count > Configuration.SN_Cal_Start and self.Calibration_Sample_Count <= Configuration.SN_Cal_End:
                    normalized_values.append(self.Normalizers[i].AddCalibrationValue(features[i]))
            else:
                self.IsNotCalibrated = False
                normalized_values.append(self.Normalizers[i].GetValue(features[i]))
        return np.array(normalized_values)


class FingerPhase:
    FingerName = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinkie']
    Labels = ["Opening", "Open", "Closing", "Close"]

    def __init__(self):
        self.Features = []
        self.Labels = []

    def AddData(self, capacitance, label=None, Calibration=False):
        normalized_features = self.feature_extraction.GetNormalizedValue(capacitance, Calibration)
        if label != 9 and not Calibration:
            self.Features.append(normalized_features)
            self.Labels.append(label)

    def GetFeatures(self, capacitance, calibration=False):
        normalized_features = self.feature_extraction.GetNormalizedValue(capacitance, calibration)
        return normalized_features

    def NewFeatureExtractionObject(self):
        self.feature_extraction = FeatureExtraction()

    def SplitDataSameSize(self, train_index, test_index):
        self.Features = np.array(self.Features)
        self.Labels = np.array(self.Labels)
        self.train_x = self.Features[train_index]
        self.train_y = self.Labels[train_index]
        self.test_x = self.Features[test_index]
        self.test_y = self.Labels[test_index]

    def SplitData(self):
        self.train_x, self.test_x, self.train_y, self.test_y = train_test_split(
            self.Features, self.Labels, train_size=Configuration.TrainRatio, random_state=Configuration.RandomState)


class ML_Models:
    def __init__(self, model,args=None, name=""):
        self.model = model
        self.argument = args
        self.name = name

    def GetModel(self):
        if self.argument is None:
            return self.model()

        return self.model(**self.argument)



class GloveAnalysis:
    ModelNames=["LR", "kNN", "DT","MLP", "RF", "XGB"]
    ResultDirectory=Configuration.Results + Configuration.TestName

    def __init__(self,name):
        self.CreateEnvironments()
        self.FeatureExtractions=[FeatureExtraction() for x in range(0,5)]
        self.Models = GloveAnalysis.LoadModels(name)

    def Predict(self, data):
        data_splitted = data.split(";")
        cal = int(re.sub("[^0-9]", "", data_splitted[0])) and self.FeatureExtractions[0].IsNotCalibrated
        raw_caps = [int(re.sub("[^0-9]", "", data_splitted[x])) for x in range(1,6)]

        postfix = ";" + data_splitted[6] if len(data_splitted) > 6 else ""

        results = []
        for i in range(5):
            features = self.FeatureExtractions[i].GetNormalizedValue(raw_caps[i],cal)

            if cal:
                results.append("-1")
            else:
                test_predict = self.Models[i].predict([features])
                results.append(str(test_predict[0]))
        return ";".join(results)+postfix
    @staticmethod
    def Initiate(dataset=None):
        GloveAnalysis.CreateEnvironments()
        if not GloveAnalysis.CheckModels():
            GloveAnalysis.Train(dataset)
            

    @staticmethod
    def LoadModels(name):
        finger_models=[]
        for fingerid in range(1, 6):
            path = GloveAnalysis.GetModelPath(modelname=name, fingerid=str(fingerid))
            with open(path, 'rb') as inp:
                finger_models.append(pickle.load(inp))
        return finger_models


    @staticmethod
    def ClearModelData():
        FileOperations.RemoveDirectory(Configuration.Model)
        FileOperations.CreateFolderIfNotExists(Configuration.Model)
        for model in GloveAnalysis.ModelNames:
            FileOperations.CreateFolderIfNotExists(Configuration.Model + model)

    @staticmethod
    def Train(dataset=None):
        if Configuration.ReloadPreprocessed:
            FileOperations.RemoveDirectory(Configuration.PreprocessedData)

        fingers = GloveAnalysis.LoadPreprocessedData()
        if fingers is None:
            if dataset is None:
                dataset = GloveAnalysis.ReadData()
            fingers = GloveAnalysis.Preprocess(dataset)

        GloveAnalysis.SplitData(fingers)

        GloveAnalysis.TrainAllModels(fingers)




    @staticmethod
    def CheckModels():
        for model_name in GloveAnalysis.ModelNames:
            for fingerid in range(1,6):
                if not FileOperations.FileIsExists(GloveAnalysis.GetModelPath(model_name, fingerid)):
                    return False
        return True
    @staticmethod
    def CreateEnvironments():
        FileOperations.CreateFolderIfNotExists(Configuration.Results)

        FileOperations.CreateFolderIfNotExists(Configuration.Model)
        for model in GloveAnalysis.ModelNames:
            FileOperations.CreateFolderIfNotExists(Configuration.Model+model)

    @staticmethod
    def TrainAllModels(fingers):
        models = [
            ML_Models(LogisticRegression,args=dict(C=100), name= "LR"),
            ML_Models(KNeighborsClassifier,args=dict(n_neighbors=20),name= "kNN"),
            ML_Models(tree.DecisionTreeClassifier,args=dict(min_samples_split=8), name="DT"),
            ML_Models(MLPClassifier,args=dict(activation="tanh"), name="MLP"),
            ML_Models(RandomForestClassifier,args=dict(n_estimators=10),name= "RF"),
            ML_Models(xgb.XGBClassifier,args=dict(n_estimators=25,max_depth=18, learning_rate=0.1, subsample=1),name= "XGB")
        ]


        for model in models:
            print(model.name)
            GloveAnalysis.MachineLearning(fingers,model, SaveOnlyResults=False)

    @staticmethod
    def ReadData(FingerSplitted=True):
        TestFolders = FileOperations.GetDirectoryNames(Configuration.Data)
        test_dataset = []
        print("Read Operation Started!")
        for directory in TestFolders:
            test_subject = GloveDataSet(Configuration.Data + directory)
            if FingerSplitted:
                test_subject=test_subject.GetGloveData()
            test_dataset.append(test_subject)
            print(directory + " is read!")
        return test_dataset

    @staticmethod
    def GetModelPath(modelname, fingerid):
        return f"{Configuration.Model}{modelname}/{modelname}_Finger{fingerid}"

    @staticmethod
    def ProcessFinger(fingerPhase, fingertests):
        fingerPhase.NewFeatureExtractionObject()
        # calibration
        for sample in fingertests.Calibration:
            fingerPhase.AddData(sample.Finger_X, sample.Finger_Y, Calibration=True)

        # FeatureExtractrion
        for test in fingertests.Tests:
            for sample in test:
                fingerPhase.AddData(sample.Finger_X, sample.Finger_Y)

    @staticmethod
    def LoadPreprocessedData():
        if FileOperations.FileIsExists(Configuration.PreprocessedData):
            fingers = []
            for i in range(5):
                with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'rb') as inp:
                    fingers.append(pickle.load(inp))
            return fingers
        return None

    @staticmethod
    def Preprocess(dataset):
        if FileOperations.FileIsExists(Configuration.PreprocessedData):
            fingers = []
            for i in range(5):
                with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'rb') as inp:
                    fingers.append(pickle.load(inp))
            return fingers

        fingers = [FingerPhase(), FingerPhase(), FingerPhase(), FingerPhase(), FingerPhase()]
        print()
        print()
        print("Preprocess is started!")
        counter = 0
        for test_subject in dataset:
            counter += 1
            print(str(counter))
            GloveAnalysis.ProcessFinger(fingers[0], test_subject.Thumb)
            GloveAnalysis.ProcessFinger(fingers[1], test_subject.Index)
            GloveAnalysis.ProcessFinger(fingers[2], test_subject.Middle)
            GloveAnalysis.ProcessFinger(fingers[3], test_subject.Ring)
            GloveAnalysis.ProcessFinger(fingers[4], test_subject.Pinkie)
        FileOperations.CreateFolder(Configuration.PreprocessedData)

        for i in range(5):
            with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'wb') as outp:
                pickle.dump(fingers[i], outp, pickle.HIGHEST_PROTOCOL)
        return fingers

    
    @staticmethod
    def SplitData(fingers, same_size=False):
        if same_size:
            random.seed(Configuration.RandomState)
            size = len(fingers[0].Features)
            train_size = int(size * Configuration.TrainRatio)
            indexes = [x for x in range(0, size)]
            random.shuffle(indexes)
            train_index = indexes[0:train_size - 1]
            test_index = indexes[train_size:]
            [x.SplitDataSameSize(train_index, test_index) for x in fingers]
        else:
            [x.SplitData() for x in fingers]

    @staticmethod
    def MachineLearning(fingers, model, SaveOnlyResults=False):
        models_available =True
        for i in range(1,6):
            path = GloveAnalysis.GetModelPath(model.name, i)
            if not FileOperations.FileIsExists(path):
                models_available=False
        if models_available:
            return

        index = 0
        true_arr = []
        predicted_arr = []
        train_size_arr = []
        train_time_arr = []
        test_time_arr = []
        for finger in fingers:
            path = GloveAnalysis.GetModelPath(model.name, index+1)
            FileOperations.RemoveFile(path)
            clf = model.GetModel()
            SectionTime.start("model_train")
            clf = clf.fit(finger.train_x, finger.train_y)
            train_time = SectionTime.end("model_train", response=True)
            SectionTime.start("model_test")
            predicted = clf.predict(finger.test_x)
            test_time = SectionTime.end("model_test", response=True)

            train_size = len(finger.train_y)
            GloveAnalysis.CalculateFingerMetrics(model.name, index, finger.test_y, predicted, train_size, train_time, test_time,
                                        SaveOnlyResults)

            true_arr.append(finger.test_y)
            predicted_arr.append(predicted)
            train_size_arr.append(len(finger.train_y))
            train_time_arr.append(train_time)
            test_time_arr.append(test_time)
            GloveAnalysis.SaveModel(model.name,index+1,clf)
            index += 1

        GloveAnalysis.CalculateGloveMetrics(model.name, true_arr, predicted_arr, train_size_arr, train_time_arr, test_time_arr,
                                   SaveOnlyResults)

    @staticmethod
    def SaveModel(modelname, finger_id, model):
        path = GloveAnalysis.GetModelPath(modelname, finger_id)
        with open(path, 'wb') as outp:
            pickle.dump(model, outp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def CalculateFingerMetrics(name, finger_index, true, predicted, train_size, train_time, test_time,
                               SaveOnlyResults=False):
        accuracy = metrics.accuracy_score(true, predicted)
        precision = metrics.precision_score(true, predicted, average="macro")
        recall = metrics.recall_score(true, predicted, average="macro")
        f1score = metrics.f1_score(true, predicted, average="macro")
        confusion_matrix = metrics.confusion_matrix(true, predicted)
        msg = ""
        filename = FingerPhase.FingerName[finger_index]
        if not FileOperations.FileIsExists(GloveAnalysis.ResultDirectory, filename + "_Results.csv"):
            msg = "method;accuracy;precision;recall;f1score;train_size;train_time[s];avg_train_time[ms];test_size;test_time[s];avg_test_time[ms]\n"
        msg += f"{name};{accuracy};{precision};{recall};{f1score};{train_size};{train_time:.2f};{train_time / train_size * 1000:.2f};{len(true)};{test_time:.2f};{test_time / len(true) * 1000:.2f}\n"
        FileOperations.WriteLines(GloveAnalysis.ResultDirectory +"Fingers/"+ filename + "/", name+"_"+filename + "_Results.csv", msg)
        if not SaveOnlyResults:
            GloveAnalysis.SaveConfusionMatrix(confusion_matrix, GloveAnalysis.ResultDirectory +"Fingers/"+ filename + "/", name+"_"+filename)
            GloveAnalysis.SaveConfusionMatrix(confusion_matrix, GloveAnalysis.ResultDirectory + "Models/"+name + "/", filename+"_"+name)

            FileOperations.WriteDataToCSV(list(zip(true, predicted)), ["True", "Predicted"],
                                          GloveAnalysis.ResultDirectory + filename + "/", name + "_values", )

        print(name + " - " + filename + " accuracy: " + str(accuracy))

    @staticmethod
    def SaveConfusionMatrix(confusion_matrix, directory, name):
        FileOperations.CreateFolderIfNotExists(directory)
        cmd = ConfusionMatrixDisplay(confusion_matrix, display_labels=FingerPhase.Labels)
        cmd.plot().figure_.savefig(directory + name + ".png", bbox_inches='tight')
        cmd.plot().figure_.savefig(directory + name + ".pdf", bbox_inches='tight')
        plt.clf()
        plt.close("all")

    @staticmethod
    def CalculateGloveMetrics(name, true_arr, predicted_arr, train_size_arr, train_time_arr, test_time_arr,
                              SaveOnlyResults=False):
        true = reduce(lambda a, b: a + b, true_arr)
        predicted = reduce(lambda a, b: list(a) + list(b), predicted_arr)
        train_size = sum(train_size_arr)
        train_time = sum(train_time_arr)
        test_time = sum(test_time_arr)

        accuracy = metrics.accuracy_score(true, predicted)
        precision = metrics.precision_score(true, predicted, average="macro")
        recall = metrics.recall_score(true, predicted, average="macro")
        f1score = metrics.f1_score(true, predicted, average="macro")
        confusion_matrix = metrics.confusion_matrix(true, predicted)
        msg = ""
        filename = "OverAll"
        if not FileOperations.FileIsExists(GloveAnalysis.ResultDirectory, filename + "_Results.csv"):
            msg = "method;accuracy;precision;recall;f1score;train_size;train_time[s];avg_train_time[ms];test_size;test_time[s];avg_test_time[ms]\n"
        msg += f"{name};{accuracy};{precision};{recall};{f1score};{train_size};{train_time:.2f};{train_time / train_size * 1000:.2f};{len(true)};{test_time:.2f};{test_time / len(true) * 1000:.2f}\n"
        FileOperations.WriteLines(GloveAnalysis.ResultDirectory, filename + "_Results.csv", msg)
        if not SaveOnlyResults:
            GloveAnalysis.SaveConfusionMatrix(confusion_matrix, GloveAnalysis.ResultDirectory + filename + "/", name)
        print(name + " - " + filename + " accuracy: " + str(accuracy))