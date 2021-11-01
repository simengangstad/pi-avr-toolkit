# pi-avr-toolkit

Toolkit to use a Raspberry PI as a programmer for an AVR. For setup on the Raspberry PI, run the `pi_setup.sh`.

## How to use

The Raspberry PI works as a bridge between the host computer where the code is written and the AVR.

1. On the Raspberry PI, run `./main.py bridge`. The PI will then work as a bridge which receives hex files and flashes them to the AVR with avrdude. Optional flags can be found with `./main.py bridge --help`
2. On the host computer where the code is written, run `./main.py flash -p {PORT} -m {MCU} -f {TARGET_HEX_FILE}`. An example can be found in the example folder where a makefile is set up with the flash command.
