CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17

logger: main.cpp $(wildcard include/*.cpp)
	$(CXX) $(CXXFLAGS) main.cpp -o logger

.PHONY: clean
clean:
	rm -f logger
