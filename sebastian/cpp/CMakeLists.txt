project(SOCS)

include_directories(/usr/include/eigen3)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

add_executable(model model.cpp)
