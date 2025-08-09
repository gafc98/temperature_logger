#include <iostream>
#include <fcntl.h>	/* For O_RDWR */
#include <unistd.h> /* For open(), creat() */
#include <sys/ioctl.h>
#include <string.h>
extern "C"
{
    #include <linux/i2c-dev.h>
}

#ifndef _I2C_BUS_
#define _I2C_BUS_

class I2C_BUS
{
public:
    I2C_BUS(__u16 i2c_bus = 0)
    {
        char filename[20];
        snprintf(filename, 19, "/dev/i2c-%d", i2c_bus);
        file = open(filename, O_RDWR);

        if (file < 0)
            throw std::runtime_error("Error opening the i2c device. Does the device exist? Run as Sudo?\n");
    }
    
    void set_device_address(__u16 new_device_address)
    {
        if (_device_address == new_device_address && _first_address_was_set)
            return; // first device has been set and new device is the same as the last one, no need to change devices.
        
        _device_address = new_device_address;
        
        if (ioctl(file, I2C_SLAVE, _device_address) < 0)
            throw std::runtime_error("Error setting board address.\n");
        
        if (!_first_address_was_set)
            _first_address_was_set = true;
    }

    template <typename T>
    void write_to_device(__u8* buffer, T num_bytes)
    {
        if (write(file, buffer, num_bytes) != num_bytes)
        {
            std::string error = std::string("Writting ") + std::to_string(num_bytes) + std::string(" bytes to device ") + std::to_string(_device_address) + std::string(" failed!");
            throw std::runtime_error(error);
        }
    }

    template <typename T>
    void read_from_device(__u8* buffer, T num_bytes)
    {
        if (read(file, buffer, num_bytes) != num_bytes)
        {
            std::string error = std::string("Reading ") + std::to_string(num_bytes) + std::string(" bytes from device ") + std::to_string(_device_address) + std::string(" failed!");
            throw std::runtime_error(error);
        }
    }
    
    ~I2C_BUS()
    {
        close(file);
    }
    
    int file;
    
private:
    __u16 _device_address;
    bool _first_address_was_set = false;
};

#endif
