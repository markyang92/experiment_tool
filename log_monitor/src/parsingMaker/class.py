import pandas as pd
import numpy as np

class LogParser:
    def __init__(self, fname=None, header=["time", "val"], separator="," ):
        self.fname = fname
        self.header = header
        self.separator = separator
        self.dtype = {col:np.float64 for col in header}

    def parse(self):
        self.result = pd.read_csv(self.fname,
                                    sep=self.separator,
                                    names=self.header,
                                    header=1,
                                    dtype=self.dtype)

        self.resampleResult(header=self.header)

    def writeOutput(self):
        parsed_fname = self.makeParsedFname()
        self.result.to_csv(parsed_fname, index=False)

    def makeParsedFname(self):
        fname_split = self.fname.split("/")
        fname_split[-1] = "parsed_" + fname_split[-1]
        parsed_fname = "/".join(fname_split)
        return parsed_fname

    def resampleResult(self, header=None):
        def mean_data(x):
            if len(x) == 0:
                return None
            else:
                return sum(x) / len(x)
        if self.header == None:
            time = self.result.iloc[:, 0]
            time = time - min(time)
            val = self.result.iloc[:, 1]
        else:
            time = self.result[self.header[0]]
            time = time - min(time)
            val = self.result[self.header[1]]

        time_int = [[] for x in range(int(max(time) - min(time) + 1))] 
        for i in range(len(self.result)):
            idx = int(time[i])
            time_int[idx].append(val[i])

        time_int = list(map(mean_data, time_int))
        
        self.result = pd.DataFrame()
        self.result["time"] = [x for x in range(len(time_int))]
        self.result["val"] = time_int

if __name__ == "__main__":
    fname = sys.argv[1]
    log_parser = LogParser(fname)
    log_parser.parse()
    log_parser.writeOutput()
