#!/usr/bin/env python3
"""
Interactive client for the Restaurant Reservation MCP Server using MCP protocol and Gemini AI (for parameter extraction)
- Prompts the user for restaurant search and reservation details
- Connects to your running MCP server (at MCP_SERVER_URL)
- No mock data; calls real endpoints and displays results
"""
import os
import json
import asyncio
from typing import Dict, Any

import google.generativeai as genai
from fastmcp.client import Client

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

if not GEMINI_API_KEY:
    print("Error: Please set GEMINI_API_KEY environment variable")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

class RestaurantAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.mcp_client = Client(MCP_SERVER_URL)

    async def run(self):
        print("🍽️ Restaurant Reservation Assistant (via MCP Server)")
        print("Type 'exit' at any prompt to quit.")

        while True:
            user_query = input("Enter your restaurant search (e.g. 'Find a sushi place near me for 2 tonight'): \n> ").strip()
            if not user_query or user_query.lower() == "exit":
                print("Goodbye!")
                break

            params = await self.extract_params(user_query)
            if not params:
                print("Could not parse your request.")
                continue

            print("Searching for restaurants..")
            restaurants = await self.mcp_client.call_tool("search_restaurants", params)
            if not restaurants.get("restaurants"):
                print("No restaurants found. Try a different search.")
                continue

            for idx, r in enumerate(restaurants["restaurants"]):
                print(f"{idx+1}. {r['name']} (Rating: {r.get('rating', '-')}) - {r['address']}")
                print(f"   Phone: {r.get('phone', '-')}, Website: {r.get('website', '-')}")
                if r.get("opening_hours"):
                    print("   Hours:")
                    for h in r["opening_hours"]:
                        print(f"     {h}")
                print()
            # Ask which restaurant to reserve
            try:
                choice = int(input(f"Choose a restaurant to reserve (1-{len(restaurants['restaurants'])}, or 0 to skip): \n> "))
                if choice == 0:
                    continue
                chosen = restaurants["restaurants"][choice-1]
            except Exception:
                print("Invalid selection.")
                continue
            # Ask for reservation date and party size
            party_size = input("How many people? (default 2): \n> ").strip()
            party_size = int(party_size) if party_size else 2
            date = input("Date for reservation (YYYY-MM-DD; default=tonight): \n> ").strip()
            import datetime
            if not date:
                date = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime("%Y-%m-%d")
            # Get available slots
            slot_params = {
                "restaurant_name": chosen["name"],
                "date": date,
                "party_size": party_size
            }
            slots_result = await self.mcp_client.call_tool("get_available_slots", slot_params)
            slots = slots_result.get("available_slots", [])
            if not slots:
                print("No slots available. Try a different restaurant or date.")
                continue
            print("Available reservation times:")
            for idx, t in enumerate(slots):
                print(f"{idx+1}. {t}")
            try:
                slot_choice = int(input(f"Choose a time slot (1-{len(slots)}, or 0 to skip): \n> "))
                if slot_choice == 0:
                    continue
                chosen_time = slots[slot_choice-1]
            except Exception:
                print("Invalid selection.")
                continue
            # Collect booking info
            name = input("Your name: > ").strip() or "Guest"
            email = input("Your email: > ").strip() or "guest@example.com"
            special_requests = input("Any special requests? (optional): > ").strip()
            # Make reservation
            reservation_params = {
                "restaurant_name": chosen["name"],
                "restaurant_address": chosen["address"],
                "date": date,
                "time": chosen_time,
                "party_size": party_size,
                "customer_name": name,
                "customer_email": email,
                "special_requests": special_requests
            }
            result = await self.mcp_client.call_tool("make_reservation", reservation_params)
            rid = result.get("reservation_id")
            print("Reservation:")
            for k, v in result.items():
                print(f"  {k}: {v}")
            # Generate calendar invite if confirmed
            if rid:
                cal_result = await self.mcp_client.call_tool("generate_calendar_invite", {"reservation_id": rid})
                fname = cal_result.get("filename")
                if fname:
                    print(f"Calendar invite saved as: {fname}")
                else:
                    print("Could not create calendar invite.")
            print("---")

    async def extract_params(self, user_query: str) -> Dict[str, Any]:
        prompt = f"""
        Extract these fields from the restaurant search request: "{user_query}". 
        Return valid JSON for the following keys:
          - location: string
          - cuisine_type: string
          - min_rating: float
          - max_results: int (default 10)
        Omit keys if not specified.
        """
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"⚠️ Could not extract parameters automatically: {e}")
            # Fallback: ask user for info
            location = input("Enter a city/area (e.g. New York, NY): > ").strip()
            cuisine = input("Cuisine type (e.g. italian, sushi, etc): > ").strip()
            return {"location": location or "New York, NY", "cuisine_type": cuisine or "restaurant"}

if __name__ == "__main__":
    asyncio.run(RestaurantAssistant().run())
