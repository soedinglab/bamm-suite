cmake_minimum_required (VERSION 2.8.11)
project (bamm-suite)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

INSTALL(DIRECTORY scripts/ DESTINATION bin)
add_subdirectory(PEnG-motif)
