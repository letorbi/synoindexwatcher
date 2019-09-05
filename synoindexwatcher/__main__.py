#
# This file is part of Synoindex Watcher.
#
# Copyright (c) 2012-2018 Mark Houghton <https://codesourcery.wordpress.com>
# Copyright (c) 2019 Torben Haase <https://pixelsvsbytes.com>
#
# Synoindex Watcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Synoindex Watcher is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.You should have received a copy of the GNU General Public License
# along with Synoindex Watcher.  If not, see <http:#www.gnu.org/licenses/>.
#
################################################################################

import sys
import os
import subprocess
import signal
import argparse
import logging
import time

from inotify_simple import INotify, flags

def process_create(filepath, is_dir):
    arg = ""
    if is_dir:
        arg = "-A"
    else:
        arg = "-a"
    do_index_command(filepath, is_dir, arg)

def process_delete(filepath, is_dir):
    arg = ""
    if is_dir:
        arg = "-D"
    else:
        arg = "-d"
    do_index_command(filepath, is_dir, arg)

def process_modify(filepath, is_dir):
    do_index_command(filepath, is_dir, "-a")
     
def do_index_command(filepath, is_dir, index_argument):
    if is_allowed_path(filepath, is_dir):
        logging.info("synoindex %s %s" % (index_argument, filepath))
        subprocess.call(["synoindex", index_argument, filepath])
    else:
        logging.warning("%s is not an allowed path" % filepath)
     
def is_allowed_path(filepath, is_dir):
    # Don't check the extension for directories
    if not is_dir:
        ext = os.path.splitext(filepath)[1][1:].lower()
        if ext in excluded_exts:
            return False
    if os.path.basename(filepath) == b"@eaDir":
        return False
    return True
 
def add_watch_recursive(inotify, root, name, mask, parent = -1):
  try:
      path = os.path.join(root, name)
      wd = inotify.add_watch(path, mask)
      watch_info[wd] = {
          "name":  path if parent == -1 else name,
        "parent": parent
      }
      logging.debug("Added info for watch %d: %s" % (wd, watch_info[wd]))
      for entry in os.listdir(path):
          entrypath = os.path.join(path, entry)
          if os.path.isdir(entrypath) and is_allowed_path(entrypath, True):
              add_watch_recursive(inotify, path, entry, mask, wd)
  except OSError as e:
    if e.errno == 2:
        logging.debug("Watch-path cannot be found anymore: %s" % path)
        pass
    else:
        raise

def get_watch_path(wd):
  path = watch_info[wd]["name"]
  parent = watch_info[wd]["parent"]
  while parent != -1:
    wd = parent
    path = os.path.join(watch_info[wd]["name"], path)
    parent = watch_info[wd]["parent"]
  return path

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", default=None,
        help="set the log-file for program messages (default: none)")
    parser.add_argument("--loglevel", default="INFO",
        help="set the minimum level that shall be logged (default: INFO)")
    parser.add_argument("--pidfile", default="/var/run/synoindexwatcher.pid",
        help="set the pid-file, if watcher runs as a daemon (default: /var/run/synoindexwatcher.pid)")
    args = parser.parse_args()

    logging.basicConfig(filename=args.logfile, level=getattr(logging, args.loglevel.upper()),
        format="%(asctime)s %(levelname)s %(message)s")
    
    signal.signal(signal.SIGTERM, sigterm)
    
    inotify = INotify()
    mask = flags.DELETE | flags.CREATE | flags.MOVED_TO | flags.MOVED_FROM | flags.MOVE_SELF | flags.MODIFY
    add_watch_recursive(inotify, b"/volume1", b"music", mask)
    add_watch_recursive(inotify, b"/volume1", b"photo", mask)
    add_watch_recursive(inotify, b"/volume1", b"video", mask)

    logging.info("Watching for media file changes...")

    try:
        last_moved_to = None
        while True:
            for event in inotify.read():
                is_dir = event.mask & flags.ISDIR
                root = get_watch_path(event.wd)
                name = str.encode(event.name)
                path = os.path.join(root, name)
                if event.mask & flags.CREATE or event.mask & flags.MOVED_TO:
                  if is_dir and event.mask & flags.CREATE:
                    add_watch_recursive(inotify, root, name, mask, event.wd)
                  if is_dir and event.mask & flags.MOVED_TO:
                    last_moved_to = name
                  process_create(path, is_dir)
                elif event.mask & flags.DELETE or event.mask & flags.MOVED_FROM:
                  process_delete(path, is_dir)
                elif event.mask & flags.MODIFY:
                  process_modify(path, is_dir)
                elif event.mask & flags.MOVE_SELF:
                  watch_info[event.wd]["name"] = last_moved_to
                  logging.debug("Updated info for watch %d: %s" % (event.wd, watch_info[event.wd]))
                elif event.mask & flags.IGNORED:
                  logging.debug("Removing info for watch %d: %s" % (event.wd, watch_info[event.wd]))
                  del watch_info[event.wd]
            # Just wait one second until we query inotify again
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Watching interrupted by user (CTRL+C)")

def sigterm(signal, frame):
    logging.info("Process received SIGTERM signal")
    sys.exit(0)

# TODO The original script only allowed certain extensions.
#      Maybe we should have a whilelist and a blacklist.
excluded_exts = ["tmp"]
watch_info = {}

if __name__ == "__main__":
    try:
        start()
    except Exception:
        logging.exception("An uncaught exception occurred")
        sys.exit(255)
