#include "FailureAnalyzer.h"
#include "LogParser.h"

#include <fstream>
#include <iostream>
#include <optional>
#include <string>

struct Options {
    std::string inputPath;
    bool summary = false;
    std::optional<LogLevel> failOn;
    std::optional<std::string> filterSubsystem;
};

void printUsage() {
    std::cout << "Usage: controller_log_monitor --input <path> [--summary] [--fail-on WARN|ERROR] "
                 "[--filter-subsystem NAME]\n";
}

std::optional<Options> parseArgs(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) {
            options.inputPath = argv[++i];
        } else if (arg == "--summary") {
            options.summary = true;
        } else if (arg == "--fail-on" && i + 1 < argc) {
            options.failOn = logLevelFromString(argv[++i]);
            if (*options.failOn == LogLevel::Unknown) {
                return std::nullopt;
            }
        } else if (arg == "--filter-subsystem" && i + 1 < argc) {
            options.filterSubsystem = argv[++i];
        } else if (arg == "--help") {
            printUsage();
            std::exit(0);
        } else {
            return std::nullopt;
        }
    }

    if (options.inputPath.empty()) {
        return std::nullopt;
    }
    return options;
}

int main(int argc, char** argv) {
    auto parsed = parseArgs(argc, argv);
    if (!parsed) {
        printUsage();
        return 1;
    }
    Options options = *parsed;

    std::ifstream input(options.inputPath);
    if (!input) {
        std::cerr << "Could not open input file: " << options.inputPath << "\n";
        return 1;
    }

    LogParser parser;
    FailureAnalyzer analyzer;
    std::string line;
    int skipped = 0;

    while (std::getline(input, line)) {
        auto entry = parser.parseLine(line);
        if (!entry) {
            skipped++;
            continue;
        }
        if (options.filterSubsystem && entry->subsystem != *options.filterSubsystem) {
            continue;
        }
        analyzer.add(*entry);
    }

    if (options.summary) {
        std::cout << "Total parsed entries: " << analyzer.total() << "\n";
        std::cout << "Skipped lines: " << skipped << "\n";
        std::cout << "INFO: " << analyzer.count(LogLevel::Info) << "\n";
        std::cout << "WARN: " << analyzer.count(LogLevel::Warn) << "\n";
        std::cout << "ERROR: " << analyzer.count(LogLevel::Error) << "\n";

        std::cout << "\nEntries by subsystem:\n";
        for (const auto& item : analyzer.countsBySubsystem()) {
            std::cout << "  " << item.first << ": " << item.second << "\n";
        }

        std::cout << "\nFailure signatures:\n";
        auto signatures = analyzer.failureSignatures();
        if (signatures.empty()) {
            std::cout << "  none\n";
        } else {
            for (const auto& signature : signatures) {
                std::cout << "  " << signature.second << "x " << signature.first << "\n";
            }
        }
    }

    if (options.failOn && analyzer.containsAtLeast(*options.failOn)) {
        return 2;
    }
    return 0;
}
