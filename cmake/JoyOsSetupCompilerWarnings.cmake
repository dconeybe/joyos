block()

include(CheckCXXCompilerFlag)

list(APPEND CMAKE_MESSAGE_CONTEXT "JoyOsSetupCompilerWarnings")

set(all_warning_flags
  -Wall
  -Wextra
  -pedantic
  -Wcast-align
  -Wconversion
  -Wdouble-promotion
  -Wduplicated-branches
  -Wduplicated-cond
  -Weffc++
  -Wformat=2
  -Wimplicit-fallthrough
  -Wlifetime
  -Wlogical-op
  -Wmisleading-indentation
  -Wnon-virtual-dtor
  -Wnull-dereference
  -Wold-style-cast
  -Woverloaded-virtual
  -Wpedantic
  -Wshadow
  -Wsign-conversion
  -Wunused
  -Wuseless-cast
)

# Test each flag for compiler support and create a list of *supported* warning flags.
set(supported_warning_flags "")
set(all_warning_flags_cache_vars "")
foreach(warning_flag IN LISTS all_warning_flags)
  # Maps each warning flag to a unique cache variable.
  set(warning_flag_id "${warning_flag}")
  string(REPLACE "/" "" warning_flag_id "${warning_flag_id}")
  string(REPLACE "-" "" warning_flag_id "${warning_flag_id}")
  string(REPLACE "=" "" warning_flag_id "${warning_flag_id}")
  string(REPLACE "++" "pp" warning_flag_id "${warning_flag_id}")
  set(warning_flag_cache_var "JOYOS_COMPILER_WARNING_${warning_flag_id}")

  # Verify that the mapping is unique.
  list(FIND all_warning_flags_cache_vars "${warning_flag_cache_var}" "warning_flag_cache_var_index")
  if(warning_flag_cache_var_index GREATER_EQUAL 0)
    list(GET all_warning_flags "${warning_flag_cache_var_index}" existing_warning_flag)
    message(
      FATAL_ERROR
      "INTERNAL ERROR: Both warning flags ${existing_warning_flag} and ${warning_flag} "
      "map to the same cache variable: ${warning_flag_cache_var}"
    )
  endif()
  list(APPEND all_warning_flags_cache_vars "${warning_flag_cache_var}")

  # Test the compiler for support of the current warning flag.
  message(VERBOSE "Testing for compiler support of flag: ${warning_flag}")
  check_cxx_compiler_flag("${warning_flag}" "${warning_flag_cache_var}")
  if(${warning_flag_cache_var})
    list(APPEND supported_warning_flags "${warning_flag}")
  endif()
endforeach()

# Set the supported warnings.
string(JOIN ", " supported_warning_flags_str ${supported_warning_flags})
message(VERBOSE "Setting compiler warning flags: ${supported_warning_flags_str}")
add_compile_options(${supported_warning_flags})

endblock()
