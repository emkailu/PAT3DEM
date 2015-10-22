#!/bin/bash

#keep typing 'p3download.py d.txt\n' when the login window is left in background
#install xdotool; login in a new window; run this script in a new tab; go back to the login tab
#put the login window in background

WID_old=`xdotool getwindowfocus|head -1`
while true
do
WID_new=`xdotool getwindowfocus|head -1`
if [ "$WID_new" != "$WID_old" ];then
xdotool type --delay 10 --clearmodifiers --window "$WID_old" "p3download.py d.txt &"
xdotool key --delay 10 --clearmodifiers --window "$WID_old" "Return"
fi
sleep 30s
done

