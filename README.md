# mcu-info-util

[![Build Status](https://travis-ci.org/KivApple/mcu-info-util.svg?branch=master)](https://travis-ci.org/KivApple/mcu-info-util)

This is small utility written in Python what allows you to generate
linker script and header files (with MMIO registers and IRQ definions)
for specified MCU. Also this utility can find toolchain if it was
installed on your system.

Currently supported AVR, MSP430 and some ARM MCUs.

Run python setup.py install to install application to your system.

Run mcu-info-util -h after installation for information about usage.

## License

Main project code released under MIT license, but some parts of data files
have different licenses. Please see copyright notices in the relevant files.
