#!/usr/bin/python
from select import select
import subprocess
import os
import signal
import threading
import shlex
import sys
import time

def start_fio():
    fio_process = subprocess.Popen(make_cmd('/root/fio_analyzer/real_time/test.ini'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setpgrp)
    exit_code = [None]
    parsing_thread = threading.Thread(target=lambda: parse_fio_output(fio_process, exit_code), args=())
    parsing_thread.start()

def parse_fio_output(riops, rbw, wiops, wbw, rlatmean, rlatmax, wlatmean, wlatmax, fio_process, exit_var):
    while fio_process.poll() == None:
        parsed = fio_process.stdout.readline().split(';')
        try:
            riops.append(int(parsed[7]))
            rbw.append(float(parsed[6])/1000)
            wiops.append(int(parsed[48]))
            wbw.append(float(parsed[47])/1000)
            rlatmean.append(float(parsed[15]))
            rlatmax.append(float(parsed[14]))
            wlatmean.append(float(parsed[56]))
            wlatmax.append(float(parsed[55]))
        except IndexError:
            poll_res = fio_process.poll()
            if poll_res != None:
                exit_var[0] = poll_res
                return poll_res

def make_cmd(path):
    prefix=['fio', '--minimal', '--eta=0', '--status-interval=1']
    if path.endswith('ini'):
        no_name = '--' + subprocess.Popen(['fio', '--showcmd', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf-8').partition(' --name=')[2].partition(' --')[2]
        fio_cmds = prefix + shlex.split(no_name)
    if not '--group_reporting' in fio_cmds:
        fio_cmds.append('--group_reporting')
    return fio_cmds
