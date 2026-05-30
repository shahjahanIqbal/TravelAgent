"""
Tools for the AI Travel Planning Agent.

Each tool wraps a specific data source or API and is registered
as a LangChain tool so the agent can call it autonomously.
"""

import json
import requests
from datetime import datetime, timedelta
from langchain.tools import tool


DATA_DIR = "data"

CITY_COORDINATES = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Goa": (15.2993, 74.1240),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639),
    "Jaipur": (26.9124, 75.7873),
}

CITY_CLIMATE = {
    "Delhi": {"desc": ["Sunny", "Partly Cloudy", "Clear sky", "Hazy", "Sunny"],
              "high": 35, "low": 22},
    "Mumbai": {"desc": ["Humid", "Partly Cloudy", "Sunny", "Overcast", "Breezy"],
               "high": 33, "low": 25},
    "Goa": {"desc": ["Sunny", "Clear sky", "Light Breeze", "Partly Cloudy", "Sunny"],
            "high": 32, "low": 24},
    "Bangalore": {"desc": ["Pleasant", "Partly Cloudy", "Light Rain", "Clear sky", "Breezy"],
                  "high": 28, "low": 18},
    "Chennai": {"desc": ["Hot & Sunny", "Humid", "Partly Cloudy", "Sunny", "Breezy"],
                "high": 36, "low": 26},
    "Hyderabad": {"desc": ["Sunny", "Clear sky", "Partly Cloudy", "Warm", "Sunny"],
                  "high": 34, "low": 22},
    "Kolkata": {"desc": ["Humid", "Partly Cloudy", "Warm", "Sunny", "Overcast"],
                "high": 33, "low": 24},
    "Jaipur": {"desc": ["Sunny", "Hot & Dry", "Clear sky", "Sunny", "Partly Cloudy"],
               "high": 38, "low": 24},
}


def _simulated_weather(city, days):
    """Return a simulated weather forecast when the live API is unavailable."""
    from datetime import date, timedelta

    climate = CITY_CLIMATE.get(city, {"desc": ["Sunny"] * 7, "high": 30, "low": 20})
    today = date.today()
    lines = [f"Weather forecast for {city} (estimated):"]
    for i in range(days):
        day_date = today + timedelta(days=i)
        desc = climate["desc"][i % len(climate["desc"])]
        high = climate["high"] + (i % 3) - 1
        low = climate["low"] + (i % 2)
        lines.append(
            f"  Day {i + 1} ({day_date}): {desc} | High: {high}C | Low: {low}C"
        )
    return "\n".join(lines)


def load_json(filename):
    """Load a JSON data file from the data directory."""
    path = f"{DATA_DIR}/{filename}"
    with open(path, "r") as f:
        return json.load(f)


@tool
def search_flights(query: str) -> str:
    """
    Search for available flights between two cities.

    The query must be in the format: 'FROM_CITY to TO_CITY'.
    Returns a list of matching flights sorted by price (cheapest first).

    Example query: 'Delhi to Goa'
    """
    try:
        parts = [p.strip() for p in query.lower().split(" to ")]
        if len(parts) != 2:
            return "Invalid query format. Use: 'City to City'"
        origin = parts[0].title()
        destination = parts[1].title()

        flights = load_json("flights.json")
        matches = [
            f for f in flights
            if f["from"].lower() == origin.lower()
            and f["to"].lower() == destination.lower()
        ]

        if not matches:
            return f"No flights found from {origin} to {destination}."

        matches.sort(key=lambda f: f["price"])

        results = []
        for f in matches:
            dep = datetime.fromisoformat(f["departure_time"])
            arr = datetime.fromisoformat(f["arrival_time"])
            duration_mins = int((arr - dep).total_seconds() / 60)
            results.append(
                f"Flight ID: {f['flight_id']} | {f['airline']} | "
                f"Departs: {dep.strftime('%H:%M')} | Arrives: {arr.strftime('%H:%M')} | "
                f"Duration: {duration_mins} min | Price: Rs.{f['price']}"
            )

        return f"Flights from {origin} to {destination}:\n" + "\n".join(results)

    except Exception as e:
        return f"Error searching flights: {str(e)}"


@tool
def search_hotels(query: str) -> str:
    """
    Search for hotels in a given city.

    The query must be a city name, optionally followed by budget and star rating filters.
    Format: 'CITY' or 'CITY budget:MAX_PRICE stars:MIN_STARS'

    Returns hotels sorted by star rating then price.

    Example queries:
      'Goa'
      'Delhi budget:4000 stars:4'
    """
    try:
        tokens = query.strip().split()
        city = tokens[0].title()
        max_price = None
        min_stars = None

        for token in tokens[1:]:
            if token.startswith("budget:"):
                max_price = int(token.split(":")[1])
            elif token.startswith("stars:"):
                min_stars = int(token.split(":")[1])

        hotels = load_json("hotels.json")
        matches = [h for h in hotels if h["city"].lower() == city.lower()]

        if max_price is not None:
            matches = [h for h in matches if h["price_per_night"] <= max_price]
        if min_stars is not None:
            matches = [h for h in matches if h["stars"] >= min_stars]

        if not matches:
            return f"No hotels found in {city} matching the given filters."

        matches.sort(key=lambda h: (-h["stars"], h["price_per_night"]))

        results = []
        for h in matches:
            amenities = ", ".join(h["amenities"])
            results.append(
                f"Hotel ID: {h['hotel_id']} | {h['name']} | "
                f"Stars: {h['stars']} | Rs.{h['price_per_night']}/night | "
                f"Amenities: {amenities}"
            )

        return f"Hotels in {city}:\n" + "\n".join(results)

    except Exception as e:
        return f"Error searching hotels: {str(e)}"


