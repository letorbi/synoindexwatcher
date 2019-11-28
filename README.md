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
$ sudo python -m pip install --upgrade https://github.com/letorbi/synoindexwatcher/archive/master.zip
```

This will also install its dependency [inotifyrecursive](https://pypi.org/project/inotifyrecursive/). You can use the same command to upgrade Synoindex Watcher from an older version.

## Usage

You can start Synoindex Watcher with the following command:

```
$ python -m synoindexwatcher
```

Synoindex Watcher will watch the directories */volume1/music*, */volume1/photo* and */volume1/video* by default.  You can change this, as well as some other things, by adding some [command-line arguments](#command-line-arguments) or using a [configuration-file](#configuration-file).

### Start on boot

Use the following commands to create an init-script that starts Synoindex Watcher in the background when your DiskStation boots:

```
$ python -m synoindexwatcher --generate-init | sudo tee /usr/local/etc/rc.d/S99synoindexwatcher.sh
$ sudo chmod a+x /usr/local/etc/rc.d/S99synoindexwatcher.sh
```

You can also use the saved init-script to start and stop the Synoindex Watcher background process manually:

```
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh start
$ sudo /usr/local/etc/rc.d/S99synoindexwatcher.sh stop
```

### Command-line arguments

The default behaviour of Synoindex Watcher can be changed with various command-line arguments:

* `path [path]`: By appending one or more paths to the command-line you can define which directories shall be watched by synoindexwatcher. For example `python -m synoindexwatcher /home/me/Music` will tell Synoindex Watcher to watch only the directory */home/me/Music*.

* `--logfile=file`: By default everything is written to the standard output (aka the console), but for example `python -m synoindexwatcher --logfile=/var/log/synoindexwatcher.log` will tell Synoindex Watcher to write its output into the file */var/log/synoindexwatcher.log*

* `--loglevel=value`: Synoindex Watcher logs errors, warnings and informational messages by default. You can chanage this by setting the log-level to either `DEBUG`, `INFO`, `WARN` or `ERROR`. For example `python -m synoindexwatcher --loglevel=DEBUG` will also log (a lot of) debugging messages along with errors, warnings and infos.

* `--config=file`: Get the default-configuration from a certain file. For example `python -m synoindexwatcher --config=/etc/synoindexwatcher.conf` will tell Synoindex Watcher to use the values in */etc/synoindexwatcher.conf* as its default-values. Any additional command-line arguments will override the values read from the configuration-file.

* `--generate-init`: Generate an init-script, write it to the standard output and exit afterwards. Any additional command-line arguments will be integrated into the generated script. See the [start on boot](#start-on-boot) section above for further details.

* `--generate-config`: Generate a configuration-file, write it to the standard output and exit afterwards. Any additional command-line arguments will be integrated into the generated configuration. See the [configuration-file](#configuration-file) section below for further details.

* `--help`: Write a short online help to the standard output and exit afterwards.

### Configuration-file

The default behaviour of Synoindex Watcher can also be changed via a configuration-file instead of command-line arguments. Use the following command to generate a configuration file:

```
python -m synoindexwatcher --generate-config | sudo tee /usr/local/etc/synoindexwatcher.conf
```

The generated file is splittet into several sections: The section `[GLOBAL]` may contain default-values for some [command-line arguments](#command-line-arguments), while each of the other sections (e.g. `[/volume1/music]`) represents a directory that shall be watched. The directory-sections contain no values so far.

You have to explicitly tell Synoindex Watcher to use a configuration-file by calling it like this:

```
python -m synoindexwatcher --config=/usr/local/etc/synoindexwatcher.conf
```

Keep in mind, that you can use additional command-line arguments to override the values from the configuration-file.

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
