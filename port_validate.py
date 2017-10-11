#!/usb/bin/python
# port_validate.py
# Rich Bocchinfuso
# 2017/10/10

import paramiko
import time
import csv
import sys
import os

class textcolor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def disable_paging(remote_conn):
    '''Disable paging on a Cisco router'''

    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

if __name__ == '__main__':

    switch_file = 'switch_list.csv'
    port_log = 'port_log.csv'
    exception_log = 'exception_log.csv'

    validate = open(port_log, 'w')
    validate.write('site_id,switch_ip,port,status\n')
    validate.close()

    exception = open(exception_log, 'w')
    exception.write('site_id,switch_ip,port,status\n')
    exception.close()

    sw = open(switch_file, 'r')  # open file
    try:
        r = csv.reader(sw)   # init csv reader
        for row in r:
            site_id = row[0]
            switch_ip = row[1]
            user = row[2]
            userpwd = row[3]
            enablepwd = row[4]
            port1 = row[5]
            port2 = row[6]
            port3 = row[7]

            # create instance of SSHClient object
            remote_conn_pre = paramiko.SSHClient()

            # automatically add untrusted hosts (make sure okay for security policy in your environment)
            remote_conn_pre.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())

            # initiate SSH connection
            remote_conn_pre.connect(switch_ip, username=user, password=userpwd, look_for_keys=False, allow_agent=False)
            print (textcolor.OKBLUE + "SSH connection established to %s" % switch_ip + textcolor.ENDC)

            # use invoke_shell to establish an 'interactive session'
            remote_conn = remote_conn_pre.invoke_shell()
            print (textcolor.OKBLUE + "Interactive SSH session established" + textcolor.ENDC)

            # strip the initial switch/router prompt
            output = remote_conn.recv(1000)
            
            # print (output)    # debug

            # turn off paging
            disable_paging(remote_conn)

            # send commands
            remote_conn.send("\n")
            remote_conn.send("show int status | i " + port1 + "|" + port2 + "|" + port3 + "\n")

            # wait for the commands to complete
            time.sleep(2)
            
            output = remote_conn.recv(5000).decode(encoding='utf-8')
            # print (output)    # debug
            tmp = open('tmp', 'w')
            tmp.write(output)
            tmp.close()
            
            # parse output and create validation file
            tmp = open('tmp', 'r')
            for row in tmp:
                if row.startswith("Fa"):
                    port_list = row.split()
                    # print (port_list)   # debug
                    validate = open(port_log, 'a')
                    validate.write (site_id + ',' + switch_ip + ',' + port_list[0] + ',' + port_list[1] + '\n')
                    validate.close()
                    if port_list[1] == 'connected':
                        print (textcolor.FAIL + 'WARNING: ' + port_list[0] + ' on switch ' + switch_ip + ' is ' + port_list[1] + textcolor.ENDC)
                        exception = open(exception_log, 'a')
                        exception.write (site_id + ',' + switch_ip + ',' + port_list[0] + ',' + port_list[1] + '\n')
                        exception.close()
            tmp.close()
            os.remove('tmp')
            

    finally:
        sw.close() #cleanup
        print (textcolor.ENDC + "Done")