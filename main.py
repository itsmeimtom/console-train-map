import requests 
from requests.auth import HTTPBasicAuth 
from datetime import date
import time
import json
import os

from creds import *

spaces = 1
timeout = 20

colourHighlight = "\033[1;36;40m" # cyan
colourPassed = "\033[1;30;40m" # dark grey
#colourPassed = "\033[1;31;40m" # bright red
colourFuture = "\033[1;37;40m" # white
colourBold = "\033[1m"
colourReset = "\033[0m"

def rttReq(endpoint):
    url = "https://api.rtt.io/api/v1/json/%s"%endpoint
    rtt = requests.get(url, 
        auth = HTTPBasicAuth(rttUser, rttPass))

    return json.loads(rtt.text)


def showServices(fromStation, toStation):
    dateString = date.today().strftime("%Y/%m/%d")
    services = rttReq("search/%s/to/%s/%s"%(fromStation.upper(),toStation.upper(),dateString))
    
    print("Today's departures between %s and %s"%(services['location']['name'],services['filter']['destination']['name']))

    serviceListing = ""
    for service in services['services']:
        dest = service['locationDetail']['destination'][0]['description']
        serviceListing += "%s - %s to %s (%s)\n"%(service['serviceUid'], service['locationDetail']['gbttBookedDeparture'], dest, service['atocName'])

    print(serviceListing)


def trainInfoLoop(uid):
    clear = os.system('clear')
    
    dateString = date.today().strftime("%Y/%m/%d")
    service = rttReq("service/%s/%s"%(uid,dateString))

    print("\033[1;31;40mRTT UID %s - %s"%(service['serviceUid'],service['runDate']))
    print("\033[1;35;40m%s %s to %s"%(service['origin'][0]['publicTime'],service['origin'][0]['description'],service['destination'][0]['description']))
    print("%s %s"%(service['trainIdentity'],service['atocName']))

    stations = []
    passedNum = 0
    currentStation = None

    for location in service['locations']:
        if not location['isCall']:
            continue

        deptTime = ""
        if 'realtimeDepartureActual' in location:
            if location['realtimeDepartureActual'] == True:
                # the the train has departed the station and we can use the realtime data
                deptTime = "left %s"%location['realtimeDeparture']
                passedNum = passedNum + 1
            else:
                # we can use RTT's realtime guestimate if the train is early or late
                deptTime = "departing %s"%location['realtimeDeparture']
        elif 'gbttBookedDeparture' in location:
            # otherwise we can fallback to the timetabled time
            deptTime = "tt'd dept %s"%location['gbttBookedDeparture']

        arrTime = ""
        if 'realtimeArrivalActual' in location:
            if location['realtimeArrivalActual'] == True:
                # the the train has arrived the station and we can use the realtime data
                arrTime = "arrived %s"%location['realtimeArrival']
                currentStation = passedNum
            else:
                # we can use RTT's realtime guestimate if the train is early or late
                arrTime = "arriving %s"%location['realtimeArrival']
        elif 'gbttBookedArrival' in location:
            # otherwise we can fallback to the timetabled time
            arrTime = "tt'd arrival %s"%location['gbttBookedArrival']
        
        times = "%s %s"%(arrTime, deptTime)
        
        status = ""
        if 'serviceLocation' in location:
            status = "%s - "%location['serviceLocation']
            status = status.replace('APPR_STAT', 'Approaching Station').replace('APPR_PLAT', 'Approaching Platform').replace('AT_PLAT', 'At Platform').replace('DEP_PREP', 'Preparing to Depart').replace('DEP_READY', 'Ready to Depart')
            currentStation = passedNum

        stationString = "%s (%s%s)"%(location['description'],status,times.strip())
        stations.append(stationString)

    print(giveUsAMap(stations, passedNum, currentStation))

    time.sleep(timeout)
    trainInfoLoop(uid)

        
def giveUsAMap(stations, stationsPassed, stationToHL):
    output = ""
    totalStations = len(stations)

    for line in range(totalStations):
        output += "\n"

        # do poles        
        for pole in range(line):
            colour = colourPassed
            if pole == stationToHL:
                colour = colourHighlight
            elif pole >= stationsPassed:
                colour = colourFuture
            # output += "%s|%s"%(colour," "*spaces)
            output += "%s"%(" "*spaces)

        # do current station name
        if line == stationToHL:
            colour = colourHighlight
        elif line < stationsPassed:
            colour = colourPassed
        else:
            colour = colourFuture

        # output += "%s/%s"%(colour,stations[line].strip())
        output += "%s\\ %s%s"%(colour,stations[line].strip(),colour)

    return output

#showServices(input('between > '), input('    and > '))
#trainInfoLoop(input('enter train uid > '))

trainInfoLoop("C15302")