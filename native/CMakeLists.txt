cmake_minimum_required(VERSION 3.21)
project(mechadk_native LANGUAGES C)

# BUILD_SHARED_LIBS selects shared (desktop, Android) or static (iOS, WebAssembly).
add_library(mechadk_native mechadk_native.c)
set_target_properties(mechadk_native PROPERTIES C_VISIBILITY_PRESET hidden)

# One flat output directory whatever the generator, so Native.targets knows where to look.
if(MECHADK_OUTPUT_DIR)
  foreach(cfg "" _DEBUG _RELEASE _RELWITHDEBINFO _MINSIZEREL)
    set_target_properties(mechadk_native PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY${cfg} "${MECHADK_OUTPUT_DIR}"
      LIBRARY_OUTPUT_DIRECTORY${cfg} "${MECHADK_OUTPUT_DIR}"
      ARCHIVE_OUTPUT_DIRECTORY${cfg} "${MECHADK_OUTPUT_DIR}")
  endforeach()
endif()
