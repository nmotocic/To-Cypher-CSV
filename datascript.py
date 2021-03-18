import csv, itertools
from Airport import Airport
from flight import Flight
from airline import Airline
from pathlib import Path
import random

airports = []
airlines = []
flights = []

_here = Path(__file__).parent

def extractAirports(airportPath):
    #extract airports from airports.csv
    with open(airportPath, 'r', newline = '') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            airport = Airport(iata_code = row["IATA_CODE"], name = row["AIRPORT"], 
                             city = row["CITY"], state = row["STATE"], lat = row["LATITUDE"], 
                             lon = row["LONGITUDE"])
            airports.append(airport)

def extractAirlines(airlinePath):
    #extract airlines from airlines.csv
    with open(airlinePath, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            airline = Airline(iata_code = row["IATA_CODE"], name = row["AIRLINE"])
            airlines.append(airline)

def extractFlights(flightsPath):
    #extract flights from flight.csv
    with open(flightsPath, 'r', newline = "") as f:
        #reader = csv.DictReader(f, delimiter=',')
        
        for row in itertools.islice(csv.DictReader(f), 5000):
            date =  row["MONTH"] + "/" + row["DAY"] + "/" + row["YEAR"]
            departure_time = departureTimeFix(row["DEPARTURE_TIME"])
            flight = Flight(flight_number = row["FLIGHT_NUMBER"], tail_number = row["TAIL_NUMBER"],
                            airline = row["AIRLINE"], origin_airport = row["ORIGIN_AIRPORT"], destination_airport = row["DESTINATION_AIRPORT"],
                            date = date, departure_time = departure_time, distance = row["DISTANCE"])
            flights.append(flight)

def generateQueries(queriesPath):
    #generate airport queries
    with open(queriesPath, 'w', newline = "") as f:
        for airport in airports:
            f.write(f'CREATE (a: Airport {{iata_code:"{airport.iata_code}", name:"{airport.name}", city:"{airport.city}", state:"{airport.state}"}});')
            f.write("\n")
        for flight in flights:
            f.write(f"MATCH (origin: Airport),(dest:Airport) WHERE origin.iata_code = '{flight.origin_airport}' AND dest.iata_code = '{flight.destination_airport}' CREATE (origin)-[:HAS_FLIGHT {{ flight_number:{flight.flight_number}, airline:'{flight.airline}', date:'{flight.date}', departure_time:'{flight.departure_time}', distance:{flight.distance} }}]->(dest);"  )
            f.write("\n")

def generateNodes(nodesPath):
    #csv file for nodes
    with open(nodesPath, 'w', newline= "" ) as f:
        fieldnames = ['iata_code:string', 'name:string', "city:string", "state:string", ":LABEL"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for airport in airports:
            writer.writerow({
                            'iata_code:string': airport.iata_code,
                            'name:string': airport.name,
                            'city:string': airport.city,
                            'state:string' : airport.state,
                            ":LABEL" : "Airport"})
            

def generateRelationships(relationshipPath):
    #csv file for relationships
    with open(relationshipPath, 'w', newline='') as f:
        fieldnames = [':START_ID(iata_code)', ':END_ID(iata_code)', ':TYPE', "flight_number:int", "airline:string", "date:string", "departure_time:string",  "distance:int"]  
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for flight in flights:
            
            writer.writerow({ ":START_ID(iata_code)" : flight.origin_airport,
                            ":END_ID(iata_code)" : flight.destination_airport ,
                            ":TYPE" : "IS_FLYING_TO",
                            "flight_number:int" : flight.flight_number, 
                            "airline:string" : flight.airline,
                            "date:string" : flight.date,
                            "departure_time:string": flight.departure_time, 
                            "distance:int" : flight.distance })


def departureTimeFix(time):
    if len(time) == 4:
        return time[0:2] + ":" + time[2:4]
    elif len(time) == 3:
        return "0" + time[0] + ":" + time[1:3]
    elif len(time) == 2:
        return "00" + ":" + time
    elif len(time) == 1:
        return "00" + ":" + "0" + time

if __name__ == "__main__":
    airportPath = _here.joinpath("Datasets\\airports.csv")
    flightPath = _here.joinpath("Datasets\\flights.csv")
    queriesPath = _here.joinpath("Queries\\queries.txt")
    importQueriesPath = _here.joinpath("Queries\\queries.cypherl")
    nodesPath = _here.joinpath("Queries\\nodes.csv")
    relationshipPath = _here.joinpath("Queries\\relationship.csv")

    extractAirports(airportPath)
    extractFlights(flightPath)
    generateQueries(queriesPath)
    generateQueries(importQueriesPath)
    generateNodes(nodesPath)
    generateRelationships(relationshipPath)
    print("success")
