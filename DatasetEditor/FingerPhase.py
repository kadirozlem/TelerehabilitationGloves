import random
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
#import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from Configuration import Configuration
from FileOperations import FileOperations
import pickle

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
    def __init__(self,N=3, Wn=0.01, init_value = 0):
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
    Labels = ["Opening", "Opened", "Closing", "Closed"]

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
    def __init__(self, model, name):
        self.model = model
        self.name = name


class GloveAnalysis:

    def __init__(self):
        self.CreateEnvironments()

        if Configuration.ReloadPreprocessed:
            FileOperations.RemoveDirectory(Configuration.PreprocessedData)

        SectionTime.start("LoadData")
        loaded = self.LoadPreprocessedData()
        SectionTime.end("LoadData", True)
        if not loaded:
            SectionTime.start("ReadData")
            self.dataset = self.ReadData()
            SectionTime.end("ReadData", True)
            SectionTime.start("Preprocess")
            self.Preprocess()
            SectionTime.end("Preprocess", True)

        SectionTime.start("Train")
        self.Train()
        SectionTime.end("Train", True)

    def CreateEnvironments(self):
        self.result_directory = Configuration.Results + Configuration.TestName
        FileOperations.CreateFolderIfNotExists(Configuration.Results)

    def Train(self):
        SectionTime.start("SplitData")
        self.SplitData()
        SectionTime.end("SplitData", True)

        self.TrainAllModels()
        #self.MLPTuning()
        # self.KNNTuning()
        #self.LRTuning()
        # self.DTTuning()
        #self.RFTuning()
        #self.XGBoostTuning()

    def TrainAllModels(self):
        models = [
            #ML_Models(LogisticRegression(C=100), "LR"),
            #ML_Models(KNeighborsClassifier(20), "kNN"),
            ML_Models(tree.DecisionTreeClassifier(min_samples_split=8), "DT"),
            #ML_Models(MLPClassifier(activation="tanh"), "MLP"),

            #ML_Models(RandomForestClassifier(max_depth=16), "RF"),
            #ML_Models(xgb.XGBClassifier(max_depth=12, learning_rate=0.1, subsample=0.7), "XGB")
        ]

        self.result_directory = Configuration.Results + Configuration.TestName
        SectionTime.start("MachineLearning")

        for model in models:
            print(model.name)
            self.MachineLearning(model.model, name=model.name, SaveOnlyResults=True)

        SectionTime.end("MachineLearning", True)

    def KNNTuning(self):
        self.result_directory = Configuration.Results + "KNN/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        numbers = [2, 3, 4, 5] + list(range(5, 101, 5))
        for i in numbers:
            SectionTime.start("MachineLearning")
            print("KNN: " + str(i))
            self.MachineLearning(KNeighborsClassifier(i), "KNN_" + str(i),SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
    def MLPTuning(self):
        self.result_directory = Configuration.Results + "MLP/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        # SectionTime.start("MachineLearning")
        # name = f"MLP__default"
        # print(name)
        # self.MachineLearning(MLPClassifier(), name,
        #                      SaveOnlyResults=True)
        # SectionTime.end("MachineLearning", True)


        parameters = {
                    'hidden_layer_sizes' : [(20,),(40,),(60,),(80),(100,),(150),(50,100),(50,75,100)],
                    "activation":['identity', 'logistic', 'tanh', 'relu'],
                    'solver':['lbfgs', 'sgd', 'adam'],
                    'learning_rate': ['constant', 'adaptive', 'invscaling']}

        for hidden_layer_sizes in parameters['hidden_layer_sizes']:
            SectionTime.start("MachineLearning")
            name = f"MLP__HL_{hidden_layer_sizes}"
            print(name)
            self.MachineLearning(
                MLPClassifier(hidden_layer_sizes=hidden_layer_sizes), name,
                SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for activation in parameters['activation']:
            SectionTime.start("MachineLearning")
            name = f"MLP__A_{activation}"
            print(name)
            self.MachineLearning(
                MLPClassifier(activation=activation), name,
                SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for solver in parameters['solver']:
            SectionTime.start("MachineLearning")
            name = f"MLP__S_{solver}"
            print(name)
            self.MachineLearning(
                MLPClassifier(solver=solver), name,
                SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        
        for learning_rate in parameters['learning_rate']:
            SectionTime.start("MachineLearning")
            name = f"MLP__L_{learning_rate}"
            print(name)
            self.MachineLearning(MLPClassifier(learning_rate=learning_rate  ), name,
                                 SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)

    def LRTuning(self):
        self.result_directory = Configuration.Results + "LR2/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        SectionTime.start("MachineLearning")
        name = f"LR__S_newton_cg__P_None__C_100"
        print(name)
        try:
            self.MachineLearning(LogisticRegression(solver='newton-cg', penalty='none', C=100), name,
                                 SaveOnlyResults=True)
        except:
            pass
        SectionTime.end("MachineLearning", True)
        return

        parameters = {'penalty' : ['l1', 'l2', 'elasticnet', 'none'],
                        'C' : np.logspace(-4, 4, 25),
                        'solver' : ['lbfgs','newton-cg','liblinear','sag','saga'],
                        'max_iter' : [100, 1000, 5000]
                        }
        for C in parameters['C']:
            SectionTime.start("MachineLearning")
            name = f"LR__CI_{C}"
            print(name)
            try:
                self.MachineLearning(LogisticRegression(C=C), name,
                                     SaveOnlyResults=True)
            except:
                pass
            SectionTime.end("MachineLearning", True)
        for max_iter in parameters['max_iter']:
            SectionTime.start("MachineLearning")
            name = f"LR__MI_{max_iter}"
            print(name)
            try:
                self.MachineLearning(LogisticRegression(max_iter=max_iter), name,
                                     SaveOnlyResults=True)
            except:
                pass
            SectionTime.end("MachineLearning", True)
        for penalty in parameters['penalty']:
            for solver in parameters['solver']:
                    SectionTime.start("MachineLearning")
                    name = f"LR__P_{penalty}__S_{solver}"
                    print(name)
                    try:
                        self.MachineLearning(LogisticRegression(penalty=penalty,solver=solver), name,
                                         SaveOnlyResults=True)
                    except:
                        pass
                    SectionTime.end("MachineLearning", True)


    def DTTuning(self):
        self.result_directory = Configuration.Results + "DT/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        parameters = {'criterion': ['gini', 'entropy'],
                      'max_depth': [None]+np.arange(2, 21).tolist()[0::5],
                      'min_samples_split':np.arange(2, 11).tolist()[0::2],
                      'max_leaf_nodes': [None]+np.arange(3, 26).tolist()[0::5]}

        for criterion in parameters['criterion']:
            for max_depth in parameters['max_depth']:
                for min_samples_split in parameters['min_samples_split']:
                    for max_leaf_nodes in parameters['max_leaf_nodes']:
                        SectionTime.start("MachineLearning")
                        name = f"DT__C_{criterion}__MD_{max_depth}__MSS_{min_samples_split}__MLN_{max_leaf_nodes}"
                        print(name)
                        self.MachineLearning(tree.DecisionTreeClassifier(criterion=criterion, max_depth=max_depth,
                                                                         min_samples_split=min_samples_split,
                                                                         max_leaf_nodes=max_leaf_nodes), name,SaveOnlyResults=True)
                        SectionTime.end("MachineLearning", True)

    def RFTuning(self):
        self.result_directory = Configuration.Results + "RF4/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        name = f"DT__MD_16__N_75__MSS_10"
        print(name)
        self.MachineLearning(
            RandomForestClassifier(max_depth=16, n_estimators=75,min_samples_split=10), name, SaveOnlyResults=True)



        return
        SectionTime.start("MachineLearning")
        print("RF_Default")
        self.MachineLearning(
            RandomForestClassifier(), "RF_Default", SaveOnlyResults=True)
        SectionTime.end("MachineLearning", True)



        parameters = {'n_estimators': [25, 50, 75, 100, 125, 150],
                      'max_features': ['sqrt', 'log2', None],
                      'criterion': ['gini', 'entropy'],
                      'max_depth': [None]+np.arange(2, 21).tolist()[0::2],
                      'min_samples_split':np.arange(2, 11).tolist()[0::2],
                      'max_leaf_nodes': [None]+np.arange(3, 26).tolist()[0::2]}

        for n_estimators in parameters['n_estimators']:
            SectionTime.start("MachineLearning")
            name = f"DT__N_{n_estimators}"
            print(name)
            self.MachineLearning(
                RandomForestClassifier(n_estimators=n_estimators), name, SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for max_features in parameters['max_features']:
            SectionTime.start("MachineLearning")
            name = f"DT__MF_{max_features}"
            print(name)
            self.MachineLearning(
                RandomForestClassifier(max_features=max_features), name, SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)

        for criterion in parameters['criterion']:
            SectionTime.start("MachineLearning")
            name = f"DT__C_{criterion}"
            print(name)
            self.MachineLearning(
                RandomForestClassifier(criterion=criterion
                                       ), name, SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for max_depth in parameters['max_depth']:
            SectionTime.start("MachineLearning")
            name = f"DT__MD_{max_depth}"
            print(name)
            self.MachineLearning(
                RandomForestClassifier(
                                       max_depth=max_depth
                                       ), name, SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for min_samples_split in parameters['min_samples_split']:
            SectionTime.start("MachineLearning")
            name = f"DT__MSS_{min_samples_split}"
            print(name)
            self.MachineLearning(
                RandomForestClassifier(min_samples_split=min_samples_split
                                       ), name, SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)
        for max_leaf_nodes in parameters['max_leaf_nodes']:
            SectionTime.start("MachineLearning")
            name = f"DT__MLN_{max_leaf_nodes}"
            print(name)
            self.MachineLearning(RandomForestClassifier( max_leaf_nodes=max_leaf_nodes), name,SaveOnlyResults=True)
            SectionTime.end("MachineLearning", True)

    def XGBoostTuning(self):
        self.result_directory = Configuration.Results + "XGBoost/"
        FileOperations.CreateFolderIfNotExists(self.result_directory)

        SectionTime.start("MachineLearning")
        name = f"XGB__Default"
        print(name)
        self.MachineLearning(xgb.XGBClassifier(),
                             name,
                             SaveOnlyResults=True)
        SectionTime.end("MachineLearning", True)


        parameters = {'max_depth': [None]+np.arange(3, 22).tolist()[0::3],
                    'learning_rate': [0.1, 0.01, 0.001],
                    'subsample': [0.5, 0.7, 1]}

        for max_depth in parameters['max_depth']:
            for learning_rate in parameters['learning_rate']:
                for subsample in parameters['subsample']:
                    SectionTime.start("MachineLearning")
                    name = f"XGB__MD_{max_depth}__LR_{learning_rate}__SS_{subsample}"
                    print(name)
                    self.MachineLearning(xgb.XGBClassifier(max_depth=max_depth,learning_rate=learning_rate,subsample=subsample), name,
                                         SaveOnlyResults=True)
                    SectionTime.end("MachineLearning", True)


    def ReadData(self):
        TestFolders = FileOperations.GetDirectoryNames(Configuration.Data)
        test_dataset = []
        print("Read Operation Started!")
        for directory in TestFolders:
            test_subject = GloveDataSet(Configuration.Data + directory).GetGloveData()
            test_dataset.append(test_subject)
            print(directory + " is read!")
        return test_dataset

    def ProcessFinger(self, fingerPhase, fingertests):
        fingerPhase.NewFeatureExtractionObject()
        # calibration
        for sample in fingertests.Calibration:
            fingerPhase.AddData(sample.Finger_X, sample.Finger_Y, Calibration=True)

        # FeatureExtractrion
        for test in fingertests.Tests:
            for sample in test:
                fingerPhase.AddData(sample.Finger_X, sample.Finger_Y)

    def LoadPreprocessedData(self):
        if FileOperations.FileIsExists(Configuration.PreprocessedData):
            self.fingers = []
            for i in range(5):
                with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'rb') as inp:
                    self.fingers.append(pickle.load(inp))
            return True
        return False

    def Preprocess(self):
        if FileOperations.FileIsExists(Configuration.PreprocessedData):
            self.fingers = []
            for i in range(5):
                with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'rb') as inp:
                    self.fingers.append(pickle.load(inp))
            return

        self.fingers = [FingerPhase(), FingerPhase(), FingerPhase(), FingerPhase(), FingerPhase()]
        print()
        print()
        print("Preprocess is started!")
        counter = 0
        for test_subject in self.dataset:
            counter += 1
            print(str(counter))
            self.ProcessFinger(self.fingers[0], test_subject.Thumb)
            self.ProcessFinger(self.fingers[1], test_subject.Index)
            self.ProcessFinger(self.fingers[2], test_subject.Middle)
            self.ProcessFinger(self.fingers[3], test_subject.Ring)
            self.ProcessFinger(self.fingers[4], test_subject.Pinkie)
        FileOperations.CreateFolder(Configuration.PreprocessedData)

        for i in range(5):
            with open(Configuration.PreprocessedData + "Finger" + str(i + 1), 'wb') as outp:
                pickle.dump(self.fingers[i], outp, pickle.HIGHEST_PROTOCOL)

    def Predict(self):
        pass

    def SplitData(self, same_size=False):
        if same_size:
            random.seed(Configuration.RandomState)
            size = len(self.fingers[0].Features)
            train_size = int(size * Configuration.TrainRatio)
            indexes = [x for x in range(0, size)]
            random.shuffle(indexes)
            train_index = indexes[0:train_size - 1]
            test_index = indexes[train_size:]
            [x.SplitDataSameSize(train_index, test_index) for x in self.fingers]
        else:
            [x.SplitData() for x in self.fingers]

    def MachineLearning(self, model=tree.DecisionTreeClassifier(), name="DecisionTree", SaveOnlyResults=False):
        index = 0
        true_arr = []
        predicted_arr = []
        train_size_arr = []
        train_time_arr = []
        test_time_arr = []
        for finger in self.fingers:
            clf = model
            SectionTime.start("model_train")
            clf = clf.fit(finger.train_x, finger.train_y)
            train_time = SectionTime.end("model_train", response=True)
            SectionTime.start("model_test")
            predicted = clf.predict(finger.test_x)
            test_time = SectionTime.end("model_test", response=True)

            train_size = len(finger.train_y)
            self.CalculateFingerMetrics(name, index, finger.test_y, predicted, train_size, train_time, test_time,SaveOnlyResults)

            true_arr.append(finger.test_y)
            predicted_arr.append(predicted)
            train_size_arr.append(len(finger.train_y))
            train_time_arr.append(train_time)
            test_time_arr.append(test_time)

            index += 1
        self.CalculateGloveMetrics(name, true_arr, predicted_arr, train_size_arr, train_time_arr, test_time_arr,SaveOnlyResults)

    def CalculateFingerMetrics(self, name, finger_index, true, predicted, train_size, train_time, test_time,SaveOnlyResults =False):
        accuracy = metrics.accuracy_score(true, predicted)
        precision = metrics.precision_score(true, predicted, average="macro")
        recall = metrics.recall_score(true, predicted, average="macro")
        f1score = metrics.f1_score(true, predicted, average="macro")
        confusion_matrix = metrics.confusion_matrix(true, predicted)
        msg = ""
        filename = FingerPhase.FingerName[finger_index]
        if not FileOperations.FileIsExists(self.result_directory, filename + "_Results.csv"):
            msg = "method;accuracy;precision;recall;f1score;train_size;train_time[s];avg_train_time[ms];test_size;test_time[s];avg_test_time[ms]\n"
        msg += f"{name};{accuracy};{precision};{recall};{f1score};{train_size};{train_time:.2f};{train_time / train_size * 1000:.2f};{len(true)};{test_time:.2f};{test_time / len(true) * 1000:.2f}\n"
        FileOperations.WriteLines(self.result_directory, filename + "_Results.csv", msg)
        if not SaveOnlyResults:
            self.SaveConfusionMatrix(confusion_matrix, self.result_directory + filename + "/", name)

            FileOperations.WriteDataToCSV(list(zip(true, predicted)), ["True", "Predicted"],
                                          self.result_directory + filename + "/", name + "_values", )

        print(name + " - " + filename + " accuracy: " + str(accuracy))

    def SaveConfusionMatrix(self, confusion_matrix, directory, name):
        FileOperations.CreateFolderIfNotExists(directory)
        cmd = ConfusionMatrixDisplay(confusion_matrix, display_labels=FingerPhase.Labels)
        cmd.plot().figure_.savefig(directory + name + ".png", bbox_inches='tight')
        cmd.plot().figure_.savefig(directory + name + ".pdf", bbox_inches='tight')
        plt.clf()
        plt.close("all")

    def CalculateGloveMetrics(self, name, true_arr, predicted_arr, train_size_arr, train_time_arr, test_time_arr, SaveOnlyResults=False):
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
        if not FileOperations.FileIsExists(self.result_directory, filename + "_Results.csv"):
            msg = "method;accuracy;precision;recall;f1score;train_size;train_time[s];avg_train_time[ms];test_size;test_time[s];avg_test_time[ms]\n"
        msg += f"{name};{accuracy};{precision};{recall};{f1score};{train_size};{train_time:.2f};{train_time / train_size * 1000:.2f};{len(true)};{test_time:.2f};{test_time / len(true) * 1000:.2f}\n"
        FileOperations.WriteLines(self.result_directory, filename + "_Results.csv", msg)
        if not SaveOnlyResults:
            self.SaveConfusionMatrix(confusion_matrix, self.result_directory + filename + "/", name)
        print(name + " - " + filename + " accuracy: " + str(accuracy))
