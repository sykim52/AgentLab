#include "log_parser.hpp"

#include <iostream>

int main() {
  const std::string sample =
      "2026-10-01T12:00:00Z|PERCEPTION|ERROR|PERCEPTION_TIMEOUT|frame deadline missed\n"
      "bad-line-without-pipes\n"
      "2026-10-01T12:00:01Z|SENSOR|WARN|SENSOR_SYNC_LOST|lidar-camera skew\n";
  agent_lab::embedded::LogParser parser;
  std::size_t malformed = 0;
  auto events = parser.parse(sample, &malformed);
  std::cout << "events=" << events.size() << " malformed=" << malformed << "\n";
  return events.empty() ? 1 : 0;
}
