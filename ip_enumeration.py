import os
import subprocess


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[1;32;40m'
    RED = '\033[1;31;40m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NORMAL = '\033[0;37;40m'


def active_addresses():
    subnet = input("Enter first three octets of a valid /24 subnet: ")
    with open(os.devnull, "wb") as limbo:
        for n in range(1, 255):

            ip = subnet + ".{0}".format(n)
            result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip], stdout=limbo, stderr=limbo).wait()
            if result:
                print(f"{ip} : {Colors.RED}Inactive{Colors.NORMAL}")
            else:
                print(f"{ip} : {Colors.GREEN}ACTIVE{Colors.NORMAL}")

active_addresses()