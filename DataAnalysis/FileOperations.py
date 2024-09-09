import json
import os
import re

import pandas as pd


class FileOperations:
    ResultDirectory = './Results/'
    ProcessedResults = './ProcessedResults/'
    PreprocessedResults = './Preprocessed/'

    @staticmethod
    def GetResultsDirectoryNames():
        result_lists = os.listdir(FileOperations.ResultDirectory)
        procesed_lists = os.listdir(FileOperations.ProcessedResults)

        non_processed_lists = [x for x in result_lists if x not in procesed_lists]
        return non_processed_lists

    @staticmethod
    def GetFiles(directory):
        files = os.listdir(FileOperations.ResultDirectory + directory)

        return files

    @staticmethod
    def GetFolderNames(directory):
        path =FileOperations.ResultDirectory + directory
        return [name for name in os.listdir(path) if os.path.isdir(path+name)]

    @staticmethod
    def CreateFolder(directory):
        os.mkdir(FileOperations.ProcessedResults + directory)

    @staticmethod
    def CreateFolderIfNotExists(directory):
        if not os.path.exists(directory):
            os.mkdir(directory)

    @staticmethod
    def ReadJsonFile(directory, filename):
        with open(FileOperations.ResultDirectory + directory + "/" + filename) as file:
            lines = file.readlines()
            return [json.loads(x) for x in lines]

    @staticmethod
    def ReadCSVFile(directory, filename):
        with open(FileOperations.ResultDirectory + directory + "/" + filename) as file:
            lines = file.readlines()
            return [re.split(";|:", x) for x in lines]

    @staticmethod
    def WriteLines(directory, filename, lines):
        os.makedirs(directory, exist_ok=True)
        with open(directory + filename, 'a') as file:
            file.writelines(lines)

    @staticmethod
    def WriteDataToCSV(value_arrays, header, directory, filename):
        if len(value_arrays) > 0:
            # merged_list = list(zip(*value_arrays))
            os.makedirs(directory, exist_ok=True)
            df = pd.DataFrame(value_arrays, columns=header)
            df.to_csv(directory + filename + ".csv", sep=";")
