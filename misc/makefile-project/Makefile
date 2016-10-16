PROJECT_NAME=led-blink
SOURCES=main.c
CFLAGS+=-DF_CPU=8000000 -Os

MCU=atmega328p
include ../rules.mk

all:: $(BUILD_DIR)/$(PROJECT_NAME).hex

$(BUILD_DIR)/$(PROJECT_NAME).hex: $(EXECUTABLE_NAME)
	$(MCU_TOOLCHAIN_DIR)avr-objcopy -Oihex $< $@
