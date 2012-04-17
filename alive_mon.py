#!/usr/bin/env python

import subprocess
import os
import time


class Program(object):
    def __init__(self, settings):
        self.process = None
        self.cmd = settings['cmd']

        if 'args' in settings:
            self.cmd += [x for x in settings['args'].split(' ')]

        self.cwd = ""
        if 'cwd' in settings:
            self.cwd = os.path.expanduser(settings['cwd'])

    def getCommand(self):
        return self.cmd

    def run(self):
        self.exec_path = self.getCommand()

        print 'start =>', self.exec_path

        if self.cwd != "":
            self.process = subprocess.Popen(self.exec_path, cwd=self.cwd, shell=True)
        else:
            self.process = subprocess.Popen(self.exec_path, shell=True)

    def kill(self):
        if not self.process:
            return

        if subprocess.mswindows:
            subprocess.Popen('taskkill /F /T /PID %i' % self.process.pid,
                shell=True)
        else:
            subprocess.Popen('kill %i' % self.process.pid, shell=True)

        self.process = None

    def getPID(self):
        if not self.process:
            return 0
        return self.process.pid

    def isRunning(self):
        if not self.process:
            return False
        return self.process.poll() == None


if __name__ == '__main__':
    import json

    jsonfile = 'settings.json'
    o = json.load(open(jsonfile))

    targets = []
    time_range = None

    start_time = None
    end_time = None

    if 'time_range' in o:
        tt = o["time_range"]

        def time_to_int(st):
            arr = st.split(":")
            return int(arr[0]) * 60 + int(arr[1])

        if "start" in tt:
            start_time = time_to_int(tt["start"])
        if "end" in tt:
            end_time = time_to_int(tt["end"])

    for i in o["target"]:
        p = Program(i)
        targets.append(p)

    while True:
        cur_hour = time.localtime().tm_hour
        cur_min = time.localtime().tm_min
        t = cur_hour * 60 + cur_min

        if end_time and t >= end_time:
            print 'timeover => %s' % (o["time_range"]["end"])
            for i in targets:
                i.kill()
            for i in o["on_exit"]:
                Program(i).run()
            exit()

        time.sleep(1)

        if start_time and t < start_time:
            print 'waiting => %s' % (o["time_range"]["start"])
            continue

        for i in targets:
            if not i.isRunning():
                i.run()

