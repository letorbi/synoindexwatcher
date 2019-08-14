Synoindex Watcher - A media watcher for Synology DiskStations
=============================================================

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It updates the
media index every time a file or directory inside the media-folders is created, deleted or changed. It is written in
Python and licensed as open-source under the GPL version 3 License.

The original version was written by Mark Houghton, who [published it in his "codesourcery"
blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/).

## Features

* Python 2 and Python 3 compatible (minimum version is 2.4)
* Uses inotify to watch for changes

## Installation

```
# pip install https://github.com/letorbi/pyinotify
# git clone https://github.com/letorbi/synoindexwatcher /opt
```

If you want to start the daemon automatically during boot:

```
ln -s /opt/synoindexwatcher/etc/init/synoindexwatcher.sh /usr/local/etc/rc.d/S99synoindexwatcher.sh
```

----

Copyright 2019 Torben Haase \<https://pixelsvsbytes.com>
