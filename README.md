# Synoindex Watcher - Automated media index updates

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It watches the
media-folders of your DiskStation an updates the media index every time a file or directory inside the media-folders is
created, deleted or changed. It is written in Python and licensed as open-source under the GPL version 3 License.

The original version was written by Mark Houghton, who [published it in his "codesourcery"
blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/).

## Features

* **Lightweight** No need to install extra Synology packages
* **Intelligent** Executes only if a file has actually been added/deleted/renamed
* **Agnostic** Python 2 and Python 3 compatible (minimum tested version is 2.7)

## Installation

I recommend to use pip for the installation. Synology DiskStations do not have pip installed by default, but you can add
it easily with the following command:

```
# wget https://bootstrap.pypa.io/get-pip.py
# python get-pip.py
```

Now you can enter the install command:

```
# python -m pip install https://github.com/letorbi/synoindexwatcher/archive/master.zip
```

This will install Synoindex Watcher along with its dependencies
[inotify-simple](https://pypi.org/project/inotify_simple/) and [enum](https://pypi.org/project/enum/).

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
