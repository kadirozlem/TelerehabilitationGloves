from statistics import mean
from config import Configuration
from FingerPhase import GloveAnalysis
from timeit import default_timer as timer

class Test:
    def __init__(self, name):
        print("Test started for "+name+".")
    @staticmethod
    def ClearModel():
        start = timer()
        GloveAnalysis.ClearModelData()
        end = timer()
        diff = (end -start)*1000
        print("Model and test data cleared at %0.2f ms" % diff)
    @staticmethod
    def Initiate(dataset):
        start = timer()
        glove_dataset= [x.GetGloveData() for x in dataset]
        GloveAnalysis.Initiate(glove_dataset)
        end = timer()
        diff = (end -start)
        print("Model Initialize completed at %0.4f s" % diff)

    def CreateModel(self,name):
        start = timer()
        self.GloveAnalysis = GloveAnalysis(name)
        end = timer()
        diff = (end -start)
        print("Model created at %0.4f s" % diff)

    def Calibrate(self, data):
        total_start = timer()
        durations=[]
        for sample in data.Samples:
            msg = f"1;{sample.Thumb};{sample.Index};{sample.Middle};{sample.Ring};{sample.Pinkie}"
            start = timer()
            self.GloveAnalysis.Predict(msg)
            diff = (timer() -start)*1000
            durations.append(diff)
        total = timer()-total_start
        Test.PrintResult("Calibrate", min(durations),max(durations), mean(durations),total, len(data.Samples))


    def Predict(self, data):
        for test in data:
            total_start = timer()
            durations = []
            results = []
            for sample in test.Samples:
                msg = f"0;{sample.Thumb};{sample.Index};{sample.Middle};{sample.Ring};{sample.Pinkie}"
                start = timer()
                results.append(self.GloveAnalysis.Predict(msg))
                diff = (timer() -start)*1000
                durations.append(diff)
            total = timer()-total_start

            Test.PrintResult("Predict", min(durations),max(durations), mean(durations),total, len(durations))


    @staticmethod
    def PrintResult(name, min, max, average, total, data_count):
        print("%20s" % ("["+name+"]"), end='')
        print("   Max: %4.2f ms" % max, end='')
        print("   Min: %4.2f ms" % min, end='')
        print("   Avg: %4.2f ms" % average, end='')
        print("   Total: %6.2f s" % total, end='')
        print("   DataCount: %6d" % data_count)


def StartTest(name = Configuration.ModelName):
    dataset = GloveAnalysis.ReadData(False)
    if Configuration.ClearModels:
        Test.ClearModel()
    Test.Initiate(dataset)
    for ts_id in range(len(dataset)):
        test_subject = dataset[ts_id]
        (calibration_samples, step_list) = (test_subject.Calibration, test_subject.AllData)
        test = Test(str(ts_id+1))
        test.CreateModel(name)
        test.Calibrate(calibration_samples)
        test.Predict(step_list)


if __name__ == '__main__':
    StartTest()
