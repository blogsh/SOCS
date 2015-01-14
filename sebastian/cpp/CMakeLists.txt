project(SOCS)

find_package( Boost REQUIRED COMPONENTS thread )
include_directories( ${Boost_INCLUDE_DIRS} )

include_directories(/usr/include/eigen3)
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

find_package(PkgConfig REQUIRED)
pkg_search_module(GLFW REQUIRED glfw3)
include_directories(${GLFW_INCLUDE_DIRS})

find_package(OpenGL REQUIRED)
include_directories(${OpenGL_INCLUDE_DIRS})
link_directories(${OpenGL_LIBRARY_DIRS})
add_definitions(${OpenGL_DEFINITIONS})

add_executable(model model.cpp)
target_link_libraries(model ${OPENGL_LIBRARIES} ${GLFW_LIBRARIES} ${Boost_LIBRARIES})
