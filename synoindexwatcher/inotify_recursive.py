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
        self.__tree = {}
        self.__tree_delete_queue = []

    def __add_watch_recursive(self, path, mask, filter, head, tail, parent, loose = True):
        try:
            wd = inotify_simple.INotify.add_watch(self, path, mask | flags.IGNORED | flags.CREATE | flags.MOVED_FROM | flags.MOVED_TO)
        except OSError as e:
            if loose and e.errno == 2:
                logging.debug("Watch-path cannot be found anymore: %s" % path)
                return
            else:
                raise
        name = path if parent == -1 else tail
        if wd in self.__tree:
            if parent != -1:
                old_parent = self.__tree[wd]["parent"]
                del self.__tree[old_parent]["children"][name]
                self.__tree[parent]["children"][name] = wd
            self.__tree[wd]["name"] = name
            self.__tree[wd]["parent"] = parent
            if parent != -1:
                self.__tree[parent]["children"][name] = wd
            logging.debug("Updated info for watch %d: %s" % (wd, self.__tree[wd]))
        else:
            if parent != -1:
                self.__tree[parent]["children"][name] = wd
            self.__tree[wd] = {
                "children": {},
                # TODO Join existing and new filter via `or` or clear existing filter if new one equals `None`.
                "filter": filter,
                "mask": mask,
                "name": name,
                "parent": parent
            }
            logging.debug("Added info for watch %d: %s" % (wd, self.__tree[wd]))
            for entry in os.listdir(path):
                entrypath = os.path.join(path, entry)
                if os.path.isdir(entrypath) and (filter == None or filter(entrypath)):
                    self.__add_watch_recursive(entrypath, mask, filter, path, entry, wd)
        return wd

    def __rm_watch_recursive(self, wd, loose = True):
        if wd in self.__tree:
            children = self.__tree[wd]["children"]
            for name in children:
                self.rm_watch_recursive(children[name])
        try:
            inotify_simple.INotify.rm_watch(self, wd)
        except OSError as e:
            if loose and e.errno == 22:
                logging.debug("Cannot remove watch, because it does not exist anymore: %d" % wd)
                return
            else:
                raise

    def add_watch_recursive(self, path, mask, filter = None):
        (head, tail) = os.path.split(path)
        return self.__add_watch_recursive(path, mask, filter, head, tail, -1, False)

    def get_path(self, wd):
        path = self.__tree[wd]["name"]
        parent = self.__tree[wd]["parent"]
        while parent != -1:
            wd = parent
            path = os.path.join(self.__tree[wd]["name"], path)
            parent = self.__tree[wd]["parent"]
        return path

    def read(self):
        events = []
        remove_queue = {}
        for wd in self.__tree_delete_queue:
            name = self.__tree[wd]["name"]
            parent = self.__tree[wd]["parent"]
            del self.__tree[parent]["children"][name]
            del self.__tree[wd]
            logging.debug("Removed info for watch %d" % (wd))
        self.__tree_delete_queue = []
        for event in inotify_simple.INotify.read(self):
            if event.wd in self.__tree:
                mask = self.__tree[event.wd]["mask"]
                if event.mask & flags.ISDIR:
                    tail = str.encode(event.name)
                    if event.mask & (flags.CREATE | flags.MOVED_TO):
                        filter = self.__tree[event.wd]["filter"]
                        head = self.get_path(event.wd)
                        path = os.path.join(head, tail)
                        self.__add_watch_recursive(path, mask, filter, head, tail, event.wd)
                        if event.mask & flags.MOVED_TO:
                            del remove_queue[event.cookie]
                    elif event.mask & flags.MOVED_FROM:
                        remove_queue[event.cookie] = self.__tree[event.wd]["children"][tail]
                elif event.mask & flags.IGNORED:
                    logging.debug("Going to remove info for watch %d" % (event.wd))
                    self.__tree_delete_queue.append(event.wd)
                if (event.mask & mask):
                    events.append(event)
            else:
                events.append(event)
        for cookie in remove_queue:
            wd = remove_queue[cookie]
            self.rm_watch_recursive(wd)
            logging.debug("Removed watch %d" % (wd))
        return events

    def rm_watch_recursive(self, wd):
        self.__rm_watch_recursive(wd, False)
