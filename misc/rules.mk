ifndef MCU_INFO_UTIL
PYTHON?=python
MCU_INFO_UTIL:=$(PYTHON) $(dir $(abspath $(lastword $(MAKEFILE_LIST))))../mcu-info-util.py $(MCU_INFO_UTIL_FLAGS)
endif

ifdef MCU
MCU_CFLAGS:=$(shell $(MCU_INFO_UTIL) --mcu $(MCU) --print-flags)
MCU_LFLAGS:=$(MCU_CFLAGS)
MCU_COMPILER:=$(shell $(MCU_INFO_UTIL) --mcu $(MCU) --find-compiler)
MCU_LINKER:=$(MCU_COMPILER)
MCU_TOOLCHAIN_DIR:=$(dir $(MCU_COMPILER))

MCU_LINKER_SCRIPT_COMMAND=$(MCU_INFO_UTIL) --mcu $(MCU) --linker-script "$(MCU_LINKER_SCRIPT)"
MCU_HEADER_FILE_COMMAND=$(MCU_INFO_UTIL) --mcu $(MCU) --header "$(MCU_HEADER_FILE)"
endif
