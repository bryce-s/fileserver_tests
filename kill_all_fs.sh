#!/usr/bin/bash
set -e
set -x
ps -ef | grep fs | grep -v grep | grep -v make | grep -v kdev | cut -c 10-14 | xargs kill -9

