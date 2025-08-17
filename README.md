# Restaurant Reservation MCP Server

A complete **Model Context Protocol (MCP)** server for restaurant discovery and reservations, integrated with **Google AI Studio (Gemini API)** and **Google Places API**. This project demonstrates how to build an AI-powered restaurant booking system that can search for restaurants, simulate reservations, and generate calendar invites.

## 🚀 Features

- **🔍 Restaurant Search**: Find restaurants using Google Places API with filters for cuisine, location, rating, and price
- **🤖 AI Integration**: Use Google AI Studio (Gemini) to understand natural language queries
- **📅 Reservation System**: Mock reservation system with availability checking
- **📧 Calendar Invites**: Generate `.ics` calendar files for reservations
- **🛠️ MCP Protocol**: Fully compliant with Model Context Protocol standard
- **💰 Free APIs**: Uses only free tiers of Google services

## 📋 Prerequisites

- Python 3.10+ 
- Google Cloud Account (free tier)
- Google AI Studio Account (free)

## 🔧 Setup Instructions

### 1. Clone and Install Dependencies

```bash
# Clone or download the project files
# Install required packages
pip install -r requirements.txt
```

### 2. Get API Keys

#### Google Places API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Places API** and **Geocoding API**
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "API Key"
6. Copy your API key

#### Google AI Studio (Gemini) API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" in the top-left
4. Click "Create API key"
5. Copy your API key

### 3. Configure Environment Variables

```bash

# Edit .env and add your API keys
GOOGLE_PLACES_API_KEY=your_actual_places_api_key
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 4. Run the MCP Server

```bash
# Start the MCP server
python server.py
```

### 5. Test with Example Client

```bash
# Run the example client (in a new terminal)
python client.py
```

## 🛠️ Available MCP Tools

The server provides these tools that can be used by any MCP client:

### `search_restaurants`
Search for restaurants with filters
```json
{
  "location": "New York, NY",
  "cuisine_type": "italian", 
  "radius": 5000,
  "min_rating": 4.0,
  "max_results": 10
}
```

### `get_available_slots`
Get available reservation time slots (mock data)
```json
{
  "restaurant_name": "Bella Italia",
  "date": "2025-08-20",
  "party_size": 4
}
```

### `make_reservation`
Create a restaurant reservation
```json
{
  "restaurant_name": "Bella Italia",
  "restaurant_address": "123 Main St, New York, NY", 
  "date": "2025-08-20",
  "time": "19:00",
  "party_size": 4,
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "special_requests": "Window seat preferred"
}
```

### `generate_calendar_invite`
Generate a .ics calendar file for a reservation
```json
{
  "reservation_id": "RES12345",
  "duration_minutes": 90
}
```

### `list_reservations`
List all reservations (optionally filtered by email)
```json
{
  "customer_email": "john@example.com"
}
```

## 💻 Usage Examples

### Using with Natural Language

```python
# The client can understand natural language:
user_input = "Find me a good Italian restaurant in Manhattan for tonight, party of 4"

# AI extracts: location="Manhattan, NY", cuisine_type="italian", party_size=4
# Then calls: search_restaurants(location="Manhattan, NY", cuisine_type="italian")
```

### Direct MCP Tool Calls

```python
# Direct tool usage:
result = mcp_server.call_tool("search_restaurants", {
    "location": "Los Angeles, CA",
    "cuisine_type": "sushi",
    "min_rating": 4.5,
    "max_results": 5
})
```

## 🏗️ Project Structure

```
restaurant-mcp/
├── server.py              # Main MCP server implementation
├── client_example.py      # Example client with AI integration  
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your actual API keys (create this)
└── README.md             # This file
```

## 🔌 Integrating with Your Own Client

To use this MCP server in your own application:

1. **Start the server**: `python server.py`
2. **Connect your MCP client** to the server endpoint
3. **Use the available tools** listed above

### Example with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "restaurant-server": {
      "command": "python",
      "args": ["path/to/your/server.py"],
      "env": {
        "GOOGLE_PLACES_API_KEY": "your_key_here",
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

## ⚠️ Important Notes

### Limitations
- **Mock Reservations**: The reservation system is simulated. Real integration would require restaurant booking APIs (like OpenTable)
- **Rate Limits**: Google Places API has usage quotas on the free tier
- **Development Only**: This is a demo project, not production-ready

### Security
- Never commit API keys to version control
- Use environment variables for all secrets
- Consider using Google Cloud IAM for production deployments

## 🎯 Next Steps & Enhancements

Want to extend this project? Here are some ideas:

- **Real Booking APIs**: Integrate with OpenTable, Resy, or restaurant-specific booking systems
- **Payment Processing**: Add Stripe integration for reservation deposits
- **SMS Notifications**: Send confirmation texts using Twilio
- **Multi-language Support**: Use Gemini's multilingual capabilities
- **Restaurant Reviews**: Scrape and analyze reviews for better recommendations
- **Availability Caching**: Cache real-time availability data
- **User Authentication**: Add user accounts and reservation history

## 🐛 Troubleshooting

### Common Issues

**"Google Places API key not configured"**
- Make sure you've set `GOOGLE_PLACES_API_KEY` in your `.env` file
- Verify the Places API is enabled in Google Cloud Console

**"No restaurants found"** 
- Check that your location string is valid (e.g., "New York, NY")
- Try increasing the search radius
- Lower the minimum rating filter

**Calendar invite not opening**
- Make sure you have a calendar application installed
- Try opening the `.ics` file manually from your file system

**Happy dining! 🍽️**
