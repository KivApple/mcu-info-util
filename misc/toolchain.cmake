if(DEFINED MCU)
	set(ENV{MCU_MODEL} ${MCU})
else()
	if (DEFINED ENV{MCU_MODEL})
		set(MCU $ENV{MCU_MODEL})
	else()
		message(FATAL_ERROR "You should set MCU variable to use this toolchain file")
	endif()
endif()

if(NOT DEFINED MCU_INFO_UTIL)
	set(MCU_INFO_UTIL ${CMAKE_CURRENT_LIST_DIR}/../mcu-info-util.py) 
endif()

execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} --find-prefix
	OUTPUT_VARIABLE MCU_TOOLCHAIN_PREFIX
	OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} --find-compiler
	OUTPUT_VARIABLE MCU_COMPILER
	OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} ${MCU_INFO_UTIL_FLAGS} --print-flags
	OUTPUT_VARIABLE MCU_FLAGS
	OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} --header ?
	OUTPUT_VARIABLE HEADER_FILE_NEED
	OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} --linker-script ?
	OUTPUT_VARIABLE LINKER_SCRIPT_NEED
	OUTPUT_STRIP_TRAILING_WHITESPACE)

set(CMAKE_SYSTEM_NAME Generic)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_C_COMPILER ${MCU_COMPILER})
set(CMAKE_CXX_COMPILER ${MCU_COMPILER})
set(UTIL_OBJCOPY ${MCU_TOOLCHAIN_PREFIX}objcopy)
set(UTIL_SIZE ${MCU_TOOLCHAIN_PREFIX}size)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${MCU_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${MCU_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${MCU_FLAGS}")

include_directories("${CMAKE_CURRENT_BINARY_DIR}")

if((NOT TARGET mcu-header) AND ("${HEADER_FILE_NEED}" STREQUAL "yes"))
	add_custom_command(OUTPUT mcudefs.h
		COMMAND ${MCU_INFO_UTIL} ARGS --mcu ${MCU} ${MCU_INFO_UTIL_FLAGS} --header mcudefs.h
		COMMENT "Generating MCU header file")
	add_custom_target(mcu-header ALL
		DEPENDS mcudefs.h)
endif()

if((NOT TARGET linker-script) AND ("${LINKER_SCRIPT_NEED}" STREQUAL "yes"))
	add_custom_command(OUTPUT script.ld
		COMMAND ${MCU_INFO_UTIL} ARGS --mcu ${MCU} ${MCU_INFO_UTIL_FLAGS} --linker-script script.ld
		COMMENT "Generating linker script")
	add_custom_target(linker-script ALL
		DEPENDS script.ld)
	set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Tscript.ld")
endif()
