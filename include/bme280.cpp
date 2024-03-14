#include "i2c_bus.cpp"

enum {
  BME280_REGISTER_DIG_T1 = 0x88,
  BME280_REGISTER_DIG_T2 = 0x8A,
  BME280_REGISTER_DIG_T3 = 0x8C,

  BME280_REGISTER_DIG_P1 = 0x8E,
  BME280_REGISTER_DIG_P2 = 0x90,
  BME280_REGISTER_DIG_P3 = 0x92,
  BME280_REGISTER_DIG_P4 = 0x94,
  BME280_REGISTER_DIG_P5 = 0x96,
  BME280_REGISTER_DIG_P6 = 0x98,
  BME280_REGISTER_DIG_P7 = 0x9A,
  BME280_REGISTER_DIG_P8 = 0x9C,
  BME280_REGISTER_DIG_P9 = 0x9E,

  BME280_REGISTER_DIG_H1 = 0xA1,
  BME280_REGISTER_DIG_H2 = 0xE1,
  BME280_REGISTER_DIG_H3 = 0xE3,
  BME280_REGISTER_DIG_H4 = 0xE4,
  BME280_REGISTER_DIG_H5 = 0xE5,
  BME280_REGISTER_DIG_H6 = 0xE7,

  BME280_REGISTER_CHIPID = 0xD0,
  BME280_REGISTER_VERSION = 0xD1,
  BME280_REGISTER_SOFTRESET = 0xE0,

  BME280_REGISTER_CAL26 = 0xE1, // R calibration stored in 0xE1-0xF0

  BME280_REGISTER_CONTROLHUMID = 0xF2,
  BME280_REGISTER_STATUS = 0XF3,
  BME280_REGISTER_CONTROL = 0xF4,
  BME280_REGISTER_CONFIG = 0xF5,
  BME280_REGISTER_PRESSUREDATA = 0xF7,
  BME280_REGISTER_TEMPDATA = 0xFA,
  BME280_REGISTER_HUMIDDATA = 0xFD
};

typedef struct {
  uint16_t dig_T1; ///< temperature compensation value
  int16_t dig_T2;  ///< temperature compensation value
  int16_t dig_T3;  ///< temperature compensation value

  uint16_t dig_P1; ///< pressure compensation value
  int16_t dig_P2;  ///< pressure compensation value
  int16_t dig_P3;  ///< pressure compensation value
  int16_t dig_P4;  ///< pressure compensation value
  int16_t dig_P5;  ///< pressure compensation value
  int16_t dig_P6;  ///< pressure compensation value
  int16_t dig_P7;  ///< pressure compensation value
  int16_t dig_P8;  ///< pressure compensation value
  int16_t dig_P9;  ///< pressure compensation value

  uint8_t dig_H1; ///< humidity compensation value
  int16_t dig_H2; ///< humidity compensation value
  uint8_t dig_H3; ///< humidity compensation value
  int16_t dig_H4; ///< humidity compensation value
  int16_t dig_H5; ///< humidity compensation value
  int8_t dig_H6;  ///< humidity compensation value
} bme280_calib_data;

class BME280
{
    BME280(I2C_BUS* i2c_bus, __u16 device_address = 0x77)
	{
		_i2c_bus = i2c_bus;
		_device_address = device_address;
		set_config();
	}

    void set_config()
    {
        _i2c_bus->set_device_address(_device_address);

        // reset the device using soft-reset
        write8(BME280_REGISTER_SOFTRESET, 0xB6);

        while(is_reading_calibration())
            usleep(10000);

    read_coefficients();

    }

private:
    bool is_reading_calibration()
    {
        // BME280_REGISTER_STATUS
        //buffer[0] = 0XF3;
        //_i2c_bus->write_to_device(_buffer, 1);
        //_i2c_bus->read_from_device(_buffer, 1);

        __u8 out = read8(0XF3);

        return (out & (1 << 0)) != 0;
    }

    void write8(__u8 reg, __u8 byte)
    {
        __u8 buffer[2];
        buffer[0] = reg;
        buffer[1] = byte;
        _i2c_bus->write_to_device(buffer, 2);
    }

    __u8 read8(__u8 reg)
    {
        _i2c_bus->write_to_device(&reg, 1);
        _i2c_bus->read_from_device(&reg, 1);
        return reg;
    }

    __u16 read16(__u8 reg)
    {
        __u8 buffer[2];
        _i2c_bus->write_to_device(&reg, 1);
        _i2c_bus->read_from_device(buffer, 2);
        return __u16(buffer[0]) << 8 | __u16(buffer[1]);
    }

    __u16 read16_LE(__u8 reg)
    {
        __u16 temp = read16(reg);
        return (temp >> 8) | (temp << 8);
    }

    __s16 readS16_LE(__u8 reg)
    {
        return (__s16)read16_LE(reg);
    }

    void read_coefficients(void)
    {
        _bme280_calib.dig_T1 = read16_LE(BME280_REGISTER_DIG_T1);
        _bme280_calib.dig_T2 = readS16_LE(BME280_REGISTER_DIG_T2);
        _bme280_calib.dig_T3 = readS16_LE(BME280_REGISTER_DIG_T3);

        _bme280_calib.dig_P1 = read16_LE(BME280_REGISTER_DIG_P1);
        _bme280_calib.dig_P2 = readS16_LE(BME280_REGISTER_DIG_P2);
        _bme280_calib.dig_P3 = readS16_LE(BME280_REGISTER_DIG_P3);
        _bme280_calib.dig_P4 = readS16_LE(BME280_REGISTER_DIG_P4);
        _bme280_calib.dig_P5 = readS16_LE(BME280_REGISTER_DIG_P5);
        _bme280_calib.dig_P6 = readS16_LE(BME280_REGISTER_DIG_P6);
        _bme280_calib.dig_P7 = readS16_LE(BME280_REGISTER_DIG_P7);
        _bme280_calib.dig_P8 = readS16_LE(BME280_REGISTER_DIG_P8);
        _bme280_calib.dig_P9 = readS16_LE(BME280_REGISTER_DIG_P9);

        _bme280_calib.dig_H1 = read8(BME280_REGISTER_DIG_H1);
        _bme280_calib.dig_H2 = readS16_LE(BME280_REGISTER_DIG_H2);
        _bme280_calib.dig_H3 = read8(BME280_REGISTER_DIG_H3);
        _bme280_calib.dig_H4 = ((int8_t)read8(BME280_REGISTER_DIG_H4) << 4) |
                         (read8(BME280_REGISTER_DIG_H4 + 1) & 0xF);
        _bme280_calib.dig_H5 = ((int8_t)read8(BME280_REGISTER_DIG_H5 + 1) << 4) |
                         (read8(BME280_REGISTER_DIG_H5) >> 4);
        _bme280_calib.dig_H6 = (int8_t)read8(BME280_REGISTER_DIG_H6);
    }

	float _conversion_factor;
	__u16 _device_address;
	I2C_BUS* _i2c_bus;
	__u8 _buffer[3];
    bme280_calib_data _bme280_calib;
};