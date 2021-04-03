import sys 
import pandas as pd
import numpy as np

from LogParser import LogParser
TARGETS = ["timestamp", "fps"]

class FFmpegLogParser(LogParser):
    def __init__(self, fname=None, targets=TARGETS):
        LogParser.__init__(self, fname=fname, header=targets)
        self.targets = targets
        self.result = None

    def parse(self):
        self.result = {x:[] for x in self.targets}
        self.prev_time = 0.0
        self.cur_time = 0.0

        # parse given ffmpeg log
        with open(self.fname) as input_file:
            for line in input_file:
                self.parseLine(line)

        # convert result to pandas.DataFrame
        self.result = pd.DataFrame.from_dict(self.result)

        # resample result
        self.resampleResult(header=self.targets)


    def parseLine(self, line):
        line = line.strip()

        # find targets in line
        if self.findTargets(line) == False:
            return

        # convert raw string to list
        data = self.lineToData(line)

        # parse targets in data
        self.parseTargets(data)

    def findTargets(self, line):
        find = True
        for target in self.targets:
            if target not in line:
                find = False
                break
        return find

    def lineToData(self, line):
        data = []
        line = line.split()
        for elem in line:
            for key in elem.split("="):
                if len(key) > 0:
                    data.append(key)
        return data

    def parseTargets(self, data):
        num = len(self.targets)

        for i in range(len(data)//2):
            if num == 0:
                break
            if data[2*i] in self.targets:
                self.result[data[2*i]].append(float(data[2*i+1]))

                
if __name__ == "__main__":
    fname = sys.argv[1]
    log_parser = FFmpegLogParser(fname)
    log_parser.parse()
    log_parser.writeOutput()
