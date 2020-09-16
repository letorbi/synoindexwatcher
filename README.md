# Synoindex Watcher - Automated media index updates

Synoindex Watcher is a media index updater for Synology DiskStations based on inotify and synoindex. It watches the media-folders of your DiskStation an updates the media index every time a file or directory inside the media-folders is created, deleted or changed. It is written in Python and licensed as open-source under the GPL version 3.

The original version was written by Mark Houghton, who [published it in his "codesourcery" blog](https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/). However, most of the original code has been replaced or rewritten by now.

*This Python package is currently in beta-stage. All planned features are implemented, it is working and used on a number of devices. The only thing that's missing are some automated testing-routines, so there could still be undiscovered bugs.*

## Features

* **Lightweight** No need to install extra Synology packages
* **Intelligent** Executes only if a file has actually been added/deleted/renamed
* **Agnostic** Python 2 and Python 3 compatible (minimum tested version is 2.7)

## Installation

Synoindex Watcher cannot be installed via Synology's Package Center. You have to log in via SSH and use the terminal.  I recommend to use pip for the installation. Synology DiskStations do not have pip installed by default, but you can add it easily with the following command:

```
$ wget https://bootstrap.pypa.io/get-pip.py -qO - | sudo python
```

Now you can install the Synoindex Watcher module:

```
$ sudo python -m pip install --upgrade synoindexwatcher
```

You can use the same command to upgrade Synoindex Watcher from an older version.

This will also install its dependency [inotifyrecursive](https://pypi.org/project/inotifyrecursive/) and also [configparser](https://pypi.org/project/configparser/), if you use Python <= 3.5.

## Usage

You can start Synoindex Watcher with the following command:

```
$ python -m synoindexwatcher
```

Synoindex Watcher will watch the directories */volume1/music*, */volume1/photo* and */volume1/video* by default.  You can change this, as well as some other things, by adding some [command-line arguments](#command-line-arguments) or using a [configuration-file](#configuration-file). You can also use an init-script to [start Synoindex Watcher on boot](#start-on-boot).

### Command-line arguments

The default behaviour of Synoindex Watcher can be changed with various command-line arguments:

* `path [path]`: By appending one or more paths to the command-line you can define which directories shall be watched by synoindexwatcher. For example `python -m synoindexwatcher /home/me/Music` will tell Synoindex Watcher to watch only the directory */home/me/Music*.

* `--blacklist=regex`: Define a regular-expression for a global blacklist. For example `python -m synoindexwatcher --blacklist="foo|bar"` will tell Synoindex Watcher ignore files and directories with `foo` or `bar` in their name. The default regular-expression is `^\.|^\@|\.tmp$`, which means that files and directories are ignored if they start with `.` or `@` or end with `.tmp`. The blacklist is applied after the whitelist.

* `--whitelist=regex`: Define a regular-expression for a global whitelist. For example `python -m synoindexwatcher --whitelist="foo|bar"` will tell Synoindex Watcher to watch only files and directories with `foo` or `bar` in their name. The default regular-expression is empty, which means that all files and directories, which are not blacklisted, are added to the media-index. The whitelist is applied before the blacklist.

* `--logfile=file`: Write log-messages to the specified file. For example `python -m synoindexwatcher --logfile=/home/me/watcher.log` will tell Synoindex Watcher to write into the file */home/me/watcher.log*. By default Synoindex Watcher will write to the terminal, if it is attached to one, or to */var/log/synoindexwatcher.log* otherwise.

* `--loglevel=value`: Synoindex Watcher logs errors, warnings and informational messages by default. You can change this by setting the log-level to either `DEBUG`, `INFO`, `WARNING` or `ERROR`. For example `python -m synoindexwatcher --loglevel=DEBUG` will also log (a lot of) debugging messages along with errors, warnings and infos.

* `--config=file`: Get the default-configuration from a certain file. For example `python -m synoindexwatcher --config=/etc/synoindexwatcher.conf` will tell Synoindex Watcher to use the values in */etc/synoindexwatcher.conf* as its default-values. Any additional command-line arguments will override the values read from the configuration-file.

* `--rebuild-index`: Add all allowed files and directories in the watched directories and exit afterwards. Use it, if your media-index lacks entries for existing files. Read the [related FAQ-entry](#the-media-index-contains-entries-for-files-that-do-not-exist), if you want to remove non-existing files from the media-index.

* `--generate-init`: Generate an init-script, write it to the standard output and exit afterwards. Any additional command-line arguments will be integrated into the generated script. See the [start on boot](#start-on-boot) section above for further details.

* `--generate-config`: Generate a configuration-file, write it to the standard output and exit afterwards. Any additional command-line arguments will be integrated into the generated configuration. See the [configuration-file](#configuration-file) section below for further details.

* `--help`: Write a short online help to the standard output and exit afterwards.

### Configuration-file

The default behaviour of Synoindex Watcher can also be changed via a configuration-file instead of command-line arguments. Use the following command to create a configuration file:

```
python -m synoindexwatcher --generate-config | sudo tee /usr/local/etc/synoindexwatcher.conf
```

The generated file is split into several sections: The section `[GLOBAL]` may contain default-values for some [command-line arguments](#command-line-arguments), while each of the other sections (e.g. `[/volume1/music]`) represents a directory that shall be watched. The directory-sections contain no values so far.

You have to explicitly tell Synoindex Watcher to use a configuration-file by calling it like this:

```
python -m synoindexwatcher --config=/usr/local/etc/synoindexwatcher.conf
```

Keep in mind, that you can use additional command-line arguments to override the values from the configuration-file.

### Start on boot

Use the following commands to create an init-script that starts Synoindex Watcher in the background when your DiskStation boots:

```
$ python -m synoindexwatcher --generate-init | sudo tee /usr/local/etc/rc.d/S99synoindexwatcher.sh
$ sudo chmod a+x /usr/local/etc/rc.d/S99synoindexwatcher.sh
```

Please note that any messages are written into the file */var/log/synoindexwatcher.log*, if Synoindex Watcher is running as a background process. You can use the `--logfile` parameter to write the output to another file.

Also other command-line arguments will be integrated into the init-script. The following line will generate an init-script that tells Synoindex Watcher to watch only the directory */home/me/Music* and to log messages to */home/me/watcher.log*:

```
$ python -m synoindexwatcher --generate-init --logfile=/home/me/watcher.log /home/me/Music
```

It is recommended to use a configuration file along with the init script, because it allows you to change the behaviour of Synoindex Watcher without the need to regenerate the init-script after every change. Assuming you have created a configuration-file with the commands in the previous section, you can use the following line to generate an init-script that recognizes this file:

```
$ python -m synoindexwatcher --generate-init --config=/usr/local/etc/synoindexwatcher.conf
```

## FAQ

### I'm getting `OSError: [Errno 28] No space left on device`

This actually does not mean that you run out of disk space, but rather that your system does not allow enough inode-watchers to watch all your media files. The message is quite confusing, though.

To fix this temporarily you could simply type `echo 204800 > /proc/sys/fs/inotify/max_user_watches` as root. The maximum number of inode-watchers in the user-space would be 204800 afterwards, which should be enough for most use-cases.  Unfortunately this fixes the problem only until the next reboot.

For a permanent solution it is recommended to add the line `fs.inotify.max_user_watches = 204800` to the file */etc/sysctl.conf*. This should set the maximum value during boot, but I had to add an init-script that executes `sysctl -p /etc/sysctl.conf` to make it work. The simplest way would be to add the command to the start-section of the init-script for Synonindex Watcher.

### The media-index contains entries for files that do not exist

To get rid of entries for non-existing files in the media-index, you have to clear the whole media-index and repopulate it afterwards. Since this requires to modify the database directly with SQL-commands, *it is strongly recommended to create a backup* before executing the following commands that clear the media-index tables:

```
$ sudo synoservice --hard-stop synoindexd
$ psql mediaserver -tAc "SELECT string_agg(tablename, ',') from pg_catalog.pg_tables WHERE tableowner = 'MediaIndex'"
$ psql mediaserver -c  "TRUNCATE `psql mediaserver -tAc "SELECT string_agg(tablename, ',') from pg_catalog.pg_tables WHERE tableowner = 'MediaIndex'"` RESTART IDENTITY"
$ sudo synoservice --start synoindexd"

```
Afterwards you can use Synoindex Watcher to repopulate the media-index:

```
$ python -m synoindexwatcher --rebuild-index
```

Make sure to add additional arguments like `--config` or the paths you want to watch.

----

Copyright (c) 2019-2020 Torben Haase \<[https://pixelsvsbytes.com](https://pixelsvsbytes.com)>
