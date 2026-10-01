#pragma once

#include <optional>
#include <string>

namespace agent_lab::embedded {

struct DiagnosticCode {
  std::string code;
  std::string description;
};

std::optional<DiagnosticCode> lookup_failure_code(const std::string& code);

}  // namespace agent_lab::embedded
