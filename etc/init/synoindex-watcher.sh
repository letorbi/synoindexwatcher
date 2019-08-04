#!/bin/sh

# https://codesourcery.wordpress.com/2012/11/29/more-on-the-synology-nas-automatically-indexing-new-files/

case "$1" in
  start|"")
    #start the monitoring daemon
    synoindex-watcher
    ;;
  restart|reload|force-reload)
    echo "Error: argument '$1' not supported" >&2
    exit 3
    ;;
  stop)
    kill `cat /var/run/synoindex-watcher.pid`
    ;;
  *)
    echo "Usage: synoindex-watcher.sh [start|stop]" >&2
    exit 3
    ;;
esac
