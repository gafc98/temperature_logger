i2c_test: main.cpp
	g++ -fdiagnostics-color=always -g main.cpp -Ofast -fconcepts-ts -std=c++17 -o logger

clean:
	rm logger *.txt

bme280: include/bme280.cpp
	g++ -fdiagnostics-color=always -g include/bme280.cpp -Ofast -fconcepts-ts -std=c++17 -o logger.o