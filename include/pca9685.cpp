#include "i2c_bus.cpp"

#ifndef _PCA9685_
#define _PCA9685_

#include <thread>

#define PCA9685_I2C_ADDRESS 0x40      /**< Default PCA9685 I2C Slave Address */
#define FREQUENCY_OSCILLATOR 25000000 /**< Int. osc. frequency in datasheet */

#define PCA9685_PRESCALE_MIN 3   /**< minimum prescale value */
#define PCA9685_PRESCALE_MAX 255 /**< maximum prescale value */
#define PCA9685_PRESCALE 0xFE     /**< Prescaler for PWM output frequency */
#define PCA9685_LED0_ON_L 0x06  /**< LED0 on tick, low byte*/

#define PCA9685_MODE1 0x00      /**< Mode Register 1 */
#define MODE1_SLEEP 0x10   /**< Low power mode. Oscillator off */
#define MODE1_RESTART 0x80 /**< Restart enabled */
#define MODE1_AI 0x20      /**< Auto-Increment enabled */

class PCA9685
{
public:
    PCA9685(I2C_BUS* i2c_bus, __u16 device_address = PCA9685_I2C_ADDRESS, __u32 oscillator_frequency = FREQUENCY_OSCILLATOR)
	{
		_i2c_bus = i2c_bus;
		_device_address = device_address;
        _oscillator_frequency = oscillator_frequency;
	}

    void set_PWM_freq(float freq)
    {
        _i2c_bus->set_device_address(_device_address); // point towards correct device for future read/writes

        float pre_scale_val = ((_oscillator_frequency / (freq * 4096.0)) + 0.5) - 1;
        if (pre_scale_val < PCA9685_PRESCALE_MIN)
        {
            pre_scale_val = PCA9685_PRESCALE_MIN;
            std::cout << "PCA9685: Prescale minimum hit while setting PWM frequency!" << std::endl;
        }
            
        if (pre_scale_val > PCA9685_PRESCALE_MAX)
        {
            pre_scale_val = PCA9685_PRESCALE_MAX;
            std::cout << "PCA9685: Prescale maximum hit while setting PWM frequency!" << std::endl;
        }
            
        __u8 pre_scale = (__u8)pre_scale_val;

        __u8 old_mode = read8(PCA9685_MODE1);
        __u8 new_mode = (old_mode & ~MODE1_RESTART) | MODE1_SLEEP; // sleep
        write8(PCA9685_MODE1, new_mode);                          // go to sleep
        write8(PCA9685_PRESCALE, pre_scale); // set the prescaler
        write8(PCA9685_MODE1, old_mode);
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
        // This sets the MODE1 register to turn on auto increment.
        write8(PCA9685_MODE1, old_mode | MODE1_RESTART | MODE1_AI);
    }

    void set_PWM(__u8 num, __u16 on, __u16 off)
    {
        _i2c_bus->set_device_address(_device_address); // point towards correct device for future read/writes

        __u8 buffer[5];
        buffer[0] = PCA9685_LED0_ON_L + 4 * num;
        buffer[1] = on;
        buffer[2] = on >> 8;
        buffer[3] = off;
        buffer[4] = off >> 8;

        _i2c_bus->write_to_device(buffer, 5);
    }
    
    void wake_up()
    {
        __u8 cur_mode = read8(PCA9685_MODE1);
        __u8 wake_up = cur_mode & ~MODE1_SLEEP; // set sleep bit low
        write8(PCA9685_MODE1, wake_up);
    }

    void turn_off()
    {
        for (__u8 i = 0; i < 16; i++)
            set_PWM(i, 0, 0);
    }

    ~PCA9685()
    {
        turn_off();
    }

private:
    I2C_BUS* _i2c_bus;
    __u16 _device_address;
    __u32 _oscillator_frequency;

    __u8 read8(__u8 reg)
    {
        _i2c_bus->write_to_device(&reg, 1);
        _i2c_bus->read_from_device(&reg, 1);
        return reg;
    }

    void write8(__u8 reg, __u8 byte)
    {
        __u8 buffer[2];
        buffer[0] = reg;
        buffer[1] = byte;
        _i2c_bus->write_to_device(buffer, 2);
    }
};

#endif //_PCA9685_