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
        self.__last_moved_to = None
        self.__watch_info = {}
        self.__watch_info_delete_queue = []

    def __add_watch_recursive(self, path, mask, filter, head, tail, parent):
        try:
            wd = inotify_simple.INotify.add_watch(self, path, mask | flags.IGNORED | flags.CREATE | flags.MOVED_TO | flags.MOVE_SELF)
            if wd in self.__watch_info:
                logging.debug("Watch %d already exists: %s" % (wd, self.__watch_info[wd]))
                return wd
            self.__watch_info[wd] = {
                # TODO Join existing and new filter via `or` or clear existing filter if new one equals `None`.
                "filter": filter,
                "mask": mask,
                "name": path if parent == -1 else tail,
                "parent": parent
            }
            logging.debug("Added info for watch %d: %s" % (wd, self.__watch_info[wd]))
        except OSError as e:
            if e.errno == 2:
                logging.debug("Watch-path cannot be found anymore: %s" % path)
                pass
            else:
                raise
        for entry in os.listdir(path):
            entrypath = os.path.join(path, entry)
            if os.path.isdir(entrypath) and (filter == None or filter(entrypath)):
                self.__add_watch_recursive(entrypath, mask, filter, path, entry, wd)
        return wd

    def add_watch_recursive(self, path, mask, filter = None):
        (head, tail) = os.path.split(path)
        return self.__add_watch_recursive(path, mask, filter, head, tail, -1)

    def get_path(self, wd):
        path = self.__watch_info[wd]["name"]
        parent = self.__watch_info[wd]["parent"]
        while parent != -1:
            wd = parent
            path = os.path.join(self.__watch_info[wd]["name"], path)
            parent = self.__watch_info[wd]["parent"]
        return path

    def read(self):
        events = []
        for wd in self.__watch_info_delete_queue:
            logging.debug("Removing info for watch %d: %s" % (wd, self.__watch_info[wd]))
            del self.__watch_info[wd]
        self.__watch_info_delete_queue = []
        for event in inotify_simple.INotify.read(self):
            if event.wd in self.__watch_info:
                mask = self.__watch_info[event.wd]["mask"]
                if event.mask & (flags.ISDIR | flags.CREATE | flags.MOVED_TO) > flags.ISDIR:
                    filter = self.__watch_info[event.wd]["filter"]
                    head = self.get_path(event.wd)
                    tail = str.encode(event.name)
                    path = os.path.join(head, tail)
                    self.__add_watch_recursive(path, mask, filter, head, tail, event.wd)
                    if event.mask & flags.MOVED_TO:
                        self.__last_moved_to = [str.encode(event.name), event.wd] # name, parent
                elif event.mask & flags.MOVE_SELF:
                    if self.__last_moved_to != None and self.__last_moved_to[1] in self.__watch_info:
                      self.__watch_info[event.wd]["name"] = self.__last_moved_to[0]
                      self.__watch_info[event.wd]["parent"] = self.__last_moved_to[1]
                      logging.debug("Updated info for watch %d: %s" % (event.wd, self.__watch_info[event.wd]))
                    else:
                      logging.debug("Going to remove watch %d" % (event.wd))
                      inotify_simple.INotify.rm_watch(self, event.wd)
                    self.__last_moved_to = None
                elif event.mask & flags.IGNORED:
                    logging.debug("Queueing info for watch %d for removal" % (event.wd))
                    self.__watch_info_delete_queue.append(event.wd)
                if (event.mask & mask):
                    events.append(event)
            else:
                events.append(event)
        return events
