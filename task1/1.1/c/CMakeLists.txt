cmake_minimum_required(VERSION 3.26)
project(psi C)

set(CMAKE_C_STANDARD 11)

add_executable(psi
        main.c)

target_link_libraries(psi PRIVATE m)