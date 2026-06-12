#include "FailureAnalyzer.h"

#include <algorithm>
#include <sstream>

void FailureAnalyzer::add(const LogEntry& entry) {
    entries_.push_back(entry);
}

int FailureAnalyzer::count(LogLevel level) const {
    return static_cast<int>(std::count_if(entries_.begin(), entries_.end(), [level](const LogEntry& entry) {
        return entry.level == level;
    }));
}

int FailureAnalyzer::total() const {
    return static_cast<int>(entries_.size());
}

bool FailureAnalyzer::containsAtLeast(LogLevel threshold) const {
    if (threshold == LogLevel::Error) {
        return count(LogLevel::Error) > 0;
    }
    if (threshold == LogLevel::Warn) {
        return count(LogLevel::Warn) > 0 || count(LogLevel::Error) > 0;
    }
    if (threshold == LogLevel::Info) {
        return total() > 0;
    }
    return false;
}

std::map<std::string, int> FailureAnalyzer::countsBySubsystem() const {
    std::map<std::string, int> counts;
    for (const auto& entry : entries_) {
        counts[entry.subsystem]++;
    }
    return counts;
}

std::vector<std::pair<std::string, int>> FailureAnalyzer::failureSignatures() const {
    std::map<std::string, int> signatures;
    for (const auto& entry : entries_) {
        if (entry.level == LogLevel::Info) {
            continue;
        }
        std::ostringstream key;
        key << toString(entry.level) << "|" << entry.subsystem << "|" << entry.message;
        signatures[key.str()]++;
    }

    std::vector<std::pair<std::string, int>> result(signatures.begin(), signatures.end());
    std::sort(result.begin(), result.end(), [](const auto& left, const auto& right) {
        return left.second > right.second;
    });
    return result;
}
