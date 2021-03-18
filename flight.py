from dataclasses import dataclass

@dataclass
class Flight:
    flight_number : int
    tail_number: str
    airline : str
    origin_airport : str
    destination_airport : str
    date : str
    departure_time : str
    distance : int