import requests,time,json,os,re,sys
from requests.auth import HTTPBasicAuth 
from datetime import date

from creds import *

#################################################################

spaces = 1
loopTime = 20
usePoles = False

colourHighlight = "\033[1;36;40m" # cyan
colourPassed = "\033[1;30;40m" # dark grey
#colourPassed = "\033[1;31;40m" # bright red
colourFuture = "\033[1;37;40m" # white
colourTitle1 = "\033[1;31;40m" # bright red
colourTitle2 = "\033[1;35;40m" # magenta
colourReset = "\033[0;37;40m"

#################################################################

def clearScreen():
    if os.name == 'nt': 
        os.system('cls')
    else:
        os.system('clear')

#################################################################

def throwErr(Err):
    clearScreen()
    print(f"\n/!\\ Error! {Err}\n")
    return sys.exit()

#################################################################

def rttReq(endpoint):
    url = "https://api.rtt.io/api/v1/json/%s"%endpoint
    rtt = requests.get(url, 
        auth = HTTPBasicAuth(rttUser, rttPass))
    
    if '<h1>Not Found</h1>' in rtt.text:
        throwErr(f"Computer said no, '{rtt.text}'")
    elif rtt.status_code != 200:
        throwErr(rtt.text)

    return json.loads(rtt.text)

#################################################################

def showServices(fromStation, toStation):
    dateString = date.today().strftime("%Y/%m/%d")
    services = rttReq("search/%s/to/%s/%s"%(fromStation.upper(),toStation.upper(),dateString))

    if not 'location' in services or not 'filter' in services:
        print("\n/!\\ one or both of those station codes didn't seem right, try again?\n")
        return menu_askForStations()

    clearScreen()
    print("\nToday's departures between %s and %s:"%(services['location']['name'],services['filter']['destination']['name']))

    if not services['services']:
        print("\n/!\\ there are no services between these stations, please try again:\n")
        return menu_askForStations()

    print("  UID  | Dept |  Dest (Operator)")

    serviceListing = ""
    for service in services['services']:
        dest = service['locationDetail']['destination'][0]['description']
        serviceListing += "%s - %s to %s (%s)\n"%(service['serviceUid'], service['locationDetail']['gbttBookedDeparture'], dest, service['atocName'])

    print(serviceListing)

#################################################################

def trainInfoLoop(uid):
    clearScreen()

    dateString = date.today().strftime("%Y/%m/%d")
    service = rttReq("service/%s/%s"%(uid.upper(),dateString))
    vehicleInfo = parseVehInfo(service)

    print("%sUID %s on %s"%(colourTitle1, service['serviceUid'],service['runDate']))
    print("%s%s %s to %s"%(colourTitle2, service['origin'][0]['publicTime'],service['origin'][0]['description'],service['destination'][0]['description']))
    print("%s%s"%(colourTitle2, service['atocName']))
    print("%s%s"%(colourTitle1, vehicleInfo))



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
                deptTime = "departed %s"%location['realtimeDeparture']
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

        timesSep = ""
        if len(arrTime) > 0 and len(deptTime) > 0:
            timesSep = ", "

        times = "%s%s%s"%(arrTime, timesSep, deptTime)
        
        status = ""
        if 'serviceLocation' in location:
            status = "%s - "%location['serviceLocation']
            status = status.replace("APPR_STAT", "Approaching Station").replace("APPR_PLAT", "Approaching Platform").replace("AT_PLAT", "At Platform").replace("DEP_PREP", "Preparing to Depart").replace("DEP_READY", "Ready to Depart")
            currentStation = passedNum

        stationString = "%s (%s%s)"%(location['description'],status.upper(),times.strip())
        stations.append(stationString)

    print(giveUsAMap(stations, passedNum, currentStation))

    time.sleep(loopTime)
    trainInfoLoop(uid)

#################################################################
        
def giveUsAMap(stations, stationsPassed, stationToHL):
    output = ""
    totalStations = len(stations)

    for line in range(totalStations):
        output += "\n"

        for pole in range(line):
            if usePoles == True:
                colour = colourPassed
                if pole == stationToHL:
                    colour = colourHighlight
                elif pole >= stationsPassed:
                    colour = colourFuture
                output += "%s|%s"%(colour," "*spaces)
            else:
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

#################################################################

def parseVehInfo(service):
    output = service['serviceType'].upper()

    output += " ("
    if 'trainClass' in service:
        output += service['trainClass']
    else:
        output += "Characteristics Unknown"

    if 'powerType' in service:
        output += " %s"%service['powerType']
    else:
        output += " Power Unknown"

    output += ")"

    if 'trainIdentity' in service:
        output += " running to %s"%service['trainIdentity']

    return output

#################################################################

def menu_askForStations():
    print("let's find you a service! which stations should we look for trains between?")
    print("enter 3-digit crs codes, you can find these at nationalrail.co.uk")
    inputFrom = input("from > ")
    inputTo = input("  to > ")

    if not re.search("[a-zA-Z]{3}", inputFrom):
        print("that does not look like a valid from station code, perhaps try again?")
        return menu_askForStations()
    if not re.search("[a-zA-Z]{3}", inputTo):
        print("that does not look like a valid to station code, perhaps try again?")
        return menu_askForStations()
    
    showServices(inputFrom, inputTo)
    menu_askForUID()
    
#################################################################

def menu_askForUID(firstUid=None):
    if firstUid:
        inputUid = firstUid
    else:
        inputUid = input("enter train uid > ")

    if not re.search("[A-Za-z][0-9]{5}", inputUid):
        print("are you sure that's a valid uid? give it another go!")
        return menu_askForUID()
    else:
        trainInfoLoop(inputUid)


#################################################################

try:
    print ("\033[1;36;40m                TomR.me - ConsoleTrainMap                ")
    print("\033[1;33;40m/===   press ↵enter to start searching for a train   ===\\")
    print("\033[1;33;40mif you already know the uid of train, type it and press ↵")

    menu = input()

    if len(menu) < 1:
        menu_askForStations()
    else:
        menu_askForUID(menu)
except KeyboardInterrupt:
    print(colourReset)
    sys.exit()

