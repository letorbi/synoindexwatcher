#!/bin/sh

# https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/

case "$1" in
  start|"")
    env LC_ALL=en_US.utf8 python /opt/synoindexwatcher/synoindexwatcher.py --daemon --logfile /opt/synoindexwatcher/synoindexwatcher.py --loglevel INFO
    ;;
  restart|reload|force-reload)
    echo "Error: argument '$1' not supported" >&2
    exit 3
    ;;
  stop)
    kill `cat /var/run/synoindexwatcher.pid`
    ;;
  *)
    echo "Usage: synoindexwatcher.sh [start|stop]" >&2
    exit 3
    ;;
esac
