#pragma once

#include <chrono>
#include <string>

namespace agent_lab::embedded {

enum class Severity { Debug, Info, Warn, Error, Fatal };

struct LogEvent {
  std::chrono::system_clock::time_point timestamp{};
  std::string component;
  Severity severity{Severity::Info};
  std::string code;
  std::string message;
};

}  // namespace agent_lab::embedded
