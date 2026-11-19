cmake_minimum_required(VERSION 3.20)

project(WebGLSimulator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(simulator
    engine/src/main.cpp
    engine/src/Physics.cpp
    engine/src/Simulation.cpp
)

target_include_directories(simulator PRIVATE engine/include)

set_target_properties(simulator PROPERTIES
    SUFFIX ".js"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/web"
)

if(EMSCRIPTEN)
    target_compile_options(simulator PRIVATE
        -O3
        -Wall
        -Wextra
    )

    target_link_options(simulator PRIVATE
        -O3
        -sWASM=1
        -sALLOW_MEMORY_GROWTH=1
        -sNO_EXIT_RUNTIME=1
        -sASSERTIONS=0
        -sEXPORTED_FUNCTIONS=['_main']
    )
endif()
