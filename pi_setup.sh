#!/bin/bash

sudo apt install avrdude

echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
echo "dwc2" | sudo tee -a /etc/modules
echo "g_serial" | sudo tee -a /etc/modules

echo "Done, you should do a reboot now"
