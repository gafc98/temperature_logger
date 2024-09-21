import sys
import datetime
from file_read_backwards import FileReadBackwards # can be installed via pip, also ew, camel case

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
LOG_FILE_NAME = "log.txt"

def print_logs(from_date):
    ref_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
    with FileReadBackwards(LOG_FILE_NAME) as log_file:
        for line in log_file:
            line_date = datetime.datetime.strptime(line.split("\t")[0], DATE_FORMAT)
            if line_date > ref_date:
                print(line, end="\n")
            else:
                return

def logs_to_list(from_date, to_date):
    lines_list = []
    with FileReadBackwards(LOG_FILE_NAME) as log_file:
        for line in log_file:
            line_date = datetime.datetime.strptime(line.split("\t")[0], DATE_FORMAT)
            if line_date < from_date:
                break
            if line_date < to_date:
                lines_list.append(line)
    return lines_list

if __name__ == '__main__':
    print_logs(sys.argv[1])
