#!/bin/bash

#keep connected with cluster by keeping typing 'bg' when the login window is left in background
#install xdotool; login in a new window; run this script in a new tab; go back to the login tab
#whenever you do not use the login tab, put the login window in background

WID_out=`xdotool getwindowfocus|head -1`
while true
do
WID=`xdotool getwindowfocus|head -1`
if [ "$WID" != "$WID_out" ];then
xdotool set_window --name "$WID_out" "$WID_out"
xdotool search --name "$WID_out" key b key g key "Return"
fi
sleep 5m
done

