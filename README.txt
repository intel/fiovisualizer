 FIO visualizer 1.1 13 Jan 2017

 DESCRIPTION
 -----------
 This tool is a data visualisation tool for FIO (http://freecode.com/projects/fio) written on PyQtGraph (http://www.pyqtgraph.org).

 OVERVIEW
 --------
 PyQtGraph based visualizer for FIO. Requires to run on behalf of root user as requires access to block devices.

 PACKAGE CONTENT
 ---------------
 README.txt
    this readme file
 LICENSE.txt
    license file   	
 fio_visualizer.py
    application script.
 mainwindow.ui 
    GUI definition part of the script
 Workloads:
  - Device
     Block device workloads covering typical specifications, separated in SATA and NVMe sections
  - Precondition
     instruction and script files to prepare SSD for the testing.
  - Simulation
     Workloads to simulate real applications.
  - MultiDevice
     Workloads to test two or more drives at a time. Currently has limitted support due to improper handling of total performance in the script. 

 INSTALLATION
 ------------
 Requires:

  FIO 2.15 or newer (2.1.x is no longer supported) https://github.com/axboe/fio/releases
  PyQtGraph http://www.pyqtgraph.org/
  Python 2.7 and 3+
  PyQt 4.8+ or PySide
  numpy
  scipy

 CentOS 7 steps:
 ---------------

  0. You should have python and PyQt installed with the OS

  1. Install pyqtgraph-develop (0.9.9 required) form http://www.pyqtgraph.org
	 $ python setup.py install

  2. Install Cyphon from http://cython.org Version 0.21 or higher is required.
	 $ python setup.py install

  3. Install Numpy from http://numpy.org 
	 $ python setup.py build
	 $ python setup.py install

  4. Install FIO from http://freecode.com/projects/fio
	 # ./configure
	 # make
	 # make install

  5. Run Visualizer under root.
         # ./fio-visualizer.py


 Ubuntu steps:
 -------------
  1. Add repository "deb http://luke.campagnola.me/debian dev/" into your /etc/apt/sources.list
    	sudo apt-get install fio python-pyqtgraph

  2. Install FIO from http://freecode.com/projects/fio
	 # ./configure
	 # make
	 # make install

  3. Run Visualizer under root.
         # ./fio-visualizer.py


 LIMITATIONS
 -----------
  1. Increased CPU load with numjobs > 4 and all threads plotting. Avoid plotting all threads 
     with numjobs > 4 or disable unneccessary ones to save CPU time.
  2. Multi-jobs configurations files (i.e. [job1]... [job2]) are not supported at the moment.
     The total amount of jobs if every workload has "numjobs" specified too are not correctly parsed.
     This can still be implemented manually specifing it in the code. See line #986.

 TODO
 ----
  1. Continue working on workload profiles for new Intel SSDs. 

 MAINTAINERS
 -----------
 Andrey Kudryavtsev andrey.o.kudryavtsev@intel.com
 Alexey Ponomarev alexey.ponomarev@intel.com
