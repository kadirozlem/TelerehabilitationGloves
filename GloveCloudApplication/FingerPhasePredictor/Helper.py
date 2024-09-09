import datetime


class SectionTime:
    Dictionary={}
    def __init__(self):
        self.start_time =None
        self.end_time=None
    @staticmethod
    def getObject(name):
        sample = SectionTime.Dictionary.get(name)
        if sample is None:
            sample = SectionTime()
            SectionTime.Dictionary[name] = sample
        return sample
    @staticmethod
    def start(name):
        time = SectionTime.now()
        SectionTime.getObject(name).start_time=time

    @staticmethod
    def end(name, print=False, response=False):
        time = SectionTime.now()
        sample = SectionTime.getObject(name)
        sample.end_time = time
        if print:
            SectionTime.printSingleSection(sample, name)
            del SectionTime.Dictionary[name]
        elif response:
            duration = -1
            if sample.start_time is not None:
                duration = sample.end_time-sample.start_time
            del SectionTime.Dictionary[name]
            return duration

    @staticmethod
    def printSingleSection(sample, name):
        error = False
        if sample.end_time is None:
            error = True
            print(name + " end time is missing")
        if sample.start_time is None:
            error = True
            print(name + " start time is missing")

        if not error:
            diff = sample.end_time - sample.start_time
            print(f"Section time of {name}:{diff:.2f} s")

    @staticmethod
    def now():
        return datetime.datetime.now().timestamp()

    @staticmethod
    def print():
        temp_dict = SectionTime.Dictionary
        SectionTime.Dictionary = {}
        message = []
        for key in temp_dict:
            sample = temp_dict[key]
            error = False
            if sample.end_time is None:
                error = True
                print(key+" end time is missing")
            if sample.start_time is None:
                error = True
                print(key+" start time is missing")

            if not error:
                diff = sample.end_time-sample.start_time
                message.append(f"{key}:{diff*1000:.2f}")

        print(" - ".join(message))