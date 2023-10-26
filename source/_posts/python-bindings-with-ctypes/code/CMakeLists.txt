cmake_minimum_required(VERSION 3.24)

project(fnv VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_BUILD_TYPE "Release")

if (MSVC)
    add_compile_options(/Wall /W4 /Ox)
else()
    add_compile_options(-Wall -Werror -O3)
endif()

add_library(fnv SHARED fnv.cpp)