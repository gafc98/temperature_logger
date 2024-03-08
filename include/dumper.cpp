// basic file operations
#include <iostream>
#include <fstream>
#include <string>
using namespace std;

class Dumper
{
public:
    Dumper(const string file_name) : _file_name(file_name) {}

    void dump(const string line)
    {
        fstream file(_file_name, std::ios::out | std::ios::app);
        if (file.is_open())
        {
            file << line << endl;
        }
        else
        {
            file.close();
            throw std::runtime_error("Error opening file!");
        }
        file.close();
    }

private:
    string _file_name;
};