logger: main.cpp
	g++ -fdiagnostics-color=always -g main.cpp -Ofast -std=c++17 -o logger

clean:
	rm logger
