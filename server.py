#!/usr/bin/env python3.11
"""
Restaurant Reservation MCP Server
Integrates with Google AI Studio (Gemini API) and Google Places API
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

import requests
from fastmcp import FastMCP
from ics import Calendar, Event
import logging

logging.basicConfig(
    level=logging.INFO,                    # Set level to info
    format="%(levelname)s:%(name)s:%(message)s"  # Format (optional)
)
log = logging.getLogger(__name__)


# Initialize MCP server
mcp = FastMCP("Restaurant Reservation Server")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration - Set these environment variables
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

if not GOOGLE_PLACES_API_KEY:
    print("Warning: GOOGLE_PLACES_API_KEY not set")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not set")

# Mock database for reservations
reservations_db = []

@dataclass
class Restaurant:
    place_id: str
    name: str
    address: str
    rating: float
    price_level: int
    phone: str
    website: str
    types: List[str]

@dataclass
class Reservation:
    reservation_id: str
    restaurant_name: str
    restaurant_address: str
    date_time: datetime
    party_size: int
    customer_name: str
    customer_email: str
    special_requests: str
    status: str = "confirmed"

@mcp.tool
def search_restaurants(
    location: str = "Los Angeles, CA",
    cuisine_type: str = "Italian",
    radius: int = 5000,
    min_rating: float = 4.0,
    max_results: int = 10,
    special_requirements: str = "",
    party_size: int = 2
) -> Dict[str, Any]:
    """
    Search for restaurants using Google Places API

    Args:
        location: Location to search (e.g., "New York, NY")
        cuisine_type: Type of cuisine (e.g., "italian", "chinese", "restaurant")
        radius: Search radius in meters (default: 5000)
        min_rating: Minimum rating filter (default: 4.0)
        max_results: Maximum number of results (default: 10)

    Returns:
        Dictionary containing list of restaurants with details
    """

    if not GOOGLE_PLACES_API_KEY:
        return {"error": "Google Places API key not configured"}
    
    try:
        # First, get coordinates for the location
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            "address": location,
            "key": GOOGLE_PLACES_API_KEY
        }

        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_data = geocode_response.json()
        log.info(geocode_data)
        if not geocode_data.get("results"):
            return {"error": f"Could not find location: {location}"}
        lat = geocode_data["results"][0]["geometry"]["location"]["lat"]
        lng = geocode_data["results"][0]["geometry"]["location"]["lng"]

        # Search for restaurants
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "restaurant",
            "key": GOOGLE_PLACES_API_KEY
        }

        if cuisine_type != "restaurant":
            params["keyword"] = cuisine_type

        response = requests.get(places_url, params=params)
        data = response.json()
        log.info(data)
        if "results" not in data:
            return {"error": "No restaurants found"}

        restaurants = []
        for result in data["results"][:max_results]:
            if result.get("rating", 0) >= min_rating:
                restaurant = {
                    "place_id": result.get("place_id", ""),
                    "name": result.get("name", "Unknown"),
                    "address": result.get("vicinity", ""),
                    "rating": result.get("rating", 0),
                    "price_level": result.get("price_level", 0),
                    "types": result.get("types", []),
                    "open_now": result.get("opening_hours", {}).get("open_now", None)
                }
                restaurants.append(restaurant)

        # Get additional details for top restaurants
        detailed_restaurants = []
        for restaurant in restaurants[:5]:  # Get details for top 5
            details = get_restaurant_details(restaurant["place_id"])
            if details:
                restaurant.update(details)
            detailed_restaurants.append(restaurant)

        return {
            "restaurants": detailed_restaurants,
            "total_found": len(restaurants),
            "search_location": location,
            "coordinates": {"lat": lat, "lng": lng}
        }

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def get_restaurant_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information about a restaurant"""
    if not GOOGLE_PLACES_API_KEY or not place_id:
        return {}

    try:
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "formatted_phone_number,website,opening_hours,photos",
            "key": GOOGLE_PLACES_API_KEY
        }

        response = requests.get(details_url, params=params)
        data = response.json()

        if "result" in data:
            result = data["result"]
            return {
                "phone": result.get("formatted_phone_number", ""),
                "website": result.get("website", ""),
                "opening_hours": result.get("opening_hours", {}).get("weekday_text", [])
            }

    except Exception as e:
        print(f"Error getting restaurant details: {e}")

    return {}

@mcp.tool
def get_available_slots(
    restaurant_name: str,
    date: str,
    party_size: int = 2
) -> Dict[str, Any]:
    """
    Get available reservation time slots for a restaurant
    This is a mock implementation since we don't have access to real reservation systems

    Args:
        restaurant_name: Name of the restaurant
        date: Date in YYYY-MM-DD format
        party_size: Number of people (default: 2)

    Returns:
        Dictionary with available time slots
    """

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")

        # Mock available time slots (in a real app, this would query restaurant's booking system)
        base_times = ["17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00"]

        # Remove some slots randomly to simulate real availability
        import random
        available_slots = random.sample(base_times, k=random.randint(4, 7))
        available_slots.sort()

        return {
            "restaurant_name": restaurant_name,
            "date": date,
            "party_size": party_size,
            "available_slots": available_slots,
            "note": "These are mock time slots. In a real implementation, this would connect to the restaurant's booking system."
        }

    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    except Exception as e:
        return {"error": f"Could not get available slots: {str(e)}"}

@mcp.tool 
def make_reservation(
    restaurant_name: str,
    restaurant_address: str,
    date: str,
    time: str,
    party_size: int,
    customer_name: str,
    customer_email: str,
    special_requests: str = ""
) -> Dict[str, Any]:
    """
    Make a restaurant reservation

    Args:
        restaurant_name: Name of the restaurant
        restaurant_address: Restaurant address
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        party_size: Number of people
        customer_name: Customer's full name
        customer_email: Customer's email address
        special_requests: Any special requests or notes

    Returns:
        Dictionary with reservation confirmation details
    """

    try:
        # Parse date and time
        reservation_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        # Generate reservation ID
        reservation_id = str(uuid.uuid4())[:8].upper()

        # Create reservation
        reservation = Reservation(
            reservation_id=reservation_id,
            restaurant_name=restaurant_name,
            restaurant_address=restaurant_address,
            date_time=reservation_datetime,
            party_size=party_size,
            customer_name=customer_name,
            customer_email=customer_email,
            special_requests=special_requests
        )

        # Store in mock database
        reservations_db.append(reservation)

        return {
            "status": "confirmed",
            "reservation_id": reservation_id,
            "restaurant_name": restaurant_name,
            "restaurant_address": restaurant_address,
            "date_time": reservation_datetime.isoformat(),
            "party_size": party_size,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "special_requests": special_requests,
            "message": f"Reservation confirmed for {customer_name} at {restaurant_name} on {date} at {time} for {party_size} people."
        }

    except ValueError as e:
        return {"error": f"Invalid date/time format: {str(e)}"}
    except Exception as e:
        return {"error": f"Reservation failed: {str(e)}"}

@mcp.tool
def generate_calendar_invite(
    reservation_id: str,
    duration_minutes: int = 90
) -> Dict[str, Any]:
    """
    Generate a calendar invite (.ics file) for a reservation

    Args:
        reservation_id: The reservation ID
        duration_minutes: Duration of the reservation in minutes (default: 90)

    Returns:
        Dictionary with calendar invite data and download information
    """

    try:
        # Find the reservation
        reservation = None
        for res in reservations_db:
            if res.reservation_id == reservation_id:
                reservation = res
                break

        if not reservation:
            return {"error": f"Reservation {reservation_id} not found"}

        # Create calendar
        cal = Calendar()

        # Create event
        event = Event()
        event.name = f"Dinner at {reservation.restaurant_name}"
        event.begin = reservation.date_time
        event.end = reservation.date_time + timedelta(minutes=duration_minutes)
        event.description = f"""
Reservation Details:
- Restaurant: {reservation.restaurant_name}
- Address: {reservation.restaurant_address}
- Party Size: {reservation.party_size} people
- Reservation ID: {reservation.reservation_id}
- Special Requests: {reservation.special_requests}

Please arrive 5-10 minutes early.
        """.strip()
        event.location = reservation.restaurant_address

        # Add event to calendar
        cal.events.add(event)

        # Generate the .ics content
        ics_content = str(cal)

        # Save to file
        filename = f"reservation_{reservation_id}.ics"
        with open(filename, 'w') as f:
            f.write(ics_content)

        import subprocess
        subprocess.run(["open", filename])


        return {
            "status": "success",
            "reservation_id": reservation_id,
            "filename": filename,
            "event_title": event.name,
            "event_start": reservation.date_time.isoformat(),
            "event_end": (reservation.date_time + timedelta(minutes=duration_minutes)).isoformat(),
            "location": reservation.restaurant_address,
            "ics_content": ics_content,
            "message": f"Calendar invite generated: {filename}"
        }

    except Exception as e:
        return {"error": f"Failed to generate calendar invite: {str(e)}"}

@mcp.tool
def list_reservations(customer_email: str = "") -> Dict[str, Any]:
    """
    List all reservations, optionally filtered by customer email

    Args:
        customer_email: Filter by customer email (optional)

    Returns:
        Dictionary with list of reservations
    """

    try:
        filtered_reservations = []

        for res in reservations_db:
            if not customer_email or res.customer_email.lower() == customer_email.lower():
                filtered_reservations.append({
                    "reservation_id": res.reservation_id,
                    "restaurant_name": res.restaurant_name,
                    "restaurant_address": res.restaurant_address,
                    "date_time": res.date_time.isoformat(),
                    "party_size": res.party_size,
                    "customer_name": res.customer_name,
                    "customer_email": res.customer_email,
                    "special_requests": res.special_requests,
                    "status": res.status
                })

        return {
            "reservations": filtered_reservations,
            "total_count": len(filtered_reservations),
            "filter_email": customer_email if customer_email else "none"
        }

    except Exception as e:
        return {"error": f"Could not list reservations: {str(e)}"}

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="http", host="127.0.0.1", port=9000)
