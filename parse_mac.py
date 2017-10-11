#!/usr/bin/python
# parse_mac.py
# Rich Bocchinfuso
# 2017/10/10

import re

mac_input = 'mac_table_alt.input'
mac_output = 'mac_parsed.txt'
mac_pattern = '([a-fA-F0-9]{4}[.:|\-]?){3}'
mac_addresses = []

with open(mac_input, 'r') as f:
  lines = f.readlines()

for line in lines:

    match = re.search(mac_pattern,line)
    if match:
        parsed_mac = match.group() + '\n'
        print (parsed_mac)
        mac_addresses.append(parsed_mac)

with open (mac_output,'w') as f:
    f.seek(0)
    f.writelines (mac_addresses)

