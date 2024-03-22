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
        float T_int, T, P, H;
        float average_T_int = 0, average_T = 0, average_H = 0, average_P = 0;
        int ret_code_sum = 0;
        for (size_t i = 0; i < AVERAGE; i++)
        {
		    T_int = -66.875 + 218.75 * adc.read_voltage() / 3.3;
            average_T_int += T_int;
            ret_code_sum += bme280.read_all(T, P, H);
            average_T += T;
            average_H += H;
            average_P += P;
            usleep(SLEEP_TIME);
        }
        average_T_int /= AVERAGE;
        average_T /= AVERAGE;
        average_H /= AVERAGE;
        average_P /= AVERAGE;

        auto timenow = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

        std::ostringstream info;
        info << std::string(strtok(ctime(&timenow), "\n")) << '\t' << average_T << '\t' << average_H << '\t' << average_P << '\t' << average_T_int << '\t' << ret_code_sum;

        std::cout << info.str() << std::endl;

        dumper.dump(info.str());
    }

	return 0;
}