#!/bin/bash

pkill -9 -ef shared_memory
VAR=$(ipcs | awk '$5 == 12 {print $2}')
ipcrm -m $VAR
unset VAR