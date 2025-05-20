#
# Name: Shriraj Patel
# Overview: This is a python program that allows a user to input commands to fetch certain pieces of information from
# the CTA2 L daily ridership database. Internally, it uses SQL queries to return this data as well as matplotlib to plot
# that data when using specific commands.
#

import sqlite3
import matplotlib.pyplot as plt

#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General statistics:")

    # Station count
    dbCursor.execute("""
                    SELECT count(*) 
                    FROM Stations;
                    """)

    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    # Stop count
    dbCursor.execute("""
                    SELECT count(*) 
                    FROM Stops;
                    """)

    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    # Ride entry count
    dbCursor.execute("""
                    SELECT count(*)
                    FROM Ridership;
                    """)

    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    # Date range
    dbCursor.execute("""
                    SELECT date(Ride_Date) 
                    FROM Ridership 
                    ORDER BY date(Ride_Date) LIMIT 1
                    """)

    row = dbCursor.fetchone()

    dbCursor.execute("""
                    SELECT date(Ride_Date)
                    FROM Ridership 
                    ORDER BY date(Ride_Date) DESC LIMIT 1
                    """)

    row2 = dbCursor.fetchone()
    print("  date range:", row[0], "-", row2[0])

    # Total ridership
    dbCursor.execute("""
                    SELECT sum(Num_Riders)
                    FROM Ridership;
                    """)

    row = dbCursor.fetchone()
    print("  Total ridership:", f"{row[0]:,}")

#
# commandOne
#
# Takes input from the user and then uses an SQL query to return all the station IDs and names that match the provided
# input.
#
def commandOne(dbConn):
    dbCursor = dbConn.cursor()
    commandOneInput = input("Enter partial station name (wildcards _ and %):")

    dbCursor.execute("""
                    SELECT Station_ID, Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}" 
                    ORDER BY Station_Name;
                    """.format(commandOneInput))

    result = dbCursor.fetchone()

    if result is None:
        print("**No stations found...")
        return

    while True:
        print(result[0], ":", result[1])
        result = dbCursor.fetchone()

        if result is None:
            return

#
# commandTwo
#
# Takes in a station name provided by the user and then outputs the weekday, saturday, sunday/holiday, and total
# ridership and percentages at that station.
#
def commandTwo(dbConn):
    dbCursor = dbConn.cursor()
    commandTwoInput = input("Enter the name of the station you would like to analyze:")

    dbCursor.execute("""
                    SELECT sum(Num_Riders) 
                    FROM Ridership 
                    JOIN Stations 
                    ON Ridership.Station_ID = Stations.Station_ID 
                    WHERE Station_Name = "{}" AND Type_of_Day = 'W';
                    """.format(commandTwoInput))

    result = dbCursor.fetchone()

    if result[0] is None:
        print("**No data found...")
        return

    weekdayRiders = result[0]

    dbCursor.execute("""
                    SELECT sum(Num_Riders) 
                    FROM Ridership 
                    JOIN Stations 
                    ON Ridership.Station_ID = Stations.Station_ID 
                    WHERE Station_Name = "{}" AND Type_of_Day = 'A';
                    """.format(commandTwoInput))

    result = dbCursor.fetchone()

    if result is None:
        saturdayRiders = 0
    else:
        saturdayRiders = result[0]

    dbCursor.execute("""
                    SELECT sum(Num_Riders) 
                    FROM Ridership 
                    JOIN Stations 
                    ON Ridership.Station_ID = Stations.Station_ID 
                    WHERE Station_Name = "{}" AND Type_of_Day = 'U';
                    """.format(commandTwoInput))

    result = dbCursor.fetchone()

    if result is None:
        sundayRiders = 0
    else:
        sundayRiders = result[0]

    totalRiders = weekdayRiders + saturdayRiders + sundayRiders
    weekdayPercentage = (weekdayRiders / totalRiders) * 100
    saturdayPercentage = (saturdayRiders / totalRiders) * 100
    sundayPercentage = (sundayRiders / totalRiders) * 100

    print("Percentage of ridership for the {} station:".format(commandTwoInput))
    print("  Weekday ridership:", f"{weekdayRiders:,}", f"({weekdayPercentage:.2f}%)")
    print("  Saturday ridership:", f"{saturdayRiders:,}", f"({saturdayPercentage:.2f}%)")
    print("  Sunday/holiday ridership:", f"{sundayRiders:,}", f"({sundayPercentage:.2f}%)")
    print("  Total ridership:", f"{totalRiders:,}")

