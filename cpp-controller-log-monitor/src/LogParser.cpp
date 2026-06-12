#include "LogParser.h"

#include <sstream>

std::string toString(LogLevel level) {
    switch (level) {
        case LogLevel::Info:
            return "INFO";
        case LogLevel::Warn:
            return "WARN";
        case LogLevel::Error:
            return "ERROR";
        default:
            return "UNKNOWN";
    }
}

LogLevel logLevelFromString(const std::string& value) {
    if (value == "INFO") {
        return LogLevel::Info;
    }
    if (value == "WARN") {
        return LogLevel::Warn;
    }
    if (value == "ERROR") {
        return LogLevel::Error;
    }
    return LogLevel::Unknown;
}

std::optional<LogEntry> LogParser::parseLine(const std::string& line) const {
    std::istringstream stream(line);
    std::string timestamp;
    std::string levelText;
    std::string subsystem;

    if (!(stream >> timestamp >> levelText >> subsystem)) {
        return std::nullopt;
    }

    std::string message;
    std::getline(stream, message);
    if (!message.empty() && message.front() == ' ') {
        message.erase(0, 1);
    }

    LogLevel level = logLevelFromString(levelText);
    if (level == LogLevel::Unknown || message.empty()) {
        return std::nullopt;
    }

    return LogEntry{timestamp, level, subsystem, message};
}
