cmake_minimum_required(VERSION 3.6)

set(MCU atmega328p)
set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

#execute_process(COMMAND mcu-info-util --build-scripts-dir
#	OUTPUT_VARIABLE BUILD_SCRIPTS_DIR
#	OUTPUT_STRIP_TRAILING_WHITESPACE)
#set(CMAKE_TOOLCHAIN_FILE "${BUILD_SCRIPTS_DIR}/toolchain.cmake")

project(led-blink)

set(CMAKE_BUILD_TYPE Release)
add_definitions(-DF_CPU=8000000)

set(SOURCES main.c)

add_executable(${PROJECT_NAME} ${SOURCES})
