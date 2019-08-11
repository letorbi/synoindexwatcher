# https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/

from __future__ import print_function

import sys
import os.path
from subprocess import call
import signal

import argparse
import pyinotify

log_file = open("/var/log/synoindexwatcher.log", "a")
     
def log(text):
    log_file.write(text + "\n")
    log_file.flush()
     
# TODO The original script only allowed certain extensions - we should have a whilelist and a blacklist.
excluded_exts = ["tmp"]
 
class EventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        self.modified_files = set()
         
    def process_IN_CREATE(self, event):
        self.process_create(event)
     
    def process_IN_MOVED_TO(self, event):
        self.process_create(event)
         
    def process_IN_MOVED_FROM(self, event):
        self.process_delete(event)
         
    def process_IN_DELETE(self, event):
        self.process_delete(event)
     
    def process_create(self, event):
        arg = ''
        if event.dir:
            arg = "-A"
        else:
            arg = "-a"
        self.do_index_command(event, arg)
     
    def process_delete(self, event):
        arg = ''
        if event.dir:
            arg = "-D"
        else:
            arg = "-d"
        self.do_index_command(event, arg)
         
    def process_IN_MODIFY(self, event):
        if self.is_allowed_path(event.pathname, event.dir):
            self.modified_files.add(event.pathname)
                 
    def process_IN_CLOSE_WRITE(self, event):
        # ignore close_write unlesss the file has previously been modified.
        if (event.pathname in self.modified_files):
            self.do_index_command(event, "-a")
         
    def do_index_command(self, event, index_argument):
        if self.is_allowed_path(event.pathname, event.dir):
            log("synoindex %s %s" % (index_argument, event.pathname))
            call(["synoindex", index_argument, event.pathname])
             
            # Remove from list of modified files.
            try:
                self.modified_files.remove(event.pathname)
            except KeyError:
                # Don't care.
                pass
        # TODO Reactivate this once we have different log levels
        #else:
        #    log("%s is not an allowed path" % event.pathname)
         
             
    def is_allowed_path(self, filename, is_dir):
        # Don't check the extension for directories
        if not is_dir:
            ext = os.path.splitext(filename)[1][1:].lower()
            if ext in excluded_exts:
                return False
        if filename.find("@eaDir") > 0:
            return False
        return True


def start():
    log("Starting")

    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', action="store_const", const=True, default=False,
        help='run watcher as a daemon')
    parser.add_argument('--pidfile', default="/var/run/synoindexwatcher.pid",
        help='set pid-file, if watcher runs as a daemon')
    args = parser.parse_args()

    mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM  # watched events
    handler = EventHandler()
    wm = pyinotify.WatchManager()  # Watch Manager
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(["/volume1/music", "/volume1/photo", "/volume1/video"], mask, rec=True, auto_add=True)

    notifier.loop(daemonize=args.daemon, pid_file=args.pidfile)

def stop(signal, frame):
    log("Exiting")
    sys.exit(0)

signal.signal(signal.SIGTERM, stop)
start()