#
# commandThree
#
# Outputs the total ridership and percentages of every station on weekdays in descending order by ridership.
#
def commandThree(dbConn):
    dbCursor = dbConn.cursor()
    print("Ridership on Weekdays for Each Station")

    dbCursor.execute("""
                    SELECT sum(Num_Riders) 
                    FROM Ridership 
                    JOIN Stations 
                    ON Ridership.Station_ID = Stations.Station_ID 
                    WHERE Type_of_Day = 'W';
                    """)

    result = dbCursor.fetchone()
    totalWeekdayRidership = result[0]

    dbCursor.execute("""
                    SELECT Station_Name, sum(Num_Riders) 
                    FROM Ridership 
                    JOIN Stations 
                    ON Ridership.Station_ID = Stations.Station_ID 
                    WHERE Type_of_Day = 'W'
                    GROUP BY Station_Name 
                    ORDER BY sum(Num_Riders) DESC;
                    """)

    result = dbCursor.fetchone()

    while True:
        percentage = (result[1] / totalWeekdayRidership) * 100
        print(result[0], ":", f"{result[1]:,}", f"({percentage:.2f}%)")
        result = dbCursor.fetchone()

        if result is None:
            return

#
# commandFour
#
# Takes in a line color and direction as input from the user, and then outputs all the stops that are in the line color
# and go in the specified direction, as well as outputting whether it is handicap accessible.
#
def commandFour(dbConn):
    dbCursor = dbConn.cursor()
    lineColor = input("Enter a line color (e.g. Red or Yellow):")
    lineColor = lineColor.lower()

    if (lineColor != "red" and lineColor != "blue" and lineColor != "green" and lineColor != "brown" and
        lineColor != "purple" and lineColor != "purple-express" and lineColor != "yellow" and lineColor != "pink" and
        lineColor != "orange"):
        print("**No such line...")
        return

    lineColor = lineColor.capitalize()

    if lineColor == "Purple-express":
        lineColor = "Purple-Express"

    direction = input("Enter a direction (N/S/W/E):")
    direction = direction.upper()

    if direction != "N" and direction != "S" and direction != "W" and direction != "E":
        print("**That line does not run in the direction chosen...")
        return

    dbCursor.execute("""
                    SELECT Stop_Name, Direction, ADA 
                    FROM Stops 
                    JOIN StopDetails 
                    ON Stops.Stop_ID = StopDetails.Stop_ID 
                    JOIN Lines 
                    ON StopDetails.Line_ID = Lines.Line_ID 
                    WHERE Color = "{}" AND Direction = "{}" 
                    ORDER BY Stop_Name;
                    """.format(lineColor, direction))

    result = dbCursor.fetchone()

    if result is None:
        print("**That line does not run in the direction chosen...")
        return

    while True:
        if result[2] == 1:
            print(result[0], ": direction =", result[1], "(handicap accessible)")
        else:
            print(result[0], ": direction =", result[1], "(not handicap accessible)")

        result = dbCursor.fetchone()

        if result is None:
            return

#
# commandFive
#
# Outputs the number of stops of each line color and direction, both being grouped together. They are sorted in
# ascending order by color and then direction, and it also outputs the percentages relative to the total number of
# stops.
#
def commandFive(dbConn):
    dbCursor = dbConn.cursor()
    print("Number of Stops For Each Color By Direction")

    dbCursor.execute("""
                    SELECT Count(*) 
                    FROM Stops;
                    """)

    result = dbCursor.fetchone()
    totalStops = result[0]

    dbCursor.execute("""
                    SELECT Color, Direction, Count(*) 
                    FROM Stops 
                    JOIN StopDetails 
                    ON Stops.Stop_ID = StopDetails.Stop_ID 
                    JOIN Lines 
                    ON StopDetails.Line_ID = Lines.Line_ID 
                    GROUP BY Color, Direction 
                    ORDER BY Color, Direction;
                    """)

    result = dbCursor.fetchone()

    while True:
        percentage = (result[2] / totalStops) * 100
        print(result[0], "going", result[1], ":", result[2], f"({percentage:.2f}%)")

        result = dbCursor.fetchone()

        if result is None:
            return

