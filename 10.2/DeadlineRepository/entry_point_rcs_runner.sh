#!/bin/bash


if [ ! -f /var/lib/Thinkbox/Deadline10/deadline.ini ]; then
    echo "deadline.ini not found.";
    exit 1;
fi;


/opt/Thinkbox/Deadline10/bin/deadlinercs
