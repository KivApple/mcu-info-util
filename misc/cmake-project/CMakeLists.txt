cmake_minimum_required(VERSION 3.6)

set(MCU atmega328p)
set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(led-blink)

set(CMAKE_BUILD_TYPE Release)
add_definitions(-DF_CPU=8000000)

set(SOURCES main.c)

add_executable(${PROJECT_NAME} ${SOURCES})
