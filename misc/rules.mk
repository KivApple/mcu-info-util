ifndef PROJECT_NAME
$(error You should set PROJECT_NAME variable to use this makefile)
endif
ifndef MCU
$(error You should set MCU variable to use this makefile)
endif
ifndef SOURCES
$(error You should set SOURCES variable to use this makefile)
endif

ifndef MCU_INFO_UTIL
MCU_INFO_UTIL:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))../mcu-info-util.py
endif
ifeq ("$(wildcard $(MCU_INFO_UTIL))","")
$(error mcu-info-util not found)
endif
MCU_INFO_UTIL:=$(MCU_INFO_UTIL) $(MCU_INFO_UTIL_FLAGS)

BUILD_DIR?=build
BUILD_OBJECTS_DIR:=$(BUILD_DIR)/obj
BUILD_DEPS_DIR:=$(BUILD_DIR)/deps
BUILD_INCLUDE_DIR:=$(BUILD_DIR)/include

MKDIR_P?=mkdir -p
RM_RFV?=rm -rfv
Q?=@

MCU_FLAGS:=$(shell $(MCU_INFO_UTIL) --mcu $(MCU) --print-flags)
COMPILER:=$(shell $(MCU_INFO_UTIL) --mcu $(MCU) --find-compiler)
LINKER:=$(COMPILER)
TOOLCHAIN_DIR:=$(dir $(MCU_COMPILER))

LINKER_SCRIPT_COMMAND=$(MCU_INFO_UTIL) --mcu $(MCU) --linker-script "$(LINKER_SCRIPT)"
MCU_HEADER_FILE_COMMAND=$(MCU_INFO_UTIL) --mcu $(MCU) --header "$(MCU_HEADER_FILE)"

C_SOURCES:=$(filter %.c,$(SOURCES))
CXX_SOURCES:=$(filter %.cpp,$(SOURCES))
ASM_SOURCES:=$(filter %.s,$(SOURCES))

C_OBJECTS:=$(addprefix $(BUILD_OBJECTS_DIR)/,$(notdir $(C_SOURCES:.c=.c.o)))
CXX_OBJECTS:=$(addprefix $(BUILD_OBJECTS_DIR)/,$(notdir $(CXX_SOURCES:.cpp=.cpp.o)))
ASM_OBJECTS:=$(addprefix $(BUILD_OBJECTS_DIR)/,$(notdir $(ASM_SOURCES:.s=.s.o)))

OBJECTS:=$(C_OBJECTS) $(CXX_OBJECTS) $(ASM_OBJECTS)

EXECUTABLE_SUFFIX?=.elf
EXECUTABLE_NAME:=$(BUILD_DIR)/$(PROJECT_NAME)$(EXECUTABLE_SUFFIX)
 
LINKER_SCRIPT?=$(BUILD_DIR)/script.ld
MCU_HEADER_FILE?=$(BUILD_INCLUDE_DIR)/mcudefs.h

VPATH=$(sort $(SOURCES))

all:: $(BUILD_DIR) $(MCU_HEADER_FILE) $(EXECUTABLE_NAME)

$(BUILD_DIR)::
	$(Q)$(MKDIR_P) $(BUILD_DIR)
	$(Q)$(MKDIR_P) $(BUILD_OBJECTS_DIR)
	$(Q)$(MKDIR_P) $(BUILD_DEPS_DIR)
	$(Q)$(MKDIR_P) $(BUILD_INCLUDE_DIR)

$(MCU_HEADER_FILE): Makefile
	@echo "GENERATE $(notdir $@)"
	$(Q)$(MCU_HEADER_FILE_COMMAND)

$(LINKER_SCRIPT): Makefile
	@echo "GENERATE $(notdir $@)"
	$(Q)$(LINKER_SCRIPT_COMMAND)

$(EXECUTABLE_NAME): $(OBJECTS) $(LINKER_SCRIPT) Makefile
	@echo "LINK     $(notdir $@)"
	$(Q)$(LINKER) -o $@ $(OBJECTS) $(MCU_FLAGS) $(LFLAGS)

$(C_OBJECTS): $(BUILD_OBJECTS_DIR)/%.c.o: %.c Makefile
	@echo "COMPILE  $(notdir $<)"
	$(Q)$(COMPILER) -c -o $@ $(MCU_FLAGS) $(CFLAGS) -MMD -MP -MF $(BUILD_DEPS_DIR)/$(notdir $<).deps $<

$(CXX_OBJECTS): $(BUILD_OBJECTS_DIR)/%.cpp.o: %.cpp Makefile
	@echo "COMPILE  $(notdir $<)"
	$(Q)$(COMPILER) -c -o $@ $(MCU_FLAGS) $(CFLAGS) -MMD -MP -MF $(BUILD_DEPS_DIR)/$(notdir $<).deps $<

$(ASM_OBJECTS): $(BUILD_OBJECTS_DIR)/%.s.o: %.s Makefile
	@echo "COMPILE  $(notdir $<)"
	$(Q)$(COMPILER) -c -o $@ $(MCU_FLAGS) $(CFLAGS) -MMD -MP -MF $(BUILD_DEPS_DIR)/$(notdir $<).deps $<

clean::
	$(Q)$(RM_RFV) $(BUILD_DIR)

-include $(BUILD_DEPS_DIR)/*.deps
