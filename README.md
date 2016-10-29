# mcu-info-util

[![Build Status](https://travis-ci.org/KivApple/mcu-info-util.svg?branch=master)](https://travis-ci.org/KivApple/mcu-info-util)

This is small utility written in Python what allows you to generate
linker script and header files (with MMIO registers and IRQ definions)
for specified MCU. Also this utility can find toolchain if it was
installed on your system.

Currently supported AVR, MSP430 and some ARM MCUs.

Run python setup.py install to install application to your system.

Run mcu-info-util -h after installation for information about usage.

## Requirements

mcu-info-util requires Python 2.7 or higher.

Also, this package relies on [cmsis-svd](https://github.com/posborne/cmsis-svd) package.

## Stand-alone usage

You should specify MCU model via --mcu command line argument.
All others arguments are optional.

Examples:

    mcu-info-util --mcu atmega328p --find-prefix
    mcu-info-util --mcu atmega328p --find-compiler
    mcu-info-util --mcu atmega328p --print-flags
    mcu-info-util --mcu stm32f103c8t6 --linker-script script.ld
    mcu-info-util --mcu stm32f103c8t6 --header mcudefs.h

If mcu-info-util failed to find needed toolchain (e. g. toolchain is not installed) it prints empty line.

If mcu-info-util failed to find specified MCU in database it prints error message.

Also you can check is linker script and header file needed for specified MCU by pass "?" instead of file name as argument of --linker-script and --header parameters. Program will print "yes" or "no". 

Examples:

    mcu-info-util --mcu atmega328p --linker-script ?
    mcu-info-util --mcu stm32f103c8t6 --header ?

Also you can find some examples of mcu-info-util usage in misc directory in this repository.

## Library usage

You can also use mcu-info-util as library in your own Python code. To do this you need to import
mcu_info_util package into your program.

Example:

```python
from mcu_info_util import Toolchain
mcu = "stm32f103c8t6"
toolchain = Toolchain.find_toolchain(mcu)
print(toolchain.find_prefix())
print(toolchain.find_compiler())
print(" ".join(toolchain.get_flags(mcu)))
if toolchain.generate_linker_script(mcu, "script.ld"):
    print("Linker script generated")
if toolchain.generate_header(mcu, "mcudefs.h"):
    print("Header file generated")
# You can run generate_header and generate_linker_script
# without second argument just to know is those files needed
```

## License

Main project code released under MIT license, but some parts of data files
have different licenses. Please see copyright notices in the relevant files.
