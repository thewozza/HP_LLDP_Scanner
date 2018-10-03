import subprocess, platform
import sys
from datetime import datetime, timedelta
import csv
import datetime
import socket

def check_ping(hostname):

    try:
        response  = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', hostname), shell=True)
    
    except Exception, e:
        return False
    return True

def iPerfTestActual(hostname,direction):

    dataIsNext = False
    if direction == "reverse":
        direction = "-R"
    else:
        direction = ""
    try:
        iperfOutput = subprocess.check_output("iperf3 -P 5 -c " + remote + " " + direction + " -i 0 -t " + str(testTime), shell=True).split("\n")
        time.sleep(1)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    for line in iperfOutput:
            results = line.split()
            if results[0] == "[SUM]":
                return results[5], results[6]
                break   

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

remote = sys.argv[1]

testTime = 10
totalDuration = int(sys.argv[2])
period = timedelta(minutes=totalDuration)
next_time = datetime.datetime.now() + period

local = get_ip()

if check_ping(remote):
    currentDate = str((datetime.datetime.date(datetime.datetime.now()))) + "." + str(datetime.datetime.time(datetime.datetime.now())).split(".")[0]
    
    database = {}
    
    keepLooping = True
    startTime = str(datetime.datetime.time(datetime.datetime.now()))
    
    while keepLooping:

        currentTime = str(datetime.datetime.time(datetime.datetime.now())).split(".")[0]
        database[currentTime] = {}
        
        (database[currentTime]["forwardSpeed"],database[currentTime]["forwardRate"]) = iPerfTestActual(remote, "forward")
        (database[currentTime]["reverseSpeed"],database[currentTime]["reverseRate"]) = iPerfTestActual(remote, "reverse")
        
        if next_time <= datetime.datetime.now():
            break

    with open("/home/paul/" + currentDate + ".csv", "wb") as csvfile:
        csvoutput = csv.writer(csvfile, delimiter=',')
        csvoutput.writerow(["local","remote","time","forwardSpeed","forwardRate","reverseSpeed","reverseRate"])
        for timeLoop, dictLoop in database.items():
            csvoutput.writerow([local,remote,timeLoop,dictLoop["forwardSpeed"],dictLoop["forwardRate"],dictLoop["reverseSpeed"],dictLoop["reverseRate"]])
    
else:
    print "Not pingable, exiting"