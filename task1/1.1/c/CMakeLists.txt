cmake_minimum_required(VERSION 3.26)
project(psi C)

set(CMAKE_C_STANDARD 11)

add_executable(main main.c)
add_executable(client client.c)
add_executable(server server.c)

target_link_libraries(main PRIVATE m)