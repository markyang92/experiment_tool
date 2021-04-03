Automatic Experiment & Log Parsing Tool
=======================================

## How to use automatic experiment
* Run `experiment_script.py` in script directory
* Before do your experiment, read `script/README.md`

## How to make graph
1. Log file will be saved in `log_monitor/logs`
2. Pre-processing and Making graph tool is in `log_monitor/src/run.py`

## Tree
```
experiment_script
├─ LICENSE
├─ README.md
├─ log_monitor
│  ├─ logs        -> Log files
│  ├─ src
│  │  ├─ csvMaker       
│  │  │  └─ csvParser.py   -> Parsing and Making log statistics. It will be saved in log_monitor/statistics csv format 
│  │  ├─ graphMaker     
│  │  │  └─ graphMaker.py  -> Making graph script
│  │  ├─ parsingMaker   
│  │  │  └─ LogParsing.py  -> Set Arguments and parsing script
│  │  └─ run.py   -> Parsing Runner
│  └─ statistics  -> Csv files will be made after parsing
└─ script
   ├─ README.md
   ├─ exp_script
   ├─ experiment_script.py  -> Do! experiment
   ├─ scenario
   │  ├─ README.md
   │  ├─ sample             -> Experiment scenario. Before write scenario, Read README.md file.
   │  │  ├─ expr_schedule
   │  │  ├─ init_cmd
   │  │  ├─ log
   │  │  └─ scenario
   └─ tools                 -> Additional tools when it used in experiment
      ├─ ...
      ├─ kill_ipc.sh
      └─ shared_memory
```