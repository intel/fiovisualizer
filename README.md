# fiovisualizer

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

# Setup

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

# Development notes

## Limitations
1. Increased CPU load with numjobs > 4 and all threads plotting. Avoid plotting all threads with numjobs > 4 or disable unneccessary ones to save CPU resources.
2. Multi-jobs configurations files (i.e. [job1]... [job2]) are not supported at the moment. The total amount of jobs if every workload has "numjobs" specified too are not correctly parsed. This can still be implemented manually specifing it in the code.

## Todo
Continue working on workload profiles for new Intel SSDs. 

## Maintainers
   - Andrey Kudryavtsev andrey.o.kudryavtsev@intel.com
   - Alexey Ponomarev alexey.ponomarev@intel.com

## Realtime backend processor

fiovisualizer implements its realtime backend processor on the file
realtime_back.py. This section documents the backend processor.

### Starting fio

The routine start_fio() kicks off the fio process, and it
kicks of a process which more or less looks something like the following:

``` bash
fio --minimal --eta=never --status-interval=1 path-to-fio.ini
```
### Realtime resolution

Since `--status-interval=1` is currently used statically, it means a resolution
of 1 second is used between updates.

### Meaning of data being processed

Since `--status-interval` is used the values being processed currently do not
provide per period measurements. The values being processed reflect the
overall cumulative (from job start) values at the specified time intervals.

#### fiovisualizer support for output format

fio supports different output formats. The smallest and most compact output
format currently is the terse output, and so fiovisualizer uses this to minimize
the amount of processing done on the output and also to minimize the amount of
data being transfered from a remote fio server.

##### fiovisualizer terse output format support

fio supports different terse format versions, the format version can be
specified via the argument `--terse-version`. If no version is specified the
version used will depend on the fio release.

##### fio terse parsing version notes

When `--minimal` is used it is equivalent to using `--output-format=terse`.

