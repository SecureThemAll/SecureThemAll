# SecureThemAll
Framework for Automatic Repair of Security Vulnerabilities in C/C++ programs, 
based on the modified Cyber Grand Challenge Event Corpus for Linux.

## Table of Contents

1. [Supported repair tools](#1-supported-repair-tools)
2. [Benchmark of vulnerabilities](#2-benchmark-of-vulnerabilities)
3. [Repository structure](#3-repository-structure)
4. [Usage](#4-usage)
5. [Results](#5-results)


## 1. Supported repair tools
The framework supports repair tools for C/C++. 
The following tools' abstraction are implemented and supported by the framework:

| #   | Tool                                                                             | Commit id |
| --- | :-------------------------------------------------------------------------------:| --------- |
| 1   | [GenProg](https://github.com/squaresLab/genprog-code)                            | e720256   |
| 2   | [AE](https://github.com/squaresLab/genprog-code)                                 | e720256   |
| 3   | [Prophet](http://www.cs.toronto.edu/~fanl/program_repair/prophet-rep/index.html) |     -     |
| 4   | [SPR](http://www.cs.toronto.edu/~fanl/program_repair/spr-rep/index.html)         |     -     |
| 5   | [Kali](http://www.cs.toronto.edu/~fanl/program_repair/prophet-rep/index.html)    |     -     |
| 6   | [MUT-APR](https://fyassiri.wixsite.com/mutapr)                                   |     -     |
| 7   | [CquenceR](https://github.com/SecureThemAll/CquenceR)                            | 2472e98   |
| 8   | [FlexiRepair](https://github.com/SecureThemAll/FlexiRepair)                            | 2563c55   |
| 9   | [SOSRepair](https://github.com/SecureThemAll/SOSRepair)                                | ae6550e   |
| 10  | [SearchRepair](https://github.com/SecureThemAll/SOSRepairr)                            | ae6550e   |
## 2. Benchmark of vulnerabilities
The framework uses the [cb-repair](https://github.com/SecureThemAll/cb-repair) benchmark, which extends the 
[CGC Corpus by Trail of Bits](https://github.com/trailofbits/cb-multios), for automatic program repair.
The used benchmark contains 57 programs that approximate real software with enough complexity and represent a wide 
variety of vulnerabilities. In  total, there are 34 unique CWE in the benchmark, grouped into 9 categories, such as 
[CWE-664](https://cwe.mitre.org/data/definitions/664.html), [CWE-118](https://cwe.mitre.org/data/definitions/118.html), 
[CWE-682](https://cwe.mitre.org/data/definitions/682.html).

## 3. Repository structure

This repository is structured as follow:

```
├── benchmark: contains the git submodule for the cb-repair benchmakr plugged-in the framework
├── data: contains repair tools' configurations, e.g. the repair tool's executable
├── plots: contains the plots generate from the results, e.g. each tool's fixes per CWE
├── repair_tools: contains the scripts and info on how to download and install the tools above mentioned
├── results: folder where the output of the tools' execution are saved (contains the latest results)
├── script: contains the main scripts to run SecureThemAll along with its source code
│ ├── Main files:
│ ├── config.py: contains the parameters of SecureThemAll, e.g. tools' execution timeout, working dir, etc.
│ ├── repair.py: script to run a repair tool on various benchmark's programs
│ └── compare.py: script to generate comparison plots based on the available results
├── Dockerfile: dockerfile to instantiate and run SecureThemAll on docker
├── RESULTS.MD: detailed results along with comprative plots of the outcome of the tools' execution
├── docker-compose.yml: to run in as microservices SecureThemAll, the benchmark and the repair tools (MUT-APR, AE, GenProg, and CquenceR)
├── init.sh: script to install SecureThemAll requirements and initialize the benchmark and the repair tools (MUT-APR, AE, GenProg, and CquenceR)
```

## 4. Usage
These instructions will get you a copy of the project up and running on your local machine for development, testing, 
and results reproducibility purposes. You can also set up and run the project on Docker by following these 
[instructions](SETUP.md). 

### Notes

---
These notes might save you some time:

* Ensure that sh is symlinked to bash, not dash
* If some commands don't work, change the timeout in the configuration file, depending on the system, the commands might take more time to execute.
* If you have to interrupt the execution of the tool, make sure to delete the generated file LOCK_CHALS_INIT.
* Make sure you have the benchmark initialized. Check benchmark's documentation for more information on that. 
* When executing compare command, make sure all the tools have result files for the same programs, i.e. results.json exists and has correct format

### Install dependencies

Install the necessary dependencies for cb-multios and GenProg before running the project.
<br/>
#### Software:
* [Python (3.7.5)](https://www.python.org/)
* [GenProg v3.2](https://github.com/squaresLab/genprog-code.git)
* [MUT-APR](https://fyassiri.wixsite.com/mutapr)

#### 1) Clone this repo with submodule
``` console
$ git clone --recurse-submodules -j8 https://github.com/SecureThemAll/SecureThemAll.git
```

Or

``` console
$ git clone https://github.com/SecureThemAll/SecureThemAll.git
$ cd SecureThemAll
$ git submodule update --init --recursive
```

#### 2) Install Tools Prerequisites
For now, GenProg doesn't have a init script. It must be setup manually. The source code needs to be compiled.
For MUT-APR, run ```repair_tools/init_mut_aprfl.sh```.

#### 3) Init Benchmark
Execute the ```init.sh``` in the folder ```benchmark/cb-repair```.


#### 4) Install Repair Tools
You can find the scripts for downloading and installing the _GenProg/AE_, _MUT-APR_, and _CquenceR_ tools in the 
```repair_tools``` folder. _Prophet/Kali/SPR_ use the same environment, and given their requirements, these follow a 
different setup on the original environment supplied by the author. The instructions for setting up all the tools are
available [here](repair_tools/README.md),```repair_tools/README.md```.


### Execute tools on programs from the benchmark
The following command is a baseline for normal usage of the repair script:

``` console
$ python3 repair.py GenProg -c BitBlaster --seed 1 --verbose
```

The following command is a baseline for normal usage of the compare script:

``` console
$ python3 compare.py --seed 1 --verbose --plot performance
```
---
The available plots are the following: 
* performance
* profile 
* fixes 
* sets

## 5. Results
In our study we found that the 7 tools can fix 26 out  of 57 vulnerable programs — 46% of the considered issues only.
At most the tools (_AE_) can repair individually 20, out of 57 programs, that is 35%.
_MUT-APR_ follows with 17 repaired programs (29.82%), _Kali_ and _GenProg_ with 15 repaired programs each (26.32%), 
_CquenceR_ with 7 repaired programs (12.28%), and lastly _SPR_ and _Prophet_ both with 3 repaired programs (5.26%).

![All Tools' repair results](./plots/all_fixes_top.png)

The detailed tool's execution results and plots can be seen [here](RESULTS.md)

## Acknowledgments
Guidance and ideas for some parts from:

* Project structure and abstractions from [The RepairThemAll Framework](https://github.com/program-repair/RepairThemAll)
