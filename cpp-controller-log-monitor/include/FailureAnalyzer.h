#ifndef FAILURE_ANALYZER_H
#define FAILURE_ANALYZER_H

#include "LogEntry.h"

#include <map>
#include <string>
#include <vector>

class FailureAnalyzer {
public:
    void add(const LogEntry& entry);
    int count(LogLevel level) const;
    int total() const;
    bool containsAtLeast(LogLevel threshold) const;
    std::map<std::string, int> countsBySubsystem() const;
    std::vector<std::pair<std::string, int>> failureSignatures() const;

private:
    std::vector<LogEntry> entries_;
};

#endif
