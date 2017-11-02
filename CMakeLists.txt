cmake_minimum_required (VERSION 2.8.11)
project (bamm-suite)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

INSTALL(DIRECTORY scripts/
  DESTINATION bin
  PATTERN *
  PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE
)

add_subdirectory(PEnG-motif)
add_subdirectory(bamm-suite-cpp)
