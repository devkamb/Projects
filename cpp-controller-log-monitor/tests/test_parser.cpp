#include "FailureAnalyzer.h"
#include "LogParser.h"

#include <cassert>
#include <iostream>

int main() {
    LogParser parser;

    auto entry = parser.parseLine("2026-06-12T10:00:00.100Z WARN NETWORK missed heartbeat controller=steering count=1");
    assert(entry.has_value());
    assert(entry->timestamp == "2026-06-12T10:00:00.100Z");
    assert(entry->level == LogLevel::Warn);
    assert(entry->subsystem == "NETWORK");
    assert(entry->message == "missed heartbeat controller=steering count=1");

    auto invalid = parser.parseLine("bad line");
    assert(!invalid.has_value());

    FailureAnalyzer analyzer;
    analyzer.add(*entry);
    analyzer.add(*parser.parseLine("2026-06-12T10:00:00.200Z ERROR HYDRAULIC pressure high psi=3400"));
    analyzer.add(*parser.parseLine("2026-06-12T10:00:00.300Z INFO CTRL auto mode stopped"));

    assert(analyzer.total() == 3);
    assert(analyzer.count(LogLevel::Warn) == 1);
    assert(analyzer.count(LogLevel::Error) == 1);
    assert(analyzer.containsAtLeast(LogLevel::Warn));
    assert(analyzer.containsAtLeast(LogLevel::Error));
    assert(analyzer.failureSignatures().size() == 2);

    std::cout << "All parser/analyzer tests passed\n";
    return 0;
}
