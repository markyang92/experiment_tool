#!/usr/bin/python
from parsingMaker.LogParsing import argumentCsv
from parsingMaker.LogParsing import ParseProcess
from csvMaker.csvParser import combineCsv
from csvMaker.csvParser import makeCSV
from graphMaker.graphMaker import graph
from graphMaker.graphMaker import csvGraph
import os
import sys

if __name__ == "__main__":
	task=argumentCsv()
	if(task.combine):
		combineCsv(task)
	elif(task.graph):
		csvGraph(task.path)


