#ifndef LOG_ENTRY_H
#define LOG_ENTRY_H

#include <string>

enum class LogLevel {
    Info,
    Warn,
    Error,
    Unknown
};

struct LogEntry {
    std::string timestamp;
    LogLevel level;
    std::string subsystem;
    std::string message;
};

std::string toString(LogLevel level);
LogLevel logLevelFromString(const std::string& value);

#endif
