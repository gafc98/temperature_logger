#ifndef _LASER_INV_KIN_
#define _LASER_INV_KIN_

#include <iostream>
#include <cmath>
#include <fstream>
#include "pca9685.cpp"

#define MAX_SERVO 600
#define MIN_SERVO 100

class InvKin
{
public:
    InvKin(PCA9685 * pwm, uint8_t phi_channel, uint8_t theta_channel) : _pwm(pwm), _phi_channel(phi_channel), _theta_channel(theta_channel) {}

    void servo_range_sweep()
    {
        for (uint16_t a0 = MIN_SERVO; a0 < MAX_SERVO; a0++)
        {
            _pwm->set_PWM(_phi_channel, 0, a0);
            usleep(200000);
        }
        for (uint16_t a1 = MIN_SERVO; a1 < MAX_SERVO; a1++)
        {
            _pwm->set_PWM(_theta_channel, 0, a1);
            usleep(200000);
        }
    }

    void make_xy_square()
    {
        std::cout << "Making square.\n";
        float X, Y = -1.0, step = 0.01;
        for (X = -1.0; X <= 1.0; X += step)
        {
            move_xy(X, Y);
            usleep(20000);
        }
        for (Y = -1.0; Y <= 1.0; Y += step)
        {
            move_xy(X, Y);
            usleep(20000);
        }
        for (X = 1.0; X >= -1.0; X -= step)
        {
            move_xy(X, Y);
            usleep(20000);
        }
        for (Y = 1.0; Y >= -1.0; Y -= step)
        {
            move_xy(X, Y);
            usleep(20000);
        }
    }

    void perform_calibration()
    {
        // calibrates the values for a11, a12, a21, a22, b1, b2;
        // such that [phi; theta] = A * [X; Y] + b --> inverse kinematics

        // go to startup position
        int16_t phi = (MAX_SERVO + MIN_SERVO) / 2, theta = (MAX_SERVO + MIN_SERVO) / 2;
        _pwm->set_PWM(_phi_channel, 0, phi);
        _pwm->set_PWM(_theta_channel, 0, theta);

        uint16_t phi1, phi2, phi3, phi4, theta1, theta2, theta3, theta4;
        // find phi and theta that match (X,Y) -> (1,1)
        menu_selection(1, 1, phi, theta);
        phi1 = phi;
        theta1 = theta;
        // find phi and theta that match (X,Y) -> (-1,1)
        menu_selection(-1, 1, phi, theta);
        phi2 = phi;
        theta2 = theta;
        // find phi and theta that match (X,Y) -> (-1,-1)
        menu_selection(-1, -1, phi, theta);
        phi3 = phi;
        theta3 = theta;
        // find phi and theta that match (X,Y) -> (1,-1)
        menu_selection(1, -1, phi, theta);
        phi4 = phi;
        theta4 = theta;

        compute_least_squares_solution(phi1, phi2, phi3, phi4, theta1, theta2, theta3, theta4);

        std::cout << "Finished calibration.\n";
    }

    void move_xy(float X, float Y)
    {
        _pwm->set_PWM(_phi_channel, 0, compute_phi(X, Y));
        _pwm->set_PWM(_theta_channel, 0, compute_theta(X, Y));
    }

    inline uint16_t compute_phi(float X, float Y) const
    {
        return static_cast<uint16_t>(round(a11*X + a12*Y + b1));
    }

    inline uint16_t compute_theta(float X, float Y) const
    {
        return static_cast<uint16_t>(round(a21*X + a22*Y + b2));
    }

    void save_cal()
    {
        std::ofstream file("laser_servo_kin.cal", std::ios::trunc);
        if (!file)
            std::cerr << "Error: Cannot write to file 'laser_servo_kin.cal'" << std::endl;

        file << a11 << "\n" << a12 << "\n" << a21 << "\n" << a22 << "\n" << b1 << "\n" << b2;
    }

