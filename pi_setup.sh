#!/bin/bash

sudo apt install avrdude python3 python3-pip
python3 -m pip install pyserial

echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
echo "dwc2" | sudo tee -a /etc/modules
echo "g_serial" | sudo tee -a /etc/modules

# TODO: enable ttyS0 serial
echo "Done, you should do a reboot now"
