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
#include "include/laser_pointer_inverse_kinematics.cpp"

#define SAMPLE_TIME 60000000 // useconds
#define AVERAGE 60 // number of samples to average over the sampling time
#define SLEEP_TIME SAMPLE_TIME / AVERAGE

// options
__u8 i2c_bus_number = 1;
bool log_to_console = false;
bool log_to_display = true;

class Load_TH_To_XY_Parameters
{
public:
    bool load_cal()
    {
        std::ifstream file("TH_to_XY.cal");
        bool success = true;
        if (!file)
            return false; // File does not exist: return false

        file >> _denominator_T >> _offset_T >> _denominator_H >> _offset_H;

        if (file.fail())
            std::cerr << "Failed to read TH_to_XY conversion values.\n";

        return true;
    }

    inline float compute_X(float T)
    {
        return (T + _offset_T) / _denominator_T;
    }

    inline float compute_Y(float H)
    {
        return (H + _offset_H) / _denominator_H;
    }
private:
    float _denominator_T = 15.0, _offset_T = -15.0, _denominator_H = 35.0, _offset_H = -55.0; // linear conversion variables
};

int start_measuring()
{
    // get main i2c bus object
    I2C_BUS i2c_bus = I2C_BUS(i2c_bus_number);

    // get oled display object
    SSD1306 display(&i2c_bus, 0x3C);
    if (log_to_display)
    {
    display.set_config();
        display.clear_display();
        display.put_string("Inilializing...");
        usleep(1000000);
    }

    // get sensor objects
    BME280 bme280_interior = BME280(&i2c_bus, 0x77);
    BME280 bme280_exterior = BME280(&i2c_bus, 0x76);
    ADS1115 adc = ADS1115(&i2c_bus, 0x48);
    adc.set_config(1);

    // get PWM servo controller object
    PCA9685 pwm = PCA9685(&i2c_bus, 0x40);

    // pwm initialization
    pwm.turn_off();
    usleep(10000);
    pwm.set_PWM_freq(50);
    pwm.wake_up();

    // Load TH_To_XY conversion parameters
    Load_TH_To_XY_Parameters TH_To_XY;
    TH_To_XY.load_cal();

    // initiate inverse kinematics object
    InvKin inv_kin = InvKin(&pwm, 14, 15);
    if (!inv_kin.load_cal())
    {
        inv_kin.perform_calibration();
        inv_kin.save_cal();
    }
    inv_kin.make_xy_square();

    // simple dumper to place logs in
    Dumper dumper("log.txt");

    display.clear_display();

    while (true)
    {
        float T_int, T_interior, P_interior, H_interior, T_exterior, P_exterior, H_exterior;
        float average_T_int = 0, average_T_interior = 0, average_H_interior = 0, average_P_interior = 0, average_T_exterior = 0, average_H_exterior = 0, average_P_exterior = 0;
        int ret_code_sum = 0;
        for (size_t i = 0; i < AVERAGE; i++)
        {
            auto t_start = std::chrono::high_resolution_clock::now();

            T_int = -66.875 + 218.75 * adc.read_voltage() / 3.3;
            average_T_int += T_int;
            ret_code_sum += bme280_interior.read_all(T_interior, P_interior, H_interior) + bme280_exterior.read_all(T_exterior, P_exterior, H_exterior);
            average_T_interior += T_interior;
            average_H_interior += H_interior;
            average_P_interior += P_interior;
            average_T_exterior += T_exterior;
            average_H_exterior += H_exterior;
            average_P_exterior += P_exterior;
            if (log_to_display)
            {
                if (i % 2 ==0)
                {
                    display.clear_display();
                    display.set_cursor(0, 0);
                    display.put_string("Interior");
                    display.set_cursor(0, 1);
                    display.put_string(to_string(T_interior));
                    display.set_cursor(0, 2);
                    display.put_string(to_string(H_interior));
                    display.set_cursor(0, 3);
                    display.put_string(to_string(P_interior));
                    display.set_cursor(0, 4);
                    display.put_string(to_string(T_int));
                }
                else
                {    
                    display.clear_display();
                    display.set_cursor(0, 0);
                    display.put_string("Exterior");
                    display.set_cursor(0, 1);
                    display.put_string(to_string(T_exterior));
                    display.set_cursor(0, 2);
                    display.put_string(to_string(H_exterior));
                    display.set_cursor(0, 3);
                    display.put_string(to_string(P_exterior));
                }
            }
            auto t_end = std::chrono::high_resolution_clock::now();
            float elapsed_time_us = std::chrono::duration<float, std::micro>(t_end - t_start).count();

            usleep(SLEEP_TIME - elapsed_time_us);
        }
        average_T_int /= AVERAGE;
        average_T_interior /= AVERAGE;
        average_H_interior /= AVERAGE;
        average_P_interior /= AVERAGE;
        average_T_exterior /= AVERAGE;
        average_H_exterior /= AVERAGE;
        average_P_exterior /= AVERAGE;
        auto timenow = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

        inv_kin.move_xy(TH_To_XY.compute_X(average_T_exterior), TH_To_XY.compute_Y(average_H_exterior), 5);

        std::ostringstream info;
        info << std::string(strtok(ctime(&timenow), "\n")) << '\t' << average_T_interior << '\t' << average_H_interior << '\t' << average_P_interior << '\t' << average_T_int << '\t' << ret_code_sum << '\t' << average_T_exterior << '\t' << average_H_exterior << '\t' << average_P_exterior;
        if (log_to_console)
            std::cout << info.str() << std::endl;

        dumper.dump(info.str());
    }

    return 0;
}

int main(int argc, char* argv[])
{
    for (__u8 i = 1; i < argc; i++)
    {
        // Check if the argument starts with "-opt" (option flag)
        if (argv[i][0] == '-')
        {
            if (strcmp(argv[i], "-i2c_bus") == 0)
                i2c_bus_number = std::atoi(argv[i + 1]);
            else if (strcmp(argv[i], "-log_to_console") == 0)
                log_to_console = true;
            else if (strcmp(argv[i], "-no_screen") == 0)
                log_to_display = false;
            else
            {
                std::cout <<    "This program is used to log the temperature loggings to a log file.\n"
                                "Usage:\n"
                                ".\\logger [-help] [-i2c_bus N] [-log_to_console] [-no_screen]\nRuntime options available:\n"
                                "-i2c_bus N         Allows the user to specify the i2c bus number (1 is default);\n"
                                "-log_to_console    Logging will also be done on console along with file;\n"
                                "-no_screen         Will disable SSD1306 screen logging.\n" << std::endl;
                return 0;
            }
        }
    }

    while (true)
    {
        try
        {
            start_measuring();
        }
        catch (const std::runtime_error& e)
        {
            // restart measuring after 10 seconds to try to fight error...
            if (log_to_display)
            std::cout << std::string("Error occurred, restarting in 10 seconds. Error message:\n") + e.what() + std::string("\n");

            Dumper error_dump("error_logs.txt");
            auto timenow = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
            std::ostringstream error_info;
            error_info << std::string(strtok(ctime(&timenow), "\n")) << " - " << e.what() << std::endl;
            error_dump.dump(error_info.str());

            usleep(10000000);
        }
    }
    return 0;
}