@tool
def search_places(query: str) -> str:
    """
    Search for tourist attractions and places of interest in a city.

    The query must be a city name, optionally with a type filter.
    Format: 'CITY' or 'CITY type:TYPE'

    Available types: temple, fort, museum, park, beach, lake, market, monument

    Returns places sorted by rating (highest first).

    Example queries:
      'Goa'
      'Delhi type:fort'
    """
    try:
        tokens = query.strip().split()
        city = tokens[0].title()
        place_type = None

        for token in tokens[1:]:
            if token.startswith("type:"):
                place_type = token.split(":")[1].lower()

        places = load_json("places.json")
        matches = [p for p in places if p["city"].lower() == city.lower()]

        if place_type:
            matches = [p for p in matches if p["type"].lower() == place_type]

        if not matches:
            return f"No places found in {city}."

        matches.sort(key=lambda p: -p["rating"])

        results = []
        for p in matches:
            results.append(
                f"Place ID: {p['place_id']} | {p['name']} | "
                f"Type: {p['type']} | Rating: {p['rating']}/5.0"
            )

        return f"Places in {city}:\n" + "\n".join(results)

    except Exception as e:
        return f"Error searching places: {str(e)}"


@tool
def get_weather(query: str) -> str:
    """
    Fetch weather forecast for a city and a travel period.

    The query must be in the format: 'CITY DAYS'
    where DAYS is an integer between 1 and 7.

    Returns daily max/min temperature, precipitation, and a simple weather summary.

    Example queries:
      'Goa 3'
      'Delhi 5'
    """
    try:
        tokens = query.strip().split()
        city = tokens[0].title()
        days = int(tokens[1]) if len(tokens) > 1 else 3
        days = max(1, min(days, 7))

        if city not in CITY_COORDINATES:
            return f"Weather data not available for {city}. Known cities: {', '.join(CITY_COORDINATES.keys())}"

        lat, lon = CITY_COORDINATES[city]
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
            f"&timezone=auto&forecast_days={days}"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weathercode", [])

        def weather_description(code):
            if code == 0:
                return "Clear sky"
            elif code <= 3:
                return "Partly cloudy"
            elif code <= 48:
                return "Foggy"
            elif code <= 67:
                return "Rainy"
            elif code <= 77:
                return "Snowy"
            elif code <= 82:
                return "Heavy showers"
            else:
                return "Thunderstorm"

        lines = [f"Weather forecast for {city}:"]
        for i in range(min(days, len(dates))):
            desc = weather_description(codes[i]) if i < len(codes) else "N/A"
            lines.append(
                f"  Day {i + 1} ({dates[i]}): {desc} | "
                f"High: {max_temps[i]}C | Low: {min_temps[i]}C | "
                f"Precipitation: {precip[i]}mm"
            )

        return "\n".join(lines)

    except requests.RequestException:
        return _simulated_weather(city, days)
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


@tool
def estimate_budget(query: str) -> str:
    """
    Estimate the total trip budget based on flight price, hotel price, and trip duration.

    The query must be in the format:
    'flight:PRICE hotel:PRICE_PER_NIGHT days:DAYS'

    A per-day local expense estimate of Rs.1500 is included for food and travel.

    Example query:
      'flight:4800 hotel:3200 days:3'
    """
    try:
        params = {}
        for token in query.strip().split():
            if ":" in token:
                key, value = token.split(":", 1)
                params[key] = float(value)

        flight_cost = params.get("flight", 0)
        hotel_per_night = params.get("hotel", 0)
        days = int(params.get("days", 3))
        daily_local = 1500

        hotel_total = hotel_per_night * days
        local_total = daily_local * days
        grand_total = flight_cost + hotel_total + local_total

        return (
            f"Budget Breakdown:\n"
            f"  Flight: Rs.{int(flight_cost)}\n"
            f"  Hotel ({days} nights @ Rs.{int(hotel_per_night)}/night): Rs.{int(hotel_total)}\n"
            f"  Food & Local Travel (Rs.{daily_local}/day x {days} days): Rs.{int(local_total)}\n"
            f"  Total Estimated Cost: Rs.{int(grand_total)}"
        )

    except Exception as e:
        return f"Error estimating budget: {str(e)}"
