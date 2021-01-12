# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.13.1)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(isc_proto)
set(ZEPHYR_MODULES $ENV{ZEPHYR_BASE}/../modules/lib/tinycbor)
# Generate version file
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# zephyr_library_link_libraries(TINYCBOR)

list(APPEND HEADERS
  "${PROJECT_BINARY_DIR}/include/generated"
  "${PROJECT_BINARY_DIR}/zephyr/include/generated"
  "${PROJECT_SOURCE_DIR}/include"
  $ENV{ZEPHYR_BASE}/../modules/lib/tinycbor/include
  "${PROJECT_SOURCE_DIR}/src/lineparser"
  )
include_directories(${HEADERS})

target_sources(app PRIVATE src/main.c)
