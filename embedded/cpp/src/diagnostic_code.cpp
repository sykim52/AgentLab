#include "diagnostic_code.hpp"

namespace agent_lab::embedded {

std::optional<DiagnosticCode> lookup_failure_code(const std::string& code) {
  if (code == "PERCEPTION_TIMEOUT") {
    return DiagnosticCode{code, "Perception pipeline exceeded latency budget"};
  }
  if (code == "SENSOR_SYNC_LOST") {
    return DiagnosticCode{code, "Camera/radar time sync drift beyond threshold"};
  }
  return std::nullopt;
}

}  // namespace agent_lab::embedded
