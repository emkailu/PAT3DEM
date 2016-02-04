#!/bin/bash

#keep connected with cluster by keeping typing 'bg' when the login window is left in background
#install xdotool; login in a new window; run this script in a new tab; go back to the login tab
#whenever you do not use the login tab, put the login window in background
#tested: works on CentOS6(Genome2), Ubuntu15(lxterminal)

WID_old=`xdotool getwindowfocus|head -1`
while true
do
WID_new=`xdotool getwindowfocus|head -1`
if [ "$WID_new" != "$WID_old" ];then
xdotool type --delay 10 --clearmodifiers --window "$WID_old" "bg"
xdotool key --delay 10 --clearmodifiers --window "$WID_old" "Return"
fi
sleep 5m
done

