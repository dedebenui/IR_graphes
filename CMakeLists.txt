cmake_minimum_required(VERSION 3.14)
project(emsapp)

set(CMAKE_CXX_STANDARD 20)


add_definitions(-DPy_ENABLE_SHARED)

# --------------------
# Variables à modifier
# --------------------

set(Python_ROOT_DIR "C:\\Users\\sierrob\\Miniconda3\\envs\\dev")
set(Python_RUNTIME_LIBRARY_DIRS "C:\\Users\\sierrob\\Miniconda3\\envs\\dev")

# Merci de décommenter si Debug ou Release pour installer python une fois
set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/build/Debug)
# set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/build/Release)

# ---------------------------
# Fin de variables à modifier
# ---------------------------

find_package(Python COMPONENTS Interpreter Development)

include_directories(${Python_INCLUDE_DIRS})

set(_PYTHON_VERSION_NO_DOTS "${Python_VERSION_MAJOR}${Python_VERSION_MINOR}")

# Install the python scripts
install(
    DIRECTORY ${CMAKE_SOURCE_DIR}/src/emsapp
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python
    PATTERN ".git" EXCLUDE
    PATTERN ".gitignore" EXCLUDE
    PATTERN ".arcconfig" EXCLUDE
    PATTERN "CMakeLists.txt" EXCLUDE
    PATTERN "__pycache__" EXCLUDE
)

install(
    PROGRAMS ${Python_EXECUTABLE}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python/bin
)

install(
   DIRECTORY ${Python_STDLIB}
   DESTINATION ${CMAKE_INSTALL_PREFIX}/python/
   PATTERN "__pycache__" EXCLUDE               # * any cache *
   PATTERN "config-${Python_VERSION}m/*.a" EXCLUDE  # static lib
   PATTERN "lib2to3" EXCLUDE                   # ./lib2to3
   PATTERN "tkinter" EXCLUDE                   # ./tkinter
   PATTERN "lib-dynload/_tkinter.*" EXCLUDE    # ./lib-dynload/_tkinter.co
   PATTERN "idlelib" EXCLUDE                   # ./idlelib
   PATTERN "test" EXCLUDE                      # ./test
   PATTERN "turtledemo" EXCLUDE                # ./turtledemo
   PATTERN "turtle.py" EXCLUDE                 # ./turtle.py
   PATTERN "wininst*.exe" EXCLUDE              # from distutils, avoid malware false positive
)

# Needed for distutils/pip
# get the last part of the include dir, will be 'python{version}{abiflag}',
install(
        FILES ${Python_INCLUDE_DIRS}/pyconfig.h
        DESTINATION ${CMAKE_INSTALL_PREFIX}/python
)

install(
    DIRECTORY ${Python_RUNTIME_LIBRARY_DIRS}/DLLs
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python
    CONFIGURATIONS Release;RelWithDebInfo;MinSizeRel
    PATTERN "*.pdb" EXCLUDE
    PATTERN "*_d.*" EXCLUDE
)
#
install(
    DIRECTORY ${Python_RUNTIME_LIBRARY_DIRS}/DLLs
    DESTINATION ${CMAKE_INSTALL_PREFIX}/python
    CONFIGURATIONS Debug
)

install(
    FILES ${Python_RUNTIME_LIBRARY_DIRS}/python${_PYTHON_VERSION_NO_DOTS}.dll
        ${Python_RUNTIME_LIBRARY_DIRS}/python${Python_VERSION_MAJOR}.dll
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)

add_subdirectory(external/pybind11)
include_directories(external/pybind11/include)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${Python_LIBRARIES})