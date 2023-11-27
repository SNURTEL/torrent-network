cmake_minimum_required(VERSION 3.22.1)
project(psi C)

set(CMAKE_C_STANDARD 11)

add_executable(main main.c)
add_executable(client client.c)
add_executable(server server.c)

target_link_libraries(main PRIVATE m)
target_link_libraries(client PRIVATE m)
target_link_libraries(server PRIVATE m)