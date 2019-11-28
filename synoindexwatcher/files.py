#
#  This file is part of Synoindex Watcher.
#
#  Copyright (c) 2012-2018 Mark Houghton <https://codesourcery.wordpress.com>
#  Copyright (c) 2019 Torben Haase <https://pixelsvsbytes.com>
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

def generateConfig(args):
    logfile = args.logfile if args.logfile else ""
    content = "[GLOBAL]\nlogfile=%s\nloglevel=%s" % (logfile, args.loglevel)
    for path in args.path:
        content += "\n\n[%s]" % path
    return content
