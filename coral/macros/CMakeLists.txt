PROJECT(merge_split CXX)

SET(ROOT_DIR ${PROJECT_SOURCE_DIR}/../../.cmake )
FIND_PACKAGE(ROOT REQUIRED)

INCLUDE_DIRECTORIES( ${ROOT_INCLUDE_DIR} )

ADD_EXECUTABLE(merge_split merge_split.cc mysignal.cc)
TARGET_LINK_LIBRARIES(merge_split ${ROOT_LIBRARIES} popt)
