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

import logging
import os

from inotify_simple import *

class INotify(inotify_simple.INotify):
    def __init__(self):
        inotify_simple.INotify.__init__(self)
        self.__info = {}
        self.__cleanup_queue = []

    def __add_info(self, wd, name, mask, filter, parent):
        self.__info[wd] = {
            "children": {},
            "filter": filter,
            "mask": mask,
            "name": name,
            "parent": parent
        }
        if parent != -1:
            self.__info[parent]["children"][name] = wd
        logging.debug("Added info for watch %d: %s" % (wd, self.__info[wd]))

    def __clr_info(self, wd):
        self.__cleanup_queue.append(wd)
        logging.debug("Enlist info for watch %d for clean-up" % (wd))

    def __clr_infos(self):
        for wd in self.__cleanup_queue:
            self.__rm_info(wd)
        self.__cleanup_queue = []

    def __set_info(self, wd, name, parent):
        old_parent = self.__info[wd]["parent"]
        if old_parent != -1:
            old_name = self.__info[wd]["name"]
            del self.__info[old_parent]["children"][old_name]
        self.__info[wd]["name"] = name
        self.__info[wd]["parent"] = parent
        if parent != -1:
            self.__info[parent]["children"][name] = wd
        logging.debug("Updated info for watch %d: %s" % (wd, self.__info[wd]))

    def __rm_info(self, wd):
        name = self.__info[wd]["name"]
        parent = self.__info[wd]["parent"]
        del self.__info[parent]["children"][name]
        del self.__info[wd]
        logging.debug("Removed info for watch %d" % (wd))

    def __add_watch_recursive(self, path, mask, filter, tail, parent, loose = True):
        try:
            wd = inotify_simple.INotify.add_watch(self, path, mask | flags.IGNORED | flags.CREATE | flags.MOVED_FROM | flags.MOVED_TO)
            logging.debug("Added watch %d" % (wd))
        except OSError as e:
            if loose and e.errno == 2:
                logging.debug("Cannot add watch, path not found: %s" % path)
                return
            else:
                raise
        name = path if parent == -1 else tail
        if wd in self.__info:
            self.__set_info(wd, name, parent)
        else:
            self.__add_info(wd, name, mask, filter, parent)
            for entry in os.listdir(path):
                entrypath = os.path.join(path, entry)
                if os.path.isdir(entrypath) and (filter == None or filter(entrypath)):
                    self.__add_watch_recursive(entrypath, mask, filter, entry, wd)
        return wd

    def __rm_watch_recursive(self, wd, loose = True):
        if wd in self.__info:
            children = self.__info[wd]["children"]
            for name in children:
                self.rm_watch_recursive(children[name])
            try:
                inotify_simple.INotify.rm_watch(self, wd)
                logging.debug("Removed watch %d" % (wd))
            except OSError as e:
                if loose and e.errno == 22:
                    logging.debug("Cannot remove watch, descriptor does not exist: %d" % wd)
                    return
                else:
                    raise

    def add_watch_recursive(self, path, mask, filter = None):
        tail = os.path.split(path)[1]
        return self.__add_watch_recursive(path, mask, filter, tail, -1, False)

    def rm_watch_recursive(self, wd):
        self.__rm_watch_recursive(wd, False)

    def get_path(self, wd):
        path = self.__info[wd]["name"]
        parent = self.__info[wd]["parent"]
        while parent != -1:
            wd = parent
            path = os.path.join(self.__info[wd]["name"], path)
            parent = self.__info[wd]["parent"]
        return path

    def read(self):
        self.__clr_infos()
        events = []
        moved_from = {}
        for event in inotify_simple.INotify.read(self):
            if event.wd in self.__info:
                info = self.__info[event.wd]
                mask = info["mask"]
                if event.mask & flags.ISDIR:
                    tail = str.encode(event.name)
                    if event.mask & (flags.CREATE | flags.MOVED_TO):
                        path = os.path.join(self.get_path(event.wd), tail)
                        self.__add_watch_recursive(path, mask, info["filter"], tail, event.wd)
                        if event.mask & flags.MOVED_TO and event.cookie in moved_from:
                            del moved_from[event.cookie]
                    elif event.mask & flags.MOVED_FROM:
                        moved_from[event.cookie] = info["children"][tail]
                elif event.mask & flags.IGNORED:
                    self.__clr_info(event.wd)
                if (event.mask & mask):
                    events.append(event)
            else:
                events.append(event)
        for cookie in moved_from:
            self.rm_watch_recursive(moved_from[cookie])
        return events
