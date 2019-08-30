# Synoindex Watcher - Automated media index updates

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It watches the
media-folders of your DiskStation an updates the media index every time a file or directory inside the media-folders is
created, deleted or changed. It is written in Python and licensed as open-source under the GPL version 3 License.

The original version was written by Mark Houghton, who [published it in his "codesourcery"
blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/).

## Features

* **Lightweight** No need to install extra Synology packages
* **Intelligent** Uses inotify to watch for changes
* **Agnostic** Python 2 and Python 3 compatible (minimum version is 2.4)

## Installation

I recommend to use pip for the installation. Synology DiskStations do not have pip installed by default, but you can add
it easily with the following command:

```
# wget https://bootstrap.pypa.io/get-pip.py
# python get-pip.py
```

Synoindex Watcher relies on pyinotify, but unfortunately the current version of it requires [a small fix](https://github.com/letorbi/pyinotify/commit/19c0e05532784e9b736b3ab960dc256b8d69ba6c) to work with
Synology's default Python installation. Therefore you have to install my forked version instead:

```
# python -m pip install https://github.com/letorbi/pyinotify/archive/master.zip
```

Now we can finally install Synoindex Watcher:

```
# python -m pip install https://github.com/letorbi/synoindexwatcher/archive/master.zip
```

## Usage

You can start Synoindex Watcher with the following command:

```
$ python -m synoindexwatcher
```

Add `-h` or `--help` to see the list of available parameters:

```
$ python -m synoindexwatcher --help
```

### Init script

The repository also contains an init-script that can be used to start and stop Synoindex Watcher as a daemon. Assuming
you've cloned the repository into */opt/synoindexwatcher*, you can use it to start and stop the daemon:

```
# /opt/synoindexwatcher/etc/init/synoindexwatcher.sh start
# /opt/synoindexwatcher/etc/init/synoindexwatcher.sh stop
```

Just create a link to the init-script, if you want to start the daemon automatically when your Synology DiskStation
boots:

```
# ln -s /opt/synoindexwatcher/etc/init/synoindexwatcher.sh /usr/local/etc/rc.d/S99synoindexwatcher.sh
```


----

Copyright 2019 Torben Haase \<https://pixelsvsbytes.com>
