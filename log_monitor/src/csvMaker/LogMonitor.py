import threading
import time
import glob
import os
import sys
import hashlib
from matplotlib import pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../parser/")
from LogParser import LogParser
from FFmpegLogParser import FFmpegLogParser

from ipywidgets import Output
out = Output()

class LogMonitor:
    def __init__(self, fname, monitor_interval=10, debug=False):
        self.fname = fname
        self.dirs = []
        self.monitor_interval = monitor_interval
        self.depth = 2
        self.graph_hash = {}
        self.debug = debug

        try:
            os.system("mkdir graph")
        except:
            print("[Error] graph already exist")
            pass


    def monitor_logs(self):
        while True:
            self.logs = []
            self.data = {}

            # update log files
            self.monitor_dir(glob.glob(self.fname + "/*"), self.depth)

            # parse all data
            self.parse_log_all()

            # plot all parsed data
            self.plot_all()

            if self.debug:
                break
            # sleep for monitoring interval
            time.sleep(self.monitor_interval)

    def monitor_dir(self, dirs, depth):
        if depth == 0:
            for dir in dirs:
                self.logs.append(dir)

        for dir in dirs:
            self.monitor_dir(glob.glob(dir + "/*"), depth-1)

    def parse_log_all(self):
        for log in self.logs:
            self.parse_log(log)

    def parse_log(self, log):
        if "ffmpeg" in log.lower():
            log_parser = FFmpegLogParser(fname=log)
        else:
            log_parser = LogParser(fname=log)

        try:
            log_parser.parse()
        except:
            print("[Error] {:s} can't be parsed, please check your log file".format(log))
            return

        self.classify_log(log, log_parser.result)

    def classify_log(self, fname, data):
        parse_name = list(filter(lambda x : x != "." and len(x) != 0,
                                 fname.split("/")))
        scenario = parse_name[1]
        app = parse_name[2]
        log_name = parse_name[3]

        if scenario not in self.data:
            self.data[scenario] = {}

        if app not in self.data[scenario]:
            self.data[scenario][app] = []

        self.data[scenario][app].append((log_name, data))

    def plot_all(self):
        for scenario in self.data.keys():
            self.plot(scenario)

    def plot(self, scenario):
        for app, app_logs in self.data[scenario].items():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            for log_name, log_val in app_logs:
                ax.scatter(log_val["time"], log_val["val"], label=log_name)

            if "ffmpeg" in app.lower():
                ylabel = "FPS"
            elif "cl" in app.lower():
                ylabel = "GFLOPS"
            elif "gl" in app.lower():
                ylabel = "FPS"

            ax.set_xlabel("Time(s)")
            ax.set_ylabel(ylabel)
            ax.legend()

            ax.set_title("{:s} - {:s}".format(scenario, app))

            if not self.check_duplicate(scenario, app_logs):
                ax.plot(1, 1)

                plt.pause(0.05)
                plt.draw()

            fig.savefig("graph/{:s}_{:s}.png".format(scenario, app), dpi=300)
            plt.close(fig)

    def check_duplicate(self, scenario, logs):
        total_hash = scenario

        for log_name, log_val in logs:
            time_str = str(log_val["time"].tolist()).encode()
            val_str = str(log_val["val"].tolist()).encode()
            total_hash += hashlib.sha256(time_str + val_str).hexdigest()

        total_hash = hashlib.sha256(total_hash.encode()).hexdigest()
            
        if total_hash in self.graph_hash:
            return True
        else:
            self.graph_hash[total_hash] = 1
            return False
