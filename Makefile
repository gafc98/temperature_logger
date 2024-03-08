i2c_test: main.cpp
	g++ -fdiagnostics-color=always -g main.cpp -Ofast -fconcepts-ts -std=c++17 -o logger

clean:
	rm logger *.txt
