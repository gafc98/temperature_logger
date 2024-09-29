import sys
import datetime
from file_read_backwards import FileReadBackwards # can be installed via pip, also ew, camel case

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
LOG_FILE_NAME = "log.txt"

def print_logs(from_date, path=LOG_FILE_NAME):
    ref_date = datetime.datetime.strptime(from_date, DATE_FORMAT)
    with FileReadBackwards(path) as log_file:
        for line in log_file:
            line_date = datetime.datetime.strptime(line.split("\t")[0], DATE_FORMAT)
            if line_date > ref_date:
                print(line, end="\n")
            else:
                return

def logs_to_list(from_date, to_date, path=LOG_FILE_NAME, subsample=1):
    lines_list = []
    with FileReadBackwards(path) as log_file:
        for i, line in enumerate(log_file):
            if (i % subsample != 0):
                continue
            line_date = datetime.datetime.strptime(line.split("\t")[0], DATE_FORMAT)
            if line_date < from_date:
                return lines_list
            if line_date < to_date:
                lines_list.append(line)

if __name__ == '__main__':
    print_logs(sys.argv[1])