    bool load_cal()
    {
        std::ifstream file("laser_servo_kin.cal");
        if (!file)
            return false; // File does not exist: return false

        file >> a11 >> a12 >> a21 >> a22 >> b1 >> b2;

        if (file.fail())
            std::cerr << "Failed to read inverse kinematics calibration values.\n";

        return true;
    }

private:
    void compute_least_squares_solution(uint16_t phi1, uint16_t phi2, uint16_t phi3, uint16_t phi4,
        uint16_t theta1, uint16_t theta2, uint16_t theta3, uint16_t theta4)
    {
        a11 = phi1/4.0-phi2/4.0-phi3/4.0+phi4/4.0;
        a12 = phi1/4.0+phi2/4.0-phi3/4.0-phi4/4.0;
        a21 = theta1/4.0-theta2/4.0-theta3/4.0+theta4/4.0;
        a22 = theta1/4.0+theta2/4.0-theta3/4.0-theta4/4.0;
        b1 = phi1/4.0+phi2/4.0+phi3/4.0+phi4/4.0;
        b2 = theta1/4.0+theta2/4.0+theta3/4.0+theta4/4.0;
    }

    void menu_selection(int8_t X, int8_t Y, int16_t & phi, int16_t & theta)
    {
        char choice;
        uint8_t step_size = 5, delete_n_lines;
        bool menu_alive = true;
        while (menu_alive)
        {
            delete_n_lines = 10;
            std::cout << "Set laser pointer to coordinates (X,Y) -> (" << static_cast<int>(X) << "," << static_cast<int>(Y) << ") : (phi,theta) -> (" << phi << "," << theta << ")\n";
            std::cout << "Current step size: " << static_cast<int>(step_size) << "\n";
            std::cout << "Menu:\n";
            std::cout << " - W: +theta step\n";
            std::cout << " - A: -phi step\n";
            std::cout << " - S: -theta step\n";
            std::cout << " - D: +phi step\n";
            std::cout << " - F: finalize\n";
            std::cout << " - C: change step size\n";
            std::cout << "Enter your choice: ";
            std::cin >> choice;

            if (choice == 'w' || choice == 'W')
            {
                theta += step_size;
                _pwm->set_PWM(_theta_channel, 0, theta);
            }
            else if (choice == 'a' || choice == 'A')
            {
                phi -= step_size;
                _pwm->set_PWM(_phi_channel, 0, phi);
            }
            else if (choice == 's' || choice == 'S')
            {
                theta -= step_size;
                _pwm->set_PWM(_theta_channel, 0, theta);
            }
            else if (choice == 'd' || choice == 'D')
            {
                phi += step_size;
                _pwm->set_PWM(_phi_channel, 0, phi);
            }
            else if (choice == 'c' || choice == 'C')
            {
                unsigned int new_step_size;
                std::cout << "Enter new step size (1 to 50): ";
                delete_n_lines += 1;
                std::cin >> new_step_size;
                // Validate input
                if (std::cin.fail() || new_step_size < 1 || new_step_size > 50)
                {
                    //std::cout << "Invalid step size. Please enter a number between 1 and 50.\n";
                    //delete_n_lines += 1;
                    std::cin.clear(); // clear error flag
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // discard bad input
                }
                else
                {
                    step_size = new_step_size;
                }
            }
            else if (choice == 'f' || choice == 'F')
            {
                std::cout << "Finished for (X,Y) -> (" << static_cast<int>(X) << "," << static_cast<int>(Y) << ") : (phi,theta) -> (" << phi << "," << theta << ")\n";
                menu_alive = false;
            }
            //else
            //{
            //    std::cout << "Invalid option. Try again.\n";
            //}

            for (uint8_t i = 0; i < delete_n_lines; i++)
            {
                std::cout << "\033[1A"   // Move cursor up one line
                          << "\033[2K"; // Clear entire line
            }
        }
    }
    float a11, a12, a21, a22, b1, b2;
    PCA9685 * _pwm;
    uint8_t _phi_channel, _theta_channel;
};

#endif // _LASER_INV_KIN_
