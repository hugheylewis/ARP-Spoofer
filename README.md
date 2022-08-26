# ARP-Spoofer
arp_spoofer.py is an ARP poisoning Python script intended to facilitate man-in-the-middle (MITM) attacks on a local subnet.
Users should include the victim IP address, the router IP address, and the amount of time (in minutes) for the attack to persist for.
  
Required and optional parameters (*** indicates a required parameter)
  -b --bypass: Bypasses the IP enumeration of a given /24 subnet. Parameter default is set to True. Use -b False to begin IP enumeration
  -a --address: Victim address to spoof ***
  -r --router: Router address to spoof ***
  -t --time: Length of time (in minutes) for the attack to persist for *** 
  Use -h or --help for all available and/or required flags

Required packages
scapy.all
  - pip3 install scapy-python3
  - More information on installing scapy can be found at https://scapy.readthedocs.io/en/latest/installation.html
  
Future improvements planned
  - Known bugs exist when exiting the script from terminal using CTRL + C
  - IP enumeration function only enumerates /24 subnets. Enhanced subnet functionality is planned for v1.1
  - Graphical user interface (GUI) is planned for v2.0
  
  
  Attacks should be tested within your own environment to ensure the ARP table of your target is properly poisoned.
