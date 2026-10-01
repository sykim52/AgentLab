#include "log_parser.hpp"

#include <cassert>
#include <iostream>

int main() {
  agent_lab::embedded::LogParser parser;
  std::size_t malformed = 0;
  const std::string sample =
      "2026-10-01T12:00:00Z|PERCEPTION|ERROR|PERCEPTION_TIMEOUT|deadline\n"
      "not-a-log\n";
  auto events = parser.parse(sample, &malformed);
  assert(events.size() == 1);
  assert(malformed == 1);
  assert(events[0].component == "PERCEPTION");
  assert(events[0].code == "PERCEPTION_TIMEOUT");
  std::cout << "log_parser_test ok\n";
  return 0;
}
