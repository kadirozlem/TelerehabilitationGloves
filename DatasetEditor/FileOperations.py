import datetime
import json
import os
import re
import shutil
import zipfile
import os.path

import pandas as pd

class ExecutionTime:
    @staticmethod
    def now():
        return datetime.datetime.now().timestamp()
    def __init__(self):
        self.start_time=ExecutionTime.now()

    def end(self,title):
        self.end_time = ExecutionTime.now()
        duration = self.end_time - self.start_time
        print(f"{title} lasts {duration:.2f} s")


class FileOperations:

    @staticmethod
    def GetDirectoryNames(directory):
        return os.listdir(directory)

    @staticmethod
    def GetFiles(directory):
        files = os.listdir(directory)
        return files

    @staticmethod
    def CreateFolder(directory):
        os.mkdir(directory)

    @staticmethod
    def CreateFolderIfNotExists(directory):
        os.makedirs(directory,exist_ok=True)

    @staticmethod
    def ReadJsonFile(directory, filename):
        with open(directory + "/" + filename) as file:
            lines = file.readlines()
            return [json.loads(x) for x in lines]

    @staticmethod
    def ReadCSVFile(directory, filename=None):
        path = directory + "/" + filename if filename is not None else directory
        with open(path) as file:
            lines = file.readlines()[1:]
            return [re.split(";", x.strip().replace("!","")) for x in lines]

    @staticmethod
    def ReadFile(directory, filename):
        with open(directory + "/" + filename) as file:
            return file.readlines()

    @staticmethod
    def WriteLines(directory, filename, lines, isAppend = True):
        os.makedirs(directory, exist_ok=True)
        with open(directory + filename, 'a' if isAppend else "w",encoding="utf-8") as file:
            file.writelines(lines)

    @staticmethod
    def WriteDataToCSV(value_arrays, header, directory, filename):
        if len(value_arrays) > 0:
            # merged_list = list(zip(*value_arrays))
            os.makedirs(directory, exist_ok=True)
            df = pd.DataFrame(value_arrays, columns=header)
            df.to_csv(directory + filename + ".csv", sep=";")

    @staticmethod
    def RemoveDirectory(directory):
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)

    @staticmethod
    def RemoveFile(directory, filename=None):
        path = directory + "/" + filename if filename is not None else directory
        if FileOperations.FileIsExists(directory, filename):
            os.remove(path)
    @staticmethod
    def CopyAllContentToDir(src, dst):
        files = os.listdir(src)

        for fname in files:
            shutil.copy2(os.path.join(src, fname), dst)

    @staticmethod
    def ExtractZip(zip_file, extract_folder):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

    @staticmethod
    def GetOSDirectory(path):
        return os.getcwd()+path

    @staticmethod
    def CopyFile(path1, path2):
        shutil.copy2(path1,path2)

    @staticmethod
    def ReadExcel(directory, filename=None):
        path = directory + "/" + filename if filename is not None else directory
        df = pd.read_excel(path, header=None)
        return df.values.tolist()

    @staticmethod
    def FileIsExists(directory, filename=None):
        path = directory + "/" + filename if filename is not None else directory
        return os.path.exists(path)