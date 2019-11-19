# Synoindex Watcher - Automated media index updates

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It watches the
media-folders of your DiskStation an updates the media index every time a file or directory inside the media-folders is
created, deleted or changed. It is written in Python and licensed as open-source under the GPL version 3.

The original version was written by Mark Houghton, who [published it in his "codesourcery"
blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/).

## Features

* **Lightweight** No need to install extra Synology packages
* **Intelligent** Executes only if a file has actually been added/deleted/renamed
* **Agnostic** Python 2 and Python 3 compatible (minimum tested version is 2.7)

## Installation

Synoindex Watcher cannot be installed via Synology's Package Center. You have to log in via SSH and use the terminal.
I recommend to use pip for the installation. Synology DiskStations do not have pip installed by default, but you can
add it easily with the following command:

```
$ wget https://bootstrap.pypa.io/get-pip.py -qO - | sudo python
```

Now you can install the synoindexwatcher module:

```
$ sudo python -m pip install https://github.com/letorbi/synoindexwatcher/archive/master.zip
```

This will also install its dependency [inotifyrecursive](https://pypi.org/project/inotifyrecursive/).

## Usage

You can start Synoindex Watcher with the following command:

```
$ python -m synoindexwatcher
```

Add `-h` or `--help` to see the list of available parameters:

```
$ python -m synoindexwatcher --help
```

### Start on boot

Synoindex Watcher can also be run as a daemon. Use the following commands to create an init-script that starts
Synoindex Watcher in the background when your DiskStation boots:

```
$ python -m synoindexwatcher --generate-init | sudo tee /usr/local/etc/rc.d/S99synoindexwatcher.sh
$ sudo chmod a+x /usr/local/etc/rc.d/S99synoindexwatcher.sh
```

You can also use the saved init-script to stop and start the Synoindex Watcher daemon:

```
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh stop
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh start
```

## FAQ

### I'm getting `OSError: [Errno 28] No space left on device`

This actually does not mean that you run out of disk space, but rather that your system does not allow enough
inode-watchers to watch all your media files. The message is quite confusing, though.

To fix this temporarily you could simply type `echo 204800 > /proc/sys/fs/inotify/max_user_watches` as root. The maximum
number of inode-watchers in the user-space would be 204800 afterwards, which should be enough for most use-cases.
Unfortunately this fixes the problem only until the next reboot.

For a permanent solution it is recommended to add the line `fs.inotify.max_user_watches = 204800` to the file
*/etc/sysctl.conf*. This should set the maximum value during boot, but I had to add an init-script that executes
`sysctl -p /etc/sysctl.conf` to make it work. The simplest way would be to add the command to the start-section of the
init-script for Synonindex Watcher.

----

Copyright 2019 Torben Haase \<[https://pixelsvsbytes.com](https://pixelsvsbytes.com)>
