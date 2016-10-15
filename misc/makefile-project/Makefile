APP_NAME=led-blink
BUILD_DIR?=./build
SOURCES=main.c
CFLAGS+=-DF_CPU=8000000 -Os

MCU=atmega328p
MCU_HEADER_FILE=$(BUILD_DIR)/mcudefs.h
MCU_LINKER_SCRIPT=$(BUILD_DIR)/script.ld
include ../rules.mk

all: $(BUILD_DIR) $(BUILD_DIR)/$(APP_NAME).elf $(BUILD_DIR)/$(APP_NAME).hex
	$(MCU_TOOLCHAIN_DIR)avr-size $(BUILD_DIR)/$(APP_NAME).elf

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

$(BUILD_DIR)/mcudefs.h: Makefile
	$(MCU_HEADER_FILE_COMMAND)

$(BUILD_DIR)/script.ld: Makefile
	$(MCU_LINKER_SCRIPT_COMMAND)

$(BUILD_DIR)/$(APP_NAME).elf: $(SOURCES) $(BUILD_DIR)/mcudefs.h $(BUILD_DIR)/script.ld Makefile
	$(MCU_COMPILER) $(MCU_CFLAGS) $(CFLAGS) -o $@ $(SOURCES)

$(BUILD_DIR)/$(APP_NAME).hex: $(BUILD_DIR)/$(APP_NAME).elf
	$(MCU_TOOLCHAIN_DIR)avr-objcopy -Oihex $< $@

clean:
	rm -rfv $(BUILD_DIR)