#
# commandSix
#
# Takes in the user's input and if it matches exactly one station, the program will output the yearly ridership at that
# station. The user is also prompted to plot this data, and if they press 'y', a plot will be generated and shown to
# them.
#
def commandSix(dbConn):
    dbCursor = dbConn.cursor()
    commandSixInput = input("Enter a station name (wildcards _ and %):")

    dbCursor.execute("""
                    SELECT Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandSixInput))

    result = dbCursor.fetchall()

    if len(result) == 0:
        print("**No station found...")
        return
    elif len(result) > 1:
        print("**Multiple stations found...")
        return

    dbCursor.execute("""
                    SELECT Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandSixInput))

    result = dbCursor.fetchone()
    stationName = result[0]
    print("Yearly Ridership at", stationName)

    dbCursor.execute("""
                    SELECT strftime('%Y', Ride_Date) as Year, sum(Num_Riders) 
                    FROM Stations 
                    JOIN Ridership 
                    ON Stations.Station_ID = Ridership.Station_ID 
                    WHERE Station_Name = "{}"
                    GROUP BY Year;
                    """.format(stationName))

    result = dbCursor.fetchone()

    x = []
    y = []
    plt.xlabel("Year")
    plt.xticks(fontsize=6)
    plt.ylabel("Number of Riders")
    plt.title("Yearly Ridership at " + stationName + " Station")

    while True:
        print(result[0], ":", f"{result[1]:,}")
        x.append(result[0])
        y.append(result[1])
        result = dbCursor.fetchone()

        if result is None:
            break

    plotInput = input("Plot? (y/n)")
    plotInput = plotInput.lower()

    if plotInput == 'y':
        plt.ioff()
        plt.plot(x, y)
        plt.show()

#
# commandSeven
#
# Takes in the user's input for a station if it matches exactly one station, and also takes in the user's input for
# a year. The program then outputs the monthly ridership of that station on that given year, and also plots this data
# if the user says that they want a plot.
#
def commandSeven(dbConn):
    dbCursor = dbConn.cursor()
    commandSevenInput = input("Enter a station name (wildcards _ and %):")

    dbCursor.execute("""
                    SELECT Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandSevenInput))

    result = dbCursor.fetchall()

    if len(result) == 0:
        print("**No station found...")
        return
    elif len(result) > 1:
        print("**Multiple stations found...")
        return

    dbCursor.execute("""
                    SELECT Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandSevenInput))

    result = dbCursor.fetchone()
    stationName = result[0]
    year = input("Enter a year:")
    print("Monthly Ridership at " + stationName + " for " + year)

    dbCursor.execute("""
                    SELECT strftime('%m', Ride_Date) as Month, sum(Num_Riders) 
                    FROM Stations 
                    JOIN Ridership 
                    ON Stations.Station_ID = Ridership.Station_ID 
                    WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}" 
                    GROUP BY Month;
                    """.format(stationName, year))

    result = dbCursor.fetchone()

    x = []
    y = []
    plt.xlabel("Month")
    plt.ylabel("Number of Riders")
    plt.yticks(fontsize=8)
    plt.title("Monthly Ridership at " + stationName + " Station (" + year + ")")

    while True:
        print(result[0] + "/" + year + " : " + f"{result[1]:,}")
        x.append(result[0])
        y.append(result[1])
        result = dbCursor.fetchone()

        if result is None:
            break

    plotInput = input("Plot? (y/n)")
    plotInput = plotInput.lower()

    if plotInput == 'y':
        plt.ioff()
        plt.plot(x, y)
        plt.show()

