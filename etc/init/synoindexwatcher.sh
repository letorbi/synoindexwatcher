#!/bin/sh

case "$1" in
  start|"")
    mkdir -p /var/run/synoindexwatcher
    # Set LC_ALL to ensure that the filesystem encoding is correctly detected
    # during boot.
    env LC_ALL=en_US.utf8 python /opt/synoindexwatcher/synoindexwatcher.py \
      --daemon \
      --logfile /var/log/synoindexwatcher.log \
      --loglevel INFO \
      --pidfile /var/run/synoindexwatcher/init.pid
    ;;
  restart|reload|force-reload)
    echo "Error: argument '$1' not supported" >&2
    exit 3
    ;;
  stop)
    kill `cat /var/run/synoindexwatcher/init.pid`
    ;;
  *)
    echo "Usage: synoindexwatcher.sh [start|stop]" >&2
    exit 3
    ;;
esac