The `--output-format` parameter was added via fio commit f3afa57e3 ("Add
--output-format command line option") merged since fio-2.0.10.

fiovisualizer started supporting fio since fio-2.1.14. The release of
fio-2.1.14 uses by default the terse output format version 3. fiovisualizer's
parser only currently supports terse output format version 3.

The `--terse-version` parameter was added to fio via commit f57a9c59e36
("Add terse version output format command line parameter"), this commit was
merged on the fio-1.58 release. This fio-1.58 release however used the terse
version format 2. Development for the terse version format 3 started
since fio commit 312b4af22018a ("Add IOPS to terse output") supported since
fio-1.99.6.

The current default terse output format on the latest fio release is terse
version format 3.

##### fio terse output format version 3

Below is a short description of each or the column outputs for fio terse
output version format 3.

| 0 | terse_version_3 |
| 1 | fio_version |
| 2 | jobname |
| 3 | groupid |
| 4 | error |
| 5 | read_kb |
| 6 | read_bandwidth |
| 7 | read_iops |
| 8 | read_runtime_ms |
| 9 | read_slat_min |
| 10 | read_slat_max |
| 11 | read_slat_mean |
| 12 | read_slat_dev |
| 13 | read_clat_min |
| 14 | read_clat_max |
| 15 | read_clat_mean |
| 16 | read_clat_dev |
| 17 | read_clat_pct01 |
| 18 | read_clat_pct02 |
| 19 | read_clat_pct03 |
| 20 | read_clat_pct04 |
| 21 | read_clat_pct05 |
| 22 | read_clat_pct06 |
| 23 | read_clat_pct07 |
| 24 | read_clat_pct08 |
| 25 | read_clat_pct09 |
| 26 | read_clat_pct10 |
| 27 | read_clat_pct11 |
| 28 | read_clat_pct12 |
| 29 | read_clat_pct13 |
| 30 | read_clat_pct14 |
| 31 | read_clat_pct15 |
| 32 | read_clat_pct16 |
| 33 | read_clat_pct17 |
| 34 | read_clat_pct18 |
| 35 | read_clat_pct19 |
| 36 | read_clat_pct20 |
| 37 | read_tlat_min |
| 38 | read_lat_max |
| 39 | read_lat_mean |
| 40 | read_lat_dev |
| 41 | read_bw_min |
| 42 | read_bw_max |
| 43 | read_bw_agg_pct |
| 44 | read_bw_mean |
| 45 | read_bw_dev |
| 46 | write_kb |
| 47 | write_bandwidth |
| 48 | write_iops |
| 49 | write_runtime_ms |
| 50 | write_slat_min |
| 51 | write_slat_max |
| 52 | write_slat_mean |
| 53 | write_slat_dev |
| 54 | write_clat_min |
| 55 | write_clat_max |
| 56 | write_clat_mean |
| 57 | write_clat_dev |
| 58 | write_clat_pct01 |
| 59 | write_clat_pct02 |
| 60 | write_clat_pct03 |
| 61 | write_clat_pct04 |
| 62 | write_clat_pct05 |
| 63 | write_clat_pct06 |
| 64 | write_clat_pct07 |
| 65 | write_clat_pct08 |
| 66 | write_clat_pct09 |
| 67 | write_clat_pct10 |
| 68 | write_clat_pct11 |
| 69 | write_clat_pct12 |
| 70 | write_clat_pct13 |
| 71 | write_clat_pct14 |
| 72 | write_clat_pct15 |
| 73 | write_clat_pct16 |
| 74 | write_clat_pct17 |
| 75 | write_clat_pct18 |
| 76 | write_clat_pct19 |
| 77 | write_clat_pct20 |
| 78 | write_tlat_min |
| 79 | write_lat_max |
| 80 | write_lat_mean |
| 81 | write_lat_dev |
| 82 | write_bw_min |
| 83 | write_bw_max |
| 84 | write_bw_agg_pct |
| 85 | write_bw_mean |
| 86 | write_bw_dev |
| 87 | cpu_user |
| 88 | cpu_sys |
| 89 | cpu_csw |
| 90 | cpu_mjf |
| 91 | cpu_minf |
| 92 | iodepth_1 |
| 93 | iodepth_2 |
| 94 | iodepth_4 |
| 95 | iodepth_8 |
| 96 | iodepth_16 |
| 97 | iodepth_32 |
| 98 | iodepth_64 |
| 99 | lat_2us |
| 100 | lat_4us |
| 101 | lat_10us |
| 102 | lat_20us |
| 103 | lat_50us |
| 104 | lat_100us |
| 105 | lat_250us |
| 106 | lat_500us |
| 107 | lat_750us |
| 108 | lat_1000us |
| 109 | lat_2ms |
| 110 | lat_4ms |
| 111 | lat_10ms |
| 112 | lat_20ms |
| 113 | lat_50ms |
| 114 | lat_100ms |
| 115 | lat_250ms |
| 116 | lat_500ms |
| 117 | lat_750ms |
| 118 | lat_1000ms |
| 119 | lat_2000ms |
| 120 | lat_over_2000ms |
| 121 | disk_name |
| 122 | disk_read_iops |
| 123 | disk_write_iops |
| 124 | disk_read_merges |
| 125 | disk_write_merges |
| 126 | disk_read_ticks |
| 127 | write_ticks |
| 128 | disk_queue_time |
| 129 | disk_util |

### Processing

Below is an example output of one line out using:

``` bash
fio  --client=some-hostname --eta=never --status-interval=1 --terse-version=3 some.ini
```
The output:

```
3;fio-3.8-41-g7302;job1;0;0;0;0;0;0;0;0;0.000000;0.000000;0;0;0.000000;0.000000;1.000000%=0;5.000000%=0;10.000000%=0;20.000000%=0;30.000000%=0;40.000000%=0;50.000000%=0;60.000000%=0;70.000000%=0;80.000000%=0;90.000000%=0;95.000000%=0;99.000000%=0;99.500000%=0;99.900000%=0;99.950000%=0;99.990000%=0;0%=0;0%=0;0%=0;0;0;0.000000;0.000000;0;0;0.000000%;0.000000;0.000000;1886832;188645;23580;10002;1;87;2.561636;0.999742;6;6575;165.280554;282.700285;1.000000%=11;5.000000%=13;10.000000%=15;20.000000%=19;30.000000%=25;40.000000%=35;50.000000%=51;60.000000%=89;70.000000%=148;80.000000%=240;90.000000%=452;95.000000%=675;99.000000%=1286;99.500000%=1679;99.900000%=2736;99.950000%=3293;99.990000%=5013;0%=0;0%=0;0%=0;12;6577;167.875769;282.729144;138363;314224;25.026987%;188630.900000;35637.687291;5.179482%;9.399060%;151970;0;51;0.1%;0.1%;100.0%;0.0%;0.0%;0.0%;0.0%;0.00%;0.00%;0.01%;21.49%;27.82%;12.61%;18.75%;10.68%;4.67%;2.00%;1.66%;0.28%;0.03%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;0.00%;nvme0n1;44;934217;0;0;9;152472;152997;99.24%
```

From the above fiovisualizer's realtime_back.py records the following 6 columns
and graphs them, below listed from the respective value from the output above:

| 6 | read_bandwidth | 0 |
| 7 | read_iops | 0 |
| 15 | read_clat_mean | 0.000000 |
| 47 | write_bandwidth | | 188645 |
| 48 | write_iops | 23580 |
| 56 | write_clat_mean | 165.280554 |
