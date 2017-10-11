import csv
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException,NetMikoAuthenticationException

# these are just simple python formatted files with variables in them
from credentials import *

def getLLDPneighbors(switch_ip,switch_origin):
    switch = {
        'device_type': 'hp_procurve',
        'ip': switch_ip,
        'username': username,
        'password': password,
        'port' : 22,          # optional, defaults to 22
        'secret': secret,     # optional, defaults to ''
        'verbose': False,       # optional, defaults to False
    }
    
    try:# if the switch is reponsive we do our thing, otherwise we hit the exeption below
        # this actually logs into the device
        net_connect = ConnectHandler(**switch)
        
        # I wanted to be sure of the hostname of the switch I'm on
        show_system = net_connect.send_command('show system').split("\n")
        for system_line in show_system:
            if len(system_line) <= 1:
                continue
            elif "Name" in system_line.split()[1]:
                Hostname = system_line.split()[3]
        
        # get a quick list of LLDP neighborships
        neighbor_list = net_connect.send_command('sh lldp info remote-device').split("\n")
        for neighbor in neighbor_list:
            # skip the leading structure
            if len(neighbor) <= 1:
                continue
            elif neighbor.split()[0] == "LLDP":
                continue
            elif neighbor.split()[0] == "LocalPort":
                continue
            elif neighbor.split()[0] == "---------":
                continue
            else: # finally this is what we're looking for, the neighbors
                # the local interface is the first column, I hope
                LocalPort = neighbor.split()[0]
                
                # using that I can get more detailed info on each neighbor
                neighbor_detail_command = 'sh lldp info remote-device ' + LocalPort
                neighbor_detail = net_connect.send_command(neighbor_detail_command).split("\n")
                if "Switch" in neighbor_detail[9]:  # if the neighbor is a switch then I'm interested
                    
                    # I had to build in exceptions to deal with weird formatting situations
                    try:
                        SysName = str(neighbor.split()[10])
                    except IndexError:
                        # basically if the formatting sucks, we just give up but don't crash the script
                        SysName = ""
                    try:
                        RemotePort = neighbor.split()[8]
                    except IndexError:
                        RemotePort = ""
                        # basically if the formatting sucks, we just give up but don't crash the script
                    for neighbor_info in neighbor_detail:
                        if len(neighbor_info) <= 1:
                            continue
                        elif "Address" in neighbor_info.split()[0]: # this approach is a bit better
                                                                    # if a line has the word Address in it
                                                                    # then we assume it is the IP
                            Address = neighbor_info.split()[2]
                    if SysName in switch_origin:    # if the switch we see on LDP is where we came from, ignore it
                        continue
                    else:   # otherwise print our nugget of information!
                        print Hostname + ":" + SysName + ":" + LocalPort + ":" + RemotePort + ":" + Address
                    
                    # if we've found a new switch that we didn't know about, try to connect and grab more info from it
                    getLLDPneighbors(Address,Hostname)
        
        # we always sanely disconnect
        net_connect.disconnect()
    except (NetMikoTimeoutException, NetMikoAuthenticationException):
        print switch_ip + ':no_response'

switches = csv.DictReader(open("switches.csv"))

print "Local Switch:Remote Switch:Local Port:Remote Port:Address"
for row in switches:
    getLLDPneighbors(row['IP'],"")