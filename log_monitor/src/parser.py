#!/usr/bin/python
from parsingMaker.LogParsing import argument
from parsingMaker.LogParsing import ParseProcess
from csvMaker.csvParser import makeCSV
from graphMaker.graphMaker import graph
from graphMaker.graphMaker import csvGraph
import os
import sys

if __name__ == "__main__":
	task=argument()
	for now_dir in task.dirList:
		# 1. Parsing Specific Directory
		AfterParsedFiles=ParseProcess(now_dir,task.streamline)

		# 2. Make CSV File using parsed log in statistics
		makeCSV(AfterParsedFiles,task.tag)


		