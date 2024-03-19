#include <iostream>
#include <ctime>
#include <chrono>
#include <string.h>
#include "include/i2c_bus.cpp"
//#include "include/ads1115.cpp"
#include "include/bme280.cpp"
#include "include/dumper.cpp"

#define SAMPLE_TIME 60000000 // useconds
#define AVERAGE 60 // number of samples to average over the sampling time
#define SLEEP_TIME SAMPLE_TIME / AVERAGE

int main()
{
	I2C_BUS i2c_bus = I2C_BUS(0);
	BME280 bme280 = BME280(&i2c_bus, 0x76);
    float T, P, H;
	bme280.read_all(T, P, H);

    std::cout << "T = " << T <<  std::endl;
    std::cout << "P = " << P <<  std::endl;
    std::cout << "H = " << H <<  std::endl;

	return 0;
}

/**
int main()
{
	I2C_BUS i2c_bus = I2C_BUS(0);
	ADS1115 adc = ADS1115(&i2c_bus, 0x48);
	adc.set_config(1);
    
    Dumper dumper("log.txt");

	while (true)
	{
        float average_T = 0;
        for (size_t i = 0; i < AVERAGE; i++)
        {
		    float T = -66.875 + 218.75 * adc.read_voltage() / 3.3;
            average_T += T;
            usleep(SLEEP_TIME);
        }
        average_T /= AVERAGE;

		auto timenow = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

        std::string info_str = std::string(strtok(ctime(&timenow), "\n"));

        info_str += std::string("\t") + std::to_string(average_T);

    	std::cout << info_str << std::endl;

        dumper.dump(info_str);
	}
	return 0;
}
**/
