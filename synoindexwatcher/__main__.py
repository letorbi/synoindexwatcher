#
#  This file is part of Synoindex Watcher.
#
#  Copyright (c) 2012-2018 Mark Houghton <https://codesourcery.wordpress.com>
#  Copyright (c) 2019-2020 Torben Haase <https://pixelsvsbytes.com>
#
#  Synoindex Watcher is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Synoindex Watcher is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#  details. You should have received a copy of the GNU General Public License
#  along with Synoindex Watcher. If not, see <https://www.gnu.org/licenses/>.
#
################################################################################

import sys
import os
import subprocess
import signal
import argparse
import logging
import time
import configparser
import re

from inotifyrecursive import INotify, flags

from . import constants
from . import files

if sys.version_info.major < 3:
    def __fix_encoding(s):
        if isinstance(s, unicode):
            return s.encode("UTF-8")
        else:
            return s
else:
    def __fix_encoding(s):
        return s

def __add_to_index_recursive(path, name):
    fullpath = os.path.join(path, name)
    is_dir = os.path.isdir(fullpath) 
    if not is_allowed_path(name, -1, is_dir):
        logging.debug("Skipping path %s" % fullpath)
        return
    add_to_index(fullpath, is_dir)
    if is_dir:
        for entry in os.listdir(fullpath):
            __add_to_index_recursive(fullpath, entry)

def call_command(args):
    logging.debug("Calling '%s'" % " ".join(args))
    return subprocess.check_output(args, stderr=subprocess.STDOUT)

def add_to_index_recursive(fullpath):
    (path, name) = os.path.split(fullpath)
    __add_to_index_recursive(path, name)

def add_to_index(fullpath, is_dir):
    if is_dir:
        arg = "-A"
    else:
        arg = "-a"
    call_command(["synoindex", arg, fullpath])

def remove_from_index(fullpath, is_dir):
    if is_dir:
        arg = "-D"
    else:
        arg = "-d"
    call_command(["synoindex", arg, fullpath])

def build_filter(args):
    blacklist = re.compile(args.blacklist) if args.blacklist != None else None;
    whitelist = re.compile(args.whitelist) if args.whitelist != None else None;
    def filter(name, parent, is_dir):
        if whitelist != None and whitelist.search(name) == None:
            return False
        if blacklist != None and blacklist.search(name) != None:
            return False
        return True
    return filter

def read_config():
    config = configparser.ConfigParser(allow_no_value=True,
        default_section="GLOBAL")
    args_length = len(sys.argv)
    args_range = range(1, args_length)
    for i in args_range:
        split_arg = sys.argv[i].split("=")
        if split_arg[0] == "--config":
            if len(split_arg) == 1:
                if i+1 < args_length:
                    split_arg += [sys.argv[i + 1]]
                else:
                    # Will throw an error
                    parse_arguments(config)
            config.read(os.path.expanduser(split_arg[1]))
            break

    loglevel = config.get("GLOBAL", "loglevel", fallback=None)
    if loglevel and not loglevel in constants.ALLOWED_LOGLEVELS:
        print("synoindexwatcher: error: option loglevel: invalid choice: '%s' (choose from '%s')"
            % (loglevel, "', '".join(constants.ALLOWED_LOGLEVELS)))
        sys.exit(1)
    return config

def parse_arguments(config):
    logfile = None if sys.stdout.isatty() else "/var/log/synoindexwatcher.log"
    sections = [__fix_encoding(s) for s in config.sections()]
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='*',
        default=sections if len(sections) else None,
        help="add a directory that shall be watched")
    parser.add_argument("--blacklist",
        default=__fix_encoding(config.get("GLOBAL", "blacklist", fallback=constants.DEFAULT_BLACKLIST)),
        help="define regular-expression for a global blacklist")
    parser.add_argument("--whitelist",
        default=__fix_encoding(config.get("GLOBAL", "whitelist", fallback=constants.DEFAULT_WHITELIST)),
        help="define regular-expression for a global whitelist")
    parser.add_argument("--logfile",
        default=__fix_encoding(config.get("GLOBAL", "logfile", fallback=logfile)),
        help="write log-messages into the file LOGFILE (default: stdout)")
    parser.add_argument("--loglevel",
        choices=constants.ALLOWED_LOGLEVELS,
        default=__fix_encoding(config.get("GLOBAL", "loglevel", fallback="INFO")),
        help="log only messages as or more important than LOGLEVEL (default: INFO)")
    parser.add_argument("--config", default=None,
        help="read the default-configuration from the file CONFIG")
    parser.add_argument("--rebuild-index", action="store_true",
        help="add all allowed files and directories to the index and exit")
    parser.add_argument("--generate-config", action="store_true",
        help="generate and show a configuration-file and exit")
    parser.add_argument("--generate-init", action="store_true",
        help="generate and show an init-script and exit")
    args = parser.parse_args()
    if args.path == []:
        args.path = get_default_paths()
    return args

def get_default_paths():
    for path in constants.DEFAULT_PATHS:
        if not os.path.isdir(path):
            print("synoindexwatcher: error: implicit path '%s' does not exist\n" % path)
            print("Please add the paths you want to watch explicitly to the command line. For example:\n")
            print("python -m synoindexwatcher /volume1/MyMusic /volume1/MyPhotos /volume1/MyVideos\n")
            sys.exit(2)
    return constants.DEFAULT_PATHS

def on_sigterm(signal, frame):
    logging.info("Process received SIGTERM signal")
    sys.exit(0)

def start():
    config = read_config()
    args = parse_arguments(config)

    if args.generate_init:
        print(files.generateInit(sys.argv))
        return

    if args.generate_config:
        print(files.generateConfig(args))
        return

    logging.basicConfig(filename=args.logfile, level=args.loglevel.upper(),
        format="%(asctime)s %(levelname)s %(message)s")

    if args.rebuild_index:
        print("Adding files to media-index (this may take some time)...")
        for path in args.path:
            add_to_index_recursive(path)
        return

    signal.signal(signal.SIGTERM, on_sigterm)

    try:
        inotify = INotify()
        filter = build_filter(args)
        mask = flags.DELETE | flags.CREATE | flags.MOVED_TO | flags.MOVED_FROM | flags.MODIFY | flags.CLOSE_WRITE
        for path in args.path:
            logging.info("Adding watch for path: %s", path)
            inotify.add_watch_recursive(path, mask, filter)

        logging.info("Waiting for media file changes...")
        modified_files = set()
        while True:
            for event in inotify.read():
                is_dir = event.mask & flags.ISDIR
                fullpath = os.path.join(inotify.get_path(event.wd), event.name)
                if event.mask & flags.CREATE or event.mask & flags.MODIFY:
                    if is_dir:
                        add_to_index(fullpath, is_dir)
                    else:
                        modified_files.add(fullpath)
                elif event.mask & flags.MOVED_TO:
                    add_to_index(fullpath, is_dir)
                elif event.mask & flags.DELETE or event.mask & flags.MOVED_FROM:
                    remove_from_index(fullpath, is_dir)
                elif event.mask & flags.CLOSE_WRITE and (fullpath in modified_files):
                    modified_files.remove(fullpath)
                    add_to_index(fullpath, is_dir)
    except OSError as e:
        if e.errno == 28:
            logging.error("No inode watchers left (see https://github.com/letorbi/synoindexwatcher#faq)")
            exit(127)
        raise
    except KeyboardInterrupt:
        logging.info("Watching interrupted by user (CTRL+C)")

if __name__ == "__main__":
    try:
        start()
    except Exception:
        logging.exception("An uncaught exception occurred")
        sys.exit(255)
