cmake_minimum_required(VERSION 3.16)
project(agent_lab_embedded LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(agent_lab_log_parser
  src/log_parser.cpp
  src/diagnostic_code.cpp
)
target_include_directories(agent_lab_log_parser PUBLIC include)

add_executable(log_parser_cli src/main.cpp)
target_link_libraries(log_parser_cli PRIVATE agent_lab_log_parser)

add_executable(log_parser_test tests/log_parser_test.cpp)
target_link_libraries(log_parser_test PRIVATE agent_lab_log_parser)

enable_testing()
add_test(NAME log_parser_test COMMAND log_parser_test)
