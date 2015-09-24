#!/bin/bash

#keep typing 'p3download.py f.txt\n' when the login window is left in background
#install xdotool; login in a new window; run this script in a new tab; go back to the login tab
#put the login window in background

WID_old=`xdotool getwindowfocus|head -1`
while true
do
WID_new=`xdotool getwindowfocus|head -1`
if [ "$WID_new" != "$WID_old" ];then
xdotool key --delay 10 --clearmodifiers --window "$WID_old" p+3+d+o+w+n+l
xdotool key --delay 10 --clearmodifiers --window "$WID_old" o+a+d+"period"+p+y+"space"
xdotool key --delay 10 --clearmodifiers --window "$WID_old" f+"period"+t+x+t+"space"+"shift"+7
xdotool key --delay 10 --clearmodifiers --window "$WID_old" "Return"
fi
sleep 30s
done

