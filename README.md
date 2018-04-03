## Description

This tool is a realtime data visualisation tool for [FIO](http://freecode.com/projects/fio) written using [PyQtGraph](http://www.pyqtgraph.org).

## Overview

This application is written in Python, using PyQtGraph to graph FIO data in realtime. Running as root is required because this application accesses block devices.

## Package Content
- README.md
  - This readme file
- LICENSE.txt
  - License file   	
- fio_visualizer.py
  - The frontend for this application
- realtime_back.py
  - The backend for this application
- mainwindow.ui 
  - GUI definition part of the script
- Workloads:
  - Device
    - Block device workloads covering typical specifications, separated in SATA and NVMe sections
  - Precondition
    - instruction and script files to prepare SSD for the testing.
  - Simulation
    - Workloads to simulate real applications.
  - MultiDevice
    - Workloads to test two or more drives at a time. Currently has limitted support due to improper handling of total performance in the script. 

## Installation
Requires:

   - FIO 2.15 or newer (2.1.x is no longer supported) found [here](https://github.com/axboe/fio/releases)
   - PyQtGraph found [here](http://www.pyqtgraph.org/)
   - Python 2.7 or 3+ [here](https://www.python.org/downloads/)
   - PyQt 4.8+ or PySide
   - numpy
   - scipy

#### CentOS 7 steps

0. You should have python and PyQt installed with this distro

1. Install pyqtgraph-develop (0.9.9 required) from [here](http://www.pyqtgraph.org)
   - `$ python setup.py install`

2. Install Cyphon from [here](http://cython.org) Version 0.21 or higher is required.
   - `$ python setup.py install`

3. Install Numpy from [here](http://numpy.org)
   - `$ python setup.py build`
   - `$ python setup.py install`

4. Install FIO from [here](http://freecode.com/projects/fio)
   - `# ./configure`
   - `# make`
   - `# make install`

5. Run Visualizer as root.
   - `# ./fio_visualizer.py`


#### Ubuntu steps

1. Add the following repository `deb http://luke.campagnola.me/debian dev/` into your `/etc/apt/sources.list` and then run `$ sudo apt-get install fio python-pyqtgraph`

2. Install FIO from [here](http://freecode.com/projects/fio)
   - `# ./configure`
   - `# make`
   - `# make install`

3. Run Visualizer as root.
   - `# ./fio_visualizer.py`


## Limitations
1. Increased CPU load with numjobs > 4 and all threads plotting. Avoid plotting all threads with numjobs > 4 or disable unneccessary ones to save CPU resources.
2. Multi-jobs configurations files (i.e. [job1]... [job2]) are not supported at the moment. The total amount of jobs if every workload has "numjobs" specified too are not correctly parsed. This can still be implemented manually specifing it in the code.

## Todo
Continue working on workload profiles for new Intel SSDs. 

## Maintainers
   - Andrey Kudryavtsev andrey.o.kudryavtsev@intel.com
   - Alexey Ponomarev alexey.ponomarev@intel.com
