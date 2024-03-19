#include <iostream>
#include <ctime>
#include <chrono>
#include <string.h>
#include <sstream>
#include "include/i2c_bus.cpp"
#include "include/ads1115.cpp"
#include "include/bme280.cpp"
#include "include/dumper.cpp"

#define SAMPLE_TIME 60000000 // useconds
#define AVERAGE 60 // number of samples to average over the sampling time
#define SLEEP_TIME SAMPLE_TIME / AVERAGE

int main()
{
	I2C_BUS i2c_bus = I2C_BUS(0);
	BME280 bme280 = BME280(&i2c_bus, 0x76);
    ADS1115 adc = ADS1115(&i2c_bus, 0x48);
    adc.set_config(1);

    Dumper dumper("log.txt");

    while (true)
    {
        float T, P, H;
        float average_T_int = 0;
        for (size_t i = 0; i < AVERAGE; i++)
        {
		    float T_int = -66.875 + 218.75 * adc.read_voltage() / 3.3;
            average_T_int += T_int;
            usleep(SLEEP_TIME);
        }
        average_T_int /= AVERAGE;
        int ret_code = bme280.read_all(T, P, H);

        auto timenow = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

        std::ostringstream info;
        info << std::string(strtok(ctime(&timenow), "\n")) << '\t' << T << '\t' << H << '\t' << P << '\t' << average_T_int << '\t' << ret_code;

        std::cout << info.str() << std::endl;

        dumper.dump(info.str());
    }

	return 0;
}