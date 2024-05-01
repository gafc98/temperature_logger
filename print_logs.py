import sys
import datetime
from file_read_backwards import FileReadBackwards # can be installed via pip, also ew, camel case

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

def main():
    ref_date = datetime.datetime.strptime(sys.argv[1], DATE_FORMAT )
    with FileReadBackwards("log.txt") as log_file:
        for line in log_file:
            line_date = datetime.datetime.strptime(line.split("\t")[0], DATE_FORMAT)
            if line_date > ref_date:
                print(line, end="\n")
            else:
                return

if __name__ == '__main__':
    main()
