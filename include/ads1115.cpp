#include "i2c_bus.cpp"

#ifndef _ADS1115_
#define _ADS1115_

static const float FULL_SCALES[] = {6.144, 4.096, 2.048, 1.024, 0.512, 0.256};

class ADS1115
{
public:
	ADS1115(I2C_BUS* i2c_bus, __u16 device_address = 0x48)
	{
		_i2c_bus = i2c_bus;
		_device_address = device_address;
		set_config(0);
	}

	void set_config(__u8 analog_input, __u8 fs_mode = 2)
	{
		if (analog_input >= 4 || analog_input < 0)
			throw std::runtime_error("analog_input is incorrect.\n");

		if (fs_mode >= 5 || fs_mode < 0)
			throw std::runtime_error("fs_mode is incorrect.\n");

		_conversion_factor = FULL_SCALES[fs_mode] / 32768.0;

		_buffer[0] = 1;
		_buffer[1] = 0b00010000 * analog_input + 0b00000010 * fs_mode + 0b11000000;
		_buffer[2] = 0x83;
		
		// writing to device
		_i2c_bus->set_device_address(_device_address);
		_i2c_bus->write_to_device(_buffer, 3);
		_buffer[0] = 0;
		_i2c_bus->write_to_device(_buffer, 1);
	}

	float read_voltage()
	{
		_i2c_bus->set_device_address(_device_address);
		_i2c_bus->read_from_device(_buffer, 2);
		return _conversion_factor * static_cast<__s16>(_buffer[0] << 8 | _buffer[1]);
	}

private:
	float _conversion_factor;
	__u16 _device_address;
	I2C_BUS* _i2c_bus;
	__u8 _buffer[3];
};

#endif