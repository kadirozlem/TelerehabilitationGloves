import os
import re
import numpy as np
from sklearn import metrics

from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

FingerNames = ["Thumb", "Index", "Middle", "Ring", "Pinkie"]
ModelNames = ["LR", "DT", "kNN", "MLP", "RF", "XGB"]
Labels = ["Opening", "Open", "Closing", "Close"]


def ReadCSVFile(directory, filename):
    with open(directory + "/" + filename) as file:
        lines = file.readlines()
        return [re.split(";|:", x) for x in lines]


def SaveConfusionMatrix(confusion_matrix, directory, name):
    os.makedirs(directory, exist_ok=True)
    cmd = ConfusionMatrixDisplay(confusion_matrix, display_labels=Labels)
    cmd.plot(values_format='').figure_.savefig(directory + name + ".png", bbox_inches='tight')
    cmd.plot(values_format='').figure_.savefig(directory + name + ".pdf", bbox_inches='tight')
    plt.clf()
    plt.close("all")


class FingerMetrics():
    def __init__(self, fingername, arr=None, true=[], predicted=[]):
        self.fingername = fingername
        if arr is None:
            self.accuracy = metrics.accuracy_score(true, predicted) * 100
            self.precision = metrics.precision_score(true, predicted, average="macro") * 100
            self.recall = metrics.recall_score(true, predicted, average="macro") * 100
            self.f1score = metrics.f1_score(true, predicted, average="macro") * 100
        else:
            self.accuracy = np.mean([x.accuracy for x in arr])
            self.precision = np.mean([x.precision for x in arr])
            self.recall = np.mean([x.recall for x in arr])
            self.f1score = np.mean([x.f1score for x in arr])
        self.Print()

    def Print(self):
        print(f"Accuracy: {self.accuracy:.2f}, Precision: {self.precision:.2f}, Recall: {self.recall:.2f}")


class GloveMetrics:
    def __init__(self, modelname):
        self.modelname = modelname
        print(modelname)

    def CalculateThumb(self, true, predicted):
        self.Thumb = FingerMetrics("Thumb", true=true, predicted=predicted)

    def CalculateIndex(self, true, predicted):
        self.Index = FingerMetrics("Index", true=true, predicted=predicted)

    def CalculateMiddle(self, true, predicted):
        self.Middle = FingerMetrics("Middle", true=true, predicted=predicted)

    def CalculateRing(self, true, predicted):
        self.Ring = FingerMetrics("Ring", true=true, predicted=predicted)

    def CalculatePinkie(self, true, predicted):
        self.Pinkie = FingerMetrics("Pinkie", true=true, predicted=predicted)

    def CalculateOverall(self):
        self.Overall = FingerMetrics("Overall", arr=[self.Thumb, self.Index, self.Middle, self.Ring, self.Pinkie])

    def SaveResults(self):
        directory = './ConfusionMatrix/'
        os.makedirs(directory, exist_ok=True)
        path = directory+'ArticleResults.csv'
        results = f"{self.modelname};{self.Thumb.f1score};{self.Index.f1score};{self.Middle.f1score};{self.Ring.f1score};{self.Pinkie.f1score};{self.Overall.accuracy};{self.Overall.recall};{self.Overall.precision};{self.Overall.f1score}\n"

        if not os.path.exists(path):
            with open(path, "w") as file:
                header = "Classifier;Thumb;Index;Middle;Ring;Pinkie;Accuracy;Recall;Precision;F1Score\n"
                file.write(header)
                file.write(results)
        else:
            with open(path, "a") as file:
                file.write(results)



def CreateConfusionMatrices():
    Directory = './ConfusionMatrix/'
    Models = {}
    for model in ModelNames:
        overall_true = []
        overall_pred = []
        glovemetrics = GloveMetrics(model)
        for Finger in FingerNames:
            samples = ReadCSVFile(Finger, model + '_values.csv')[1:]
            true_vals = [int(x[1]) for x in samples]
            pred_vals = [int(x[2]) for x in samples]
            overall_true.extend(true_vals)
            overall_pred.extend(pred_vals)
            getattr(glovemetrics, "Calculate" + Finger)(true_vals, pred_vals)

            confmat = confusion_matrix(true_vals, pred_vals)
            SaveConfusionMatrix(confmat,Directory+'Models/'+model+'/',model+'_'+Finger)
            SaveConfusionMatrix(confmat,Directory+'Fingers/'+Finger+'/',model+'_'+Finger)
        glovemetrics.CalculateOverall()
        glovemetrics.SaveResults()
        confmat = confusion_matrix(overall_true, overall_pred)
        SaveConfusionMatrix(confmat, Directory +'Models/'+ model + '/', model + '_Overall')
        SaveConfusionMatrix(confmat, Directory +'Fingers/'+'Overall' + '/', model + '_Overall')

    def CalculateFingerMetrics(name, fingername, true, predicted, train_size, train_time, test_time,
                               SaveOnlyResults=False):
        accuracy = metrics.accuracy_score(true, predicted)
        precision = metrics.precision_score(true, predicted, average="macro")
        recall = metrics.recall_score(true, predicted, average="macro")
        f1score = metrics.f1_score(true, predicted, average="macro")
        confusion_matrix = metrics.confusion_matrix(true, predicted)
        msg = ""
        filename = fingername
        if not FileOperations.FileIsExists(GloveAnalysis.ResultDirectory, filename + "_Results.csv"):
            msg = "method;accuracy;precision;recall;f1score;train_size;train_time[s];avg_train_time[ms];test_size;test_time[s];avg_test_time[ms]\n"
        msg += f"{name};{accuracy};{precision};{recall};{f1score};{train_size};{train_time:.2f};{train_time / train_size * 1000:.2f};{len(true)};{test_time:.2f};{test_time / len(true) * 1000:.2f}\n"
        FileOperations.WriteLines(GloveAnalysis.ResultDirectory + "Fingers/" + filename + "/",
                                  name + "_" + filename + "_Results.csv", msg)
        if not SaveOnlyResults:
            GloveAnalysis.SaveConfusionMatrix(confusion_matrix,
                                              GloveAnalysis.ResultDirectory + "Fingers/" + filename + "/",
                                              name + "_" + filename)
            GloveAnalysis.SaveConfusionMatrix(confusion_matrix, GloveAnalysis.ResultDirectory + "Models/" + name + "/",
                                              filename + "_" + name)

            FileOperations.WriteDataToCSV(list(zip(true, predicted)), ["True", "Predicted"],
                                          GloveAnalysis.ResultDirectory + filename + "/", name + "_values", )

        print(name + " - " + filename + " accuracy: " + str(accuracy))


CreateConfusionMatrices()
