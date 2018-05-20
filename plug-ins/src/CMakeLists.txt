set(SOURCE_FILES
    "spore.h"
    "sporeLocator.cpp"
)

find_package(Maya REQUIRED)
find_package(OpenGL REQUIRED)

message("#####################################################")

message("DEVKIT_LOCATION: ${DEVKIT_LOCATION}")
message("MAYA_LOCATION: ${MAYA_LOCATION}")

if (OPENGL_FOUND)
    message("opengl found")
    message("include dir: ${OPENGL_INCLUDE_DIR}")
    message("link libraries: ${OPENGL_gl_LIBRARY}")
else (OPENGL_FOUND)
    message("opengl not found")
endif()

message("#####################################################")

include_directories(${MAYA_INCLUDE_DIR})
link_directories(${MAYA_LIBRARY_DIR})
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${MAYA_LIBRARIES})

MAYA_PLUGIN(${PROJECT_NAME})
install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION plug-ins)
