#include "i2c_bus.cpp"
#include "fonts.hpp"
#include <string>

#ifndef _SSD1306_
#define _SSD1306_

#define COMMAND_REG 0x80
#define DATA_REG 0x40
#define ON_CMD 0xAF
#define OFF_CMD 0xAE
#define NORMAL_DISPLAY_CMD 0xA6
#define PAGE_ADDRESSING_MODE 0x02

class SSD1306
{
public:
    SSD1306(I2C_BUS* i2c_bus, __u16 device_address = 0x3C)
	{
		_i2c_bus = i2c_bus;
		_device_address = device_address;
		set_config();
	}

    void set_cursor(__u8 x, __u8 y)
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        write8(COMMAND_REG, 0x00 + (x & 0x0F));
        write8(COMMAND_REG, 0x10 + ((x >> 4) & 0x0F));
        write8(COMMAND_REG, 0xB0 + y);
    }

    void clear_display()
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        for (__u8 page = 0; page <= 7; page++)
        {
            set_cursor(0, page);
            for (__u8 col = 0; col <= 127; col++)
                write8(DATA_REG, 0x00);
        }
        set_cursor(0, 0);
    }

    void write_col(__u8 byte)
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        write8(DATA_REG, byte);
    }

    void turn_off_display()
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        write8(COMMAND_REG, OFF_CMD);
    }

    void put_string(std::string str)
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        for (char & ch : str)
            put_char(ch);
    }

    void put_char(char ch)
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        if (ch < 32 || ch > 127) 
            ch = ' ';
        ch -= 32; // Font array starts at 0, ASCII starts at 32, 2 is offset
        for (__u8 i = 0; i < font8x8[0]; i++) // font8x8[0] is font width
            write8(DATA_REG, font8x8[ch * 8 + 2 + i]);
    }

private:
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

    __u32 read24(__u8 reg)
    {
        __u8 buffer[3];
        buffer[0] = __u8(reg);
        _i2c_bus->write_to_device(&reg, 1);
        _i2c_bus->read_from_device(buffer, 3);
        return __u32(buffer[0]) << 16 | __u32(buffer[1]) << 8 | __u32(buffer[2]);
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


    void set_config()
    {
        // first set device address to ensure correct communication
        _i2c_bus->set_device_address(_device_address);
        // turn on display
        std::cout << "SSD1306: turning on display\n";
        write8(COMMAND_REG, ON_CMD);
        // set normal display mode
        std::cout << "SSD1306: setting normal display display\n";
        write8(COMMAND_REG, NORMAL_DISPLAY_CMD);
        // set page adressing mode
        std::cout << "SSD1306: setting page adressing mode\n";
        write8(COMMAND_REG, 0x20);
        write8(COMMAND_REG, PAGE_ADDRESSING_MODE);
        // charge pump
        std::cout << "SSD1306: charging pump\n";
        write8(COMMAND_REG, 0x8d);
        write8(COMMAND_REG, 0x14);

        clear_display();
        std::cout << "SSD1306: setup complete!\n";
    }

	float _conversion_factor;
	__u16 _device_address;
	I2C_BUS* _i2c_bus;
};


#endif