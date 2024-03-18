#!/bin/sh
#  DensitronSetup1U.sh
#  
#
#  Created on 07/11/2023.
#

cd /etc/X11/
file="./xorg.conf"

if [ -f "$file" ] ; then
    echo "xorg.conf already exists"
    echo "Deleting old xorg.conf"
    rm "$file"
fi

echo "Creating xorg.conf"
touch $file
echo "Section \"Files\"" >> $file
echo "  ModulePath \"/usr/lib/xorg/modules\"" >> $file
echo "  ModulePath \"/usr/local/lib/xorg/modules\"" >> $file
echo "  ModulePath \"/usr/local/lib/xorg/modules/drivers\"" >> $file
echo "EndSection" >> $file
echo "" >> $file
echo "Section \"Device\"" >> $file
echo "  Identifier \"DisplayLinkDevice\"" >> $file
echo "  Driver \"fbdev\"" >> $file
echo "  Option \"fbdev\" \"/dev/fb0\"" >> $file
echo "EndSection" >> $file
echo "" >> $file
echo "Section \"Monitor\"" >> $file
echo "  Identifier \"DisplayLinkMonitor\"" >> $file
echo "EndSection" >> $file
echo "" >> $file
echo "Section \"Screen\"" >> $file
echo "  Identifier \"DisplayLinkScreen\"" >> $file
echo "  Device \"DisplayLinkDevice\"" >> $file
echo "  Monitor \"DisplayLinkMonitor\"" >> $file
echo "EndSection" >> $file
echo "" >> $file
echo "Section \"ServerLayout\"" >> $file
echo "  Identifier \"Server Layout\"" >> $file
echo "  Screen 0 \"DisplayLinkScreen\" 0 0" >> $file
echo "EndSection" >> $file

cat $file

echo "Please type in the IP and Port of your SKAARHOJ Touch Raw Panel application.(Example:192.168.11.5:7952)"
echo "Browser will try to reach this IP on startup..."
read ipToUse
echo "Writing display.desktop with IP=$ipToUse"

cd /etc/xdg/autostart/
file2="./display.desktop"

if [ -f "$file2" ] ; then
    echo "display.desktop already exists"
    echo "Deleting old display.desktop"
    rm "$file2"
fi

echo "Creating display.desktop"
touch $file2
echo "[Desktop Entry]" >> $file2
echo "Name=Chrome" >> $file2
echo "Exec=chromium-browser --app=http://$ipToUse --start-fullscreen" >> $file2

cat $file2

echo "Disabling screen-saver"

cd /etc/xdg/lxsession/LXDE-pi/
file3="./autostart"

if [ -f "$file3" ] ; then
    echo "autostart already exists"
    echo "Deleting old autostart"
    rm "$file3"
fi

echo "Creating autostart"
echo touch $file3
echo "@lxpanel --profile LXDE-pi" >> $file3
echo "@pcmanfm --desktop --profile LXDE-pi" >> $file3
echo "@xscreensaver -no-splash" >> $file3
echo "@xset s off" >> $file3
echo "@xset -dpms" >> $file3

cat $file3

echo "Done!"
echo "Do not forget to unplug your HDMI monitor if it is still attached!"
echo "Please reboot your system!"

