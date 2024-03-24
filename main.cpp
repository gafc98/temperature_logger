#include <iostream>
#include <ctime>
#include <chrono>
#include <string.h>
#include <sstream>
#include "include/i2c_bus.cpp"
#include "include/ads1115.cpp"
#include "include/bme280.cpp"
#include "include/dumper.cpp"
#include "include/ssd1306.cpp"

#define SAMPLE_TIME 60000000 // useconds
#define AVERAGE 60 // number of samples to average over the sampling time
#define SLEEP_TIME SAMPLE_TIME / AVERAGE

int main()
{
    // get main i2c bus object
	I2C_BUS i2c_bus = I2C_BUS(0);

    // get sensor objects
	BME280 bme280 = BME280(&i2c_bus, 0x76);
    ADS1115 adc = ADS1115(&i2c_bus, 0x48);
    adc.set_config(1);
    SSD1306 display(&i2c_bus, 0x3C);

    // simple dumper to place logs in
    Dumper dumper("log.txt");

    while (true)
    {
        float T_int, T, P, H;
        float average_T_int = 0, average_T = 0, average_H = 0, average_P = 0;
        int ret_code_sum = 0;
        for (size_t i = 0; i < AVERAGE; i++)
        {
            auto t_start = std::chrono::high_resolution_clock::now();

		    T_int = -66.875 + 218.75 * adc.read_voltage() / 3.3;
            average_T_int += T_int;
            ret_code_sum += bme280.read_all(T, P, H);
            average_T += T;
            average_H += H;
            average_P += P;

            //display.clear_display();
            display.set_cursor(0, 0);
            display.put_string(to_string(T));
            display.set_cursor(0, 1);
            display.put_string(to_string(H));
            display.set_cursor(0, 2);
            display.put_string(to_string(P));
            display.set_cursor(0, 3);
            display.put_string(to_string(T_int));

            auto t_end = std::chrono::high_resolution_clock::now();
            float elapsed_time_us = std::chrono::duration<float, std::micro>(t_end - t_start).count();

            usleep(SLEEP_TIME - elapsed_time_us);

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