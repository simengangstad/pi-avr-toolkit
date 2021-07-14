#!/usr/bin/python3

import os
import subprocess
import shutil

import serial

import argparse

AVRDUDE_CONF_LINUX_GPIO = """
programmer
  id    = "pi";
  desc  = "Use the Linux sysfs interface to bitbang GPIO lines";
  type  = "linuxgpio";
  reset = {reset};
  sck   = {sck};
  miso  = {miso};
  mosi  = {mosi};
;
"""

TRANSMIT_START_MARKER = "tx-begin"
TRANSMIT_END_MARKER = "tx-end"


def flash():
    """
    Sends the hex file to the Raspberry PI for flashing.
    """
    with open(args.file, "r") as hexfile:

        payload = hexfile.read()
        payload_size = len(payload)

        with serial.Serial(args.port, args.baud_rate, timeout=args.timeout) as interface:

            start_sequence = "{marker},{mcu},{size}\n".format(
                marker=TRANSMIT_START_MARKER,
                mcu=args.mcu,
                size=payload_size
            )

            interface.write(start_sequence.encode())
            interface.write(payload.encode())

            # Grab feedback
            line = interface.readline().decode()

            while not line.startswith(TRANSMIT_END_MARKER):
                print(line, end="")
                line = interface.readline().decode()


def bridge():
    """
    Receives the hex file from the host and uses avrdude to flash the AVR.
    """

    # Firstly prepare the avrdude configuration file if it doesn't exists
    custom_avrdude_configuration_file = os.path.join(
        os.getcwd(), "avrdude.conf")

    if not os.path.exists(custom_avrdude_configuration_file):
        shutil.copyfile(args.configuration_file,
                        custom_avrdude_configuration_file)

        # Add our related functionality with using the GPIO pins for
        # programming pins
        extra_configuration = AVRDUDE_CONF_LINUX_GPIO.format(
            mosi=args.mosi_pin,
            miso=args.mosi_pin,
            sck=args.sck_pin,
            reset=args.reset_pin
        )

        with open(custom_avrdude_configuration_file, "a") as file_handle:
            file_handle.write(extra_configuration)

    # Open the 'bridge' and wait for a hex file to flash to the AVR
    with serial.Serial(args.bridge_port, args.baud_rate, timeout=args.timeout) as interface:

        while True:
            start_sequence = interface.readline().decode()

            if not start_sequence.startswith(TRANSMIT_START_MARKER):
                continue

            _, mcu, payload_size = start_sequence.strip().split(",")

            # Grab the hex data, write it in tmp for use within avrdude
            payload = interface.read(size=int(payload_size))
            with open("/tmp/main.hex", "wb") as hexfile:
                hexfile.write(payload)

            avrdude_command = [
                "sudo", "avrdude",
                "-p", mcu,
                "-C", custom_avrdude_configuration_file,
                "-c", "pi",
                "-v",
                "-U", "flash:w:/tmp/main.hex:i"]

            output = subprocess.Popen(
                avrdude_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Read stdout and stderr continously
            for stdout_line in iter(output.stdout.readline, ""):
                interface.write(stdout_line.encode())
            output.stdout.close()

            for stderr_line in iter(output.stderr.readline, ""):
                interface.write(stderr_line.encode())
            output.stderr.close()

            # Mark the GPIO pins as unexported
            gpio_pins = [args.mosi_pin, args.miso_pin,
                         args.sck_pin, args.reset_pin]

            for pin in gpio_pins:
                subprocess.run(
                    ["echo", str(pin),
                     ">", "/sys/class/gpio/unexport"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            interface.write((TRANSMIT_END_MARKER + "\n").encode())


parser = argparse.ArgumentParser(
    description="AVR flash script for using a Raspberry PI as a programmer",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    "-b", "--baud-rate", type=int,
    help="Baud rate for host/Raspberry PI interface", default=115200)
parser.add_argument(
    "-t", "--timeout", type=int,
    help="Timeout for host/Raspberry PI interface in seconds", default=10)

subparsers = parser.add_subparsers(help="Commands", dest="command")


bridge_parser = subparsers.add_parser(
    "bridge",
    help="Start process receiving hex files and feeding them to avrdude (running on Raspberry PI)",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

bridge_parser.add_argument(
    "-p",
    "--bridge-port",
    help="Port for the interface with the host sending the hex file",
    default="/dev/ttyGS0")
bridge_parser.add_argument(
    "-c",
    "--configuration-file",
    help="Path to avrdude configuration file",
    default="/etc/avrdude.conf")
bridge_parser.add_argument(
    "--mosi-pin",
    help="GPIO pin on Raspberry PI connected to the AVR's MOSI pin", type=int,
    default=26)
bridge_parser.add_argument(
    "--miso-pin",
    help="GPIO pin on Raspberry PI connected to the AVR's MSIO pin", type=int,
    default=19)
bridge_parser.add_argument(
    "--sck-pin",
    help="GPIO pin on Raspberry PI connected to the AVR's SCK pin", type=int,
    default=13)
bridge_parser.add_argument(
    "--reset-pin",
    help="GPIO pin on Raspberry PI connected to the AVR's RESET pin", type=int,
    default=6)


flash_parser = subparsers.add_parser(
    "flash",
    help="Send a hex file to the Raspberry PI which is further flashed to the AVR",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

flash_parser.add_argument("-p", "--port", help="Target port for PI")
flash_parser.add_argument("-m", "--mcu", help="Target microcontroller")
flash_parser.add_argument("-f", "--file", help="Path to hex file")


args = parser.parse_args()

if args.command == "bridge":
    bridge()
elif args.command == "flash":
    if args.port and args.mcu and args.file:
        flash()
    else:
        flash_parser.print_help()
else:
    parser.print_help()
