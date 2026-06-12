CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Wpedantic -O2 -Iinclude
BUILD_DIR := build

APP := $(BUILD_DIR)/controller_log_monitor
TEST := $(BUILD_DIR)/test_parser

APP_SRC := src/main.cpp src/LogParser.cpp src/FailureAnalyzer.cpp
TEST_SRC := tests/test_parser.cpp src/LogParser.cpp src/FailureAnalyzer.cpp

.PHONY: all test clean

all: $(APP)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(APP): $(APP_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(APP_SRC) -o $(APP)

$(TEST): $(TEST_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(TEST_SRC) -o $(TEST)

test: $(TEST)
	$(TEST)

clean:
	rm -rf $(BUILD_DIR)
