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
        return_switches = {}
    
        show_system = net_connect.send_command('show system').split("\n")
        for system_line in show_system:
            if len(system_line) <= 1:
                continue
            elif "Name" in system_line.split()[1]:
                Hostname = system_line.split()[3]
        return_switches["Hostname"] = Hostname
        neighbor_list = net_connect.send_command('sh lldp info remote-device').split("\n")
        for neighbor in neighbor_list:
            if len(neighbor) <= 1:
                continue
            elif neighbor.split()[0] == "LLDP":
                continue
            elif neighbor.split()[0] == "LocalPort":
                continue
            elif neighbor.split()[0] == "---------":
                continue
            else:
                LocalPort = neighbor.split()[0]
                neighbor_detail_command = 'sh lldp info remote-device ' + LocalPort
                neighbor_detail = net_connect.send_command(neighbor_detail_command).split("\n")
                if "Switch" in neighbor_detail[9]:
                    try:
                        SysName = str(neighbor.split()[10])
                    except IndexError:
                        SysName = ""
                    try:
                        RemotePort = neighbor.split()[8]
                    except IndexError:
                        RemotePort = ""
                    for neighbor_info in neighbor_detail:
                        if len(neighbor_info) <= 1:
                            continue
                        elif "Address" in neighbor_info.split()[0]:
                            Address = neighbor_info.split()[2]
                    if SysName in switch_origin:
                        continue
                    else:
                        print Hostname + ":" + SysName + ":" + LocalPort + ":" + RemotePort + ":" + Address
                    getLLDPneighbors(Address,Hostname)
        net_connect.disconnect()
    except (NetMikoTimeoutException, NetMikoAuthenticationException):
        print switch_ip + ':no_response'

switches = csv.DictReader(open("switches.csv"))

print "Local Switch:Remote Switch:Local Port:Remote Port:Address"
for row in switches:
    getLLDPneighbors(row['IP'],"")