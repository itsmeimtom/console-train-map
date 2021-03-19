import requests 
from requests.auth import HTTPBasicAuth 
from datetime import date
import json

from creds import *

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
    firstService = True
    for service in services['services']:
        dest = service['locationDetail']['destination'][0]['description']
        serviceListing += "%s - %s to %s (%s)\n"%(service['serviceUid'], service['locationDetail']['gbttBookedDeparture'], dest, service['atocName'])
        firstService = False

    print(serviceListing)


def trainInfoLoop(uid):
    dateString = date.today().strftime("%Y/%m/%d")
    service = rttReq("service/%s/%s"%(uid,dateString))

    print("RTT UID %s - %s"%(service['serviceUid'],service['runDate']))
    print("%s %s to %s"%(service['origin'][0]['publicTime'],service['origin'][0]['description'],service['destination'][0]['description']))
    print("%s %s"%(service['trainIdentity'],service['atocName']))

    stations = []

    for location in service['locations']:
        # print(location)

        # if('gbttBookedDeparture' in location):
        #     departureTime = location['gbttBookedDeparture']
        # else:
        #     departureTime = 'WHAT'
        
        # if('realtimeDepartureActual' in location):
        #     latenessString = "OT"
        #     if 'realtimeWttDepartureLateness' in location:
        #         latenessMins = location['realtimeWttDepartureLateness']
        #         if latenessMins > 0:
        #             latenessString = "%sm late"%latenessMins
        #         elif latenessMins < 0:
        #             latenessString = "%sm erly"%latenessMins*-1

        #     departureTime = "dept %s"%latenessString
        
        stationString = "%s"%(location['description'])

        if location['isCall']:
            stations.append(stationString)

    print(giveUsAMap(stations))


def giveUsAMap(stations, trainLocation="", trainDetails=""):
    spaces = 3
    offset = " "*spaces

    output = ""
    totalStations = len(stations)

    for line in range(totalStations):
        # /A           LINE ZERO
        # |   /B       LINE  ONE
        output += ("|%s"%offset)*line
        output += "/%s\n"%stations[line].strip()

    for charset in range(totalStations):
        track = ""
        if charset == totalStations-1:
            track = "="*len(stations[totalStations-1])
        else:
            track = "="*spaces

        if charset == 0:
            output += "O%s"%track
        elif charset == totalStations-1:
            output += "D%s"%track
        else:
            output += "^%s"%track

    return output

# renderMap(["Shrewsbury","Telford Central","Wolverhampton","Smethwick Galton B","Bham New Street"])


showServices(input('between > '), input('    and > '))
trainInfoLoop(input('enter train uid > '))