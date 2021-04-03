# Parse and Make Graph with Log file
1. Parsing log files
* ../logs/ExperimentTitle/*.log
```console
./parser.py -path ../logs/ExperimentTitle 
```

example:
../logs/
└── matmulGEMM4_768x3584
    ├── matmulGEMM4_128_128
    │   ├── framework_result.log
    │   ├── matmul_kernel_result.log
    │   └── streamline_matmulGEMM4_768x3584_128_128.log
    ├── matmulGEMM4_16_16
    │   ├── framework_result.log
    │   ├── matmul_kernel_result.log
    │   └── streamline_matmulGEMM4_768x3584_16_16.log
    └── matmulGEMM4_768_3584
        ├── framework_result.log
        ├── matmul_kernel_result.log
        └── streamline_matmulGEMM4_768x3584_768_3584.log

./parser.py -path ../logs/matmulGEMM4_768x3584/ -r Y -s GE -tag GEMM4
1) ../logs/matmulGEMM4_768x3584/* 로 디렉터리를 search 한다.
2) 각 디렉터리에 .log 파일들을 parsing 한 후, dirname 기준으로 새로운 디렉터리를 만들고 거기에 전처리 된 csv 파일을 저장한다.
3) -g 옵션을 넣으면 여기서 만들어진 csv를 기준으로 그래프를 작성한다.
4) -tag 에 문자를 넣은대로 csv['APP'] Column에 문자가 저장된다.
4) 특별한 옵션을 명시 하지 않아도 이 디렉터리 log 파일들로 유의미한 하나의 csv 파일은 ../statistics에 저장된다.


Statistics file will be saved in ../logs/statistics/ automatically

2. Combine Csv files
* ../statistics/*.csv
```console
./csvCombinder.py -path ../statistics -c Y
```

example:
../statistics/
└── matmulGEMM4
    ├── matmulGEMM4_32_32.csv
    ├── matmulGEMM4_16_16.csv
    ├── matmulGEMM4_128_128.csv
    └── result.csv

./csvCombinder.py -path ../statistics/matmulGEMM4 -c Y
1) ../statistics/matmulGEMM4/*.csv 로 search
2) 모아서 처리 후, result.csv 하나의 파일을 만든다.

./csvCombinder.py -path ../statistics/matmulGEMM4/result.csv -g y
1) 주어지는 result.csv로 그래프 그린다.

