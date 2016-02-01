#!/bin/bash

# Start Xvfb in separate process
start-stop-daemon --start -b -x /usr/bin/Xvfb :99

# start sshd
/usr/sbin/sshd -D
