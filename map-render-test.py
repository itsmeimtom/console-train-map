spaces = 3

stationsInput = input('Enter stations, seperated by a comma > ')
stations = stationsInput.upper().split(',')

offset = ""
for _ in range(spaces):
    offset += " "


i = 0
totalStations = len(stations)

output = ""
for line in range(totalStations):
    # /-A           LINE ZERO
    # |   /-B       LINE  ONE

    output += ("|%s"%offset)*i
    output += "/-%s\n"%stations[line]
    i = i+1


for charset in range(totalStations):
    track = "="*spaces

    if charset == totalStations-1:
        track += "="*len(stations[totalStations-1])

    if charset == 0:
        output += "D%s"%track
    else:
        output += "s%s"%track

print(output)

print("\033[0m")