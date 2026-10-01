#pragma once

#include <string>
#include <vector>

#include "log_event.hpp"

namespace agent_lab::embedded {

class LogParser {
 public:
  // Line-oriented embedded log parse. Malformed lines are skipped and counted.
  std::vector<LogEvent> parse(const std::string& text, std::size_t* malformed_out = nullptr) const;
};

}  // namespace agent_lab::embedded
