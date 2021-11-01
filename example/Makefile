MCU=atmega168p
F_CPU=8000000
CC=avr-gcc
OBJCOPY=avr-objcopy
CFLAGS=-std=c11 -Wall -g -Os -mmcu=${MCU} -DF_CPU=${F_CPU} -I.
TARGET=main
SRCS=main.c
PORT=/dev/ttyACM0

all:
	${CC} ${CFLAGS} -o ${TARGET}.bin ${SRCS}
	${OBJCOPY} -j .text -j .data -O ihex ${TARGET}.bin ${TARGET}.hex

flash:
	../main.py flash -p ${PORT} -m ${MCU} -f ${TARGET}.hex

clean:
	rm -f *.bin *.hex

