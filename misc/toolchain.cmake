if(DEFINED MCU)
	set(ENV{MCU_MODEL} ${MCU})
else()
	if (DEFINED ENV{MCU_MODEL})
		set(MCU $ENV{MCU_MODEL})
	else()
		message(FATAL_ERROR "You should set MCU variable to use this toolchain file")
	endif()
endif()

find_program(MCU_INFO_UTIL mcu-info-util ${CMAKE_CURRENT_LIST_DIR}/..) 
if (NOT MCU_INFO_UTIL)
	message(FATAL_ERROR "mcu-info-util not found")
endif()
message(STATUS "mcu-info-util found at path ${MCU_INFO_UTIL}")

if(DEFINED ENABLE_LIBOPENCM3)
	list(APPEND MCU_INFO_UTIL_FLAGS --enable-libopencm3)
endif()
if(DEFINED USE_DEFINES_IN_MCU_HEADER_FILE)
	list(APPEND MCU_INFO_UTIL_FLAGS --use-defines)
endif()

execute_process(COMMAND ${MCU_INFO_UTIL} --mcu ${MCU} --print-tags
	OUTPUT_VARIABLE MCU_TAGS
	OUTPUT_STRIP_TRAILING_WHITESPACE)
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

file(TO_CMAKE_PATH ${MCU_TOOLCHAIN_PREFIX} MCU_TOOLCHAIN_PREFIX)
file(TO_CMAKE_PATH ${MCU_COMPILER} MCU_COMPILER)

set(CMAKE_SYSTEM_NAME Generic)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_C_COMPILER ${MCU_COMPILER})
set(CMAKE_CXX_COMPILER ${MCU_COMPILER})
set(UTIL_OBJCOPY ${MCU_TOOLCHAIN_PREFIX}objcopy)
set(UTIL_SIZE ${MCU_TOOLCHAIN_PREFIX}size)

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
	set(MCU_FLAGS "${MCU_FLAGS} -Tscript.ld")
endif()

set(CMAKE_C_FLAGS "${MCU_FLAGS}" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS "${MCU_FLAGS}" CACHE INTERNAL "")
set(CMAKE_EXE_LINKER_FLAGS "${MCU_FLAGS}" CACHE INTERNAL "")
include_directories("${CMAKE_CURRENT_BINARY_DIR}")
