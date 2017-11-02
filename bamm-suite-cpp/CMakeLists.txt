cmake_minimum_required(VERSION 2.8.12)
project(bamm_suite CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

include_directories(validators)
add_subdirectory(validators)