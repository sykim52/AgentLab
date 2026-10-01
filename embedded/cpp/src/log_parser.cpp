#include "log_parser.hpp"

#include <cctype>
#include <sstream>

namespace agent_lab::embedded {
namespace {

Severity parse_severity(const std::string& token) {
  std::string u;
  u.reserve(token.size());
  for (char c : token) u.push_back(static_cast<char>(std::toupper(static_cast<unsigned char>(c))));
  if (u == "DEBUG") return Severity::Debug;
  if (u == "INFO") return Severity::Info;
  if (u == "WARN" || u == "WARNING") return Severity::Warn;
  if (u == "ERROR") return Severity::Error;
  if (u == "FATAL") return Severity::Fatal;
  return Severity::Info;
}

}  // namespace

std::vector<LogEvent> LogParser::parse(const std::string& text, std::size_t* malformed_out) const {
  std::vector<LogEvent> events;
  std::size_t malformed = 0;
  std::istringstream in(text);
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty()) continue;
    // Expected: ISO8601|COMPONENT|SEVERITY|CODE|message
    std::size_t p1 = line.find('|');
    std::size_t p2 = p1 == std::string::npos ? std::string::npos : line.find('|', p1 + 1);
    std::size_t p3 = p2 == std::string::npos ? std::string::npos : line.find('|', p2 + 1);
    std::size_t p4 = p3 == std::string::npos ? std::string::npos : line.find('|', p3 + 1);
    if (p1 == std::string::npos || p2 == std::string::npos || p3 == std::string::npos ||
        p4 == std::string::npos) {
      ++malformed;
      continue;
    }
    LogEvent ev;
    ev.timestamp = std::chrono::system_clock::now();  // timestamp string parse: P1 follow-up
    ev.component = line.substr(p1 + 1, p2 - p1 - 1);
    ev.severity = parse_severity(line.substr(p2 + 1, p3 - p2 - 1));
    ev.code = line.substr(p3 + 1, p4 - p3 - 1);
    ev.message = line.substr(p4 + 1);
    events.push_back(std::move(ev));
  }
  if (malformed_out) *malformed_out = malformed;
  return events;
}

}  // namespace agent_lab::embedded
