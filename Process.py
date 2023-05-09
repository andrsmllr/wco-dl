# -*- coding: utf-8 -*-

import threading

class ProcessParallel(object):
    """Object that performs tasks in parallel using threads"""

    #Thanks https://stackoverflow.com/questions/11968689/python-multithreading-wait-till-all-threads-finished
    def __init__(self, *jobs):
        self.jobs = jobs
        self.processes = []
        self.processes_url = []
        self.processes_extra = []

    def append_process(self, *job, url=None, extra=None):
        """Append a job to the list of jobs"""
        self.jobs = self.jobs + job
        if (url != None and extra != None):
            self.processes_url.append(url)
            self.processes_extra.append(extra)


    def fork_processes(self):
        """Create a new thread and append it to the list of threads"""
        count = -1
        for job in self.jobs:
            try:
                if (count == -1):
                    proc  = threading.Thread(target=job)
                    self.processes.append(proc)
                    count+=1
                else:
                    proc  = threading.Thread(target=job, args=(self.processes_url[count], self.processes_extra[count]))
                    self.processes.append(proc)
                    count+=1
            except Exception:
                pass


    def start_all(self):
        """Start all threads"""
        for proc in self.processes:
            proc.start()

    def join_all(self):
        """Wait until all threads are done"""
        for proc in self.processes:
            proc.join()