#
# commandEight
#
# Takes in a user's input for a year, and then two station names that correspond to exactly one station. The program
# then outputs the ridership on that year for the first and last 5 days at each of those stations, and if the user wants
# a plot, the program will plot out the ridership for that entire year at both of the stations.
#
def commandEight(dbConn):
    dbCursor = dbConn.cursor()
    year = input("Year to compare against?")
    commandEightInput = input("Enter station 1 (wildcards _ and %):")

    dbCursor.execute("""
                    SELECT Station_ID, Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandEightInput))

    result = dbCursor.fetchall()

    if len(result) == 0:
        print("**No station found...")
        return
    elif len(result) > 1:
        print("**Multiple stations found...")
        return

    dbCursor.execute("""
                    SELECT Station_ID, Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandEightInput))

    result = dbCursor.fetchone()
    firstStationID = result[0]
    firstStationName = result[1]

    commandEightInput = input("Enter station 2 (wildcards _ and %):")

    dbCursor.execute("""
                    SELECT Station_ID, Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandEightInput))

    result = dbCursor.fetchall()

    if len(result) == 0:
        print("**No station found...")
        return
    elif len(result) > 1:
        print("**Multiple stations found...")
        return

    dbCursor.execute("""
                    SELECT Station_ID, Station_Name 
                    FROM Stations 
                    WHERE Station_Name LIKE "{}";
                    """.format(commandEightInput))

    result = dbCursor.fetchone()
    secondStationID = result[0]
    secondStationName = result[1]
    print("Station 1:", firstStationID, firstStationName)

    dbCursor.execute("""
                    SELECT date(Ride_Date), sum(Num_Riders)
                    FROM Stations 
                    JOIN Ridership 
                    ON Stations.Station_ID = Ridership.Station_ID 
                    WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                    GROUP BY date(Ride_Date) LIMIT 5;
                    """.format(firstStationName, year))

    result = dbCursor.fetchone()

    while True:
        print(result[0], result[1])
        result = dbCursor.fetchone()

        if result is None:
            break

    dbCursor.execute("""
                    SELECT date(Ride_Date), sum(Num_Riders) 
                    FROM Stations 
                    JOIN Ridership 
                    ON Stations.Station_ID = Ridership.Station_ID 
                    WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                    GROUP BY date(Ride_Date) 
                    ORDER BY date(Ride_Date) DESC LIMIT 5;
                    """.format(firstStationName, year))

    result = dbCursor.fetchone()
    stationOneLastFiveDays = []

    while True:
        output = result[0], result[1]
        stationOneLastFiveDays.append(output)
        result = dbCursor.fetchone()

        if result is None:
            break

    stationOneLastFiveDays.reverse()

    for row in stationOneLastFiveDays:
        print(row[0], row[1])

    print("Station 2:", secondStationID, secondStationName)

    dbCursor.execute("""
                        SELECT date(Ride_Date), sum(Num_Riders)
                        FROM Stations 
                        JOIN Ridership 
                        ON Stations.Station_ID = Ridership.Station_ID 
                        WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                        GROUP BY date(Ride_Date) LIMIT 5;
                        """.format(secondStationName, year))

    result = dbCursor.fetchone()

    while True:
        print(result[0], result[1])
        result = dbCursor.fetchone()

        if result is None:
            break

    dbCursor.execute("""
                        SELECT date(Ride_Date), sum(Num_Riders) 
                        FROM Stations 
                        JOIN Ridership 
                        ON Stations.Station_ID = Ridership.Station_ID 
                        WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                        GROUP BY date(Ride_Date) 
                        ORDER BY date(Ride_Date) DESC LIMIT 5;
                        """.format(secondStationName, year))

    result = dbCursor.fetchone()
    stationTwoLastFiveDays = []

    while True:
        output = result[0], result[1]
        stationTwoLastFiveDays.append(output)
        result = dbCursor.fetchone()

        if result is None:
            break

    stationTwoLastFiveDays.reverse()

    for row in stationTwoLastFiveDays:
        print(row[0], row[1])

    x = []
    y1 = []
    y2 = []
    day = 1
    plt.xlabel("Day")
    plt.ylabel("Number of Riders")
    plt.title("Ridership Each Day of " + year)

    dbCursor.execute("""
                        SELECT date(Ride_Date), sum(Num_Riders)
                        FROM Stations 
                        JOIN Ridership 
                        ON Stations.Station_ID = Ridership.Station_ID 
                        WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                        GROUP BY date(Ride_Date);
                        """.format(firstStationName, year))

    result = dbCursor.fetchone()

    while True:
        x.append(day)
        y1.append(result[1])
        day = day + 1
        result = dbCursor.fetchone()

        if result is None:
            break

    dbCursor.execute("""
                            SELECT date(Ride_Date), sum(Num_Riders)
                            FROM Stations 
                            JOIN Ridership 
                            ON Stations.Station_ID = Ridership.Station_ID 
                            WHERE Station_Name = "{}" AND strftime('%Y', Ride_Date) = "{}"
                            GROUP BY date(Ride_Date);
                            """.format(secondStationName, year))

    result = dbCursor.fetchone()

    while True:
        y2.append(result[1])
        result = dbCursor.fetchone()

        if result is None:
            break

    plotInput = input("Plot? (y/n)")
    plotInput = plotInput.lower()

    if plotInput == 'y':
        plt.ioff()
        plt.plot(x, y1, label=firstStationName)
        plt.plot(x, y2, label=secondStationName)
        plt.legend()
        plt.show()

#
# commandNine
#
# Takes in a latitude and longitude as input from the user, and then displays a list of all the stations that are
# within a one square mile radius of the provided latitude and longitude as well as displaying each station's location.
# The program also allows the user to plot the locations of these stations on a map of Chicago so that they can visually
# see where the stations are located.
#
def commandNine(dbConn):
    dbCursor = dbConn.cursor()
    latitude = input("Enter a latitude:")
    latitude = float(latitude)

    if latitude < 40 or latitude > 43:
        print("**Latitude entered is out of bounds...")
        return

    longitude = input("Enter a longitude:")
    longitude = float(longitude)

    if longitude < -88 or longitude > -87:
        print("**Longitude entered is out of bounds...")
        return

    northBoundary = round(latitude + (1 / 69), 3)
    southBoundary = round(latitude - (1 / 69), 3)
    eastBoundary = round(longitude + (1 / 51), 3)
    westBoundary = round(longitude - (1 / 51), 3)

    dbCursor.execute("""
                    SELECT Station_Name, Latitude, Longitude
                    FROM Stops
                    JOIN Stations
                    ON Stops.Station_ID = Stations.Station_ID
                    ORDER BY Station_Name;
                    """)

    result = dbCursor.fetchone()
    nearbyStations = []
    x = []
    y = []

    while True:
        if northBoundary > result[1] > southBoundary and eastBoundary > result[2] > westBoundary:
            print(result[0] + " : ({}, {})".format(result[1], result[2]))
            nearbyStations.append(result[0])
            x.append(result[2])
            y.append(result[1])

        result = dbCursor.fetchone()
        result = dbCursor.fetchone()

        if result is None:
            break

    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # area covered by the map:
    plt.imshow(image, extent=xydims)
    plt.title("Stations Near You")
    plt.plot(x, y, 'o')

    for i in range(len(nearbyStations)):
        plt.annotate(nearbyStations[i], (x[i], y[i]))

    plotInput = input("Plot? (y/n)")
    plotInput = plotInput.lower()

    if plotInput == 'y':
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()

#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')
print_stats(dbConn)

while True:
    userInput = input("Please enter a command (1-9, x to exit):")

    match userInput:
        case 'x':
            exit(0)

        case '1':
            commandOne(dbConn)

        case '2':
            commandTwo(dbConn)

        case '3':
            commandThree(dbConn)

        case '4':
            commandFour(dbConn)

        case '5':
            commandFive(dbConn)

        case '6':
            commandSix(dbConn)

        case '7':
            commandSeven(dbConn)

        case '8':
            commandEight(dbConn)

        case '9':
            commandNine(dbConn)

        case _:
            print("**Error, unknown command, try again... ")

#
# done
#
