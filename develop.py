import asyncio
import json
import websockets
from datetime import datetime
import random


async def generate_mock_weight():
    """Generate mock weight data between 100-9999"""
    return round(random.uniform(100, 9999))


async def send_weight_data(api_key):
    """Connect to WebSocket server and send weight data"""
    uri = "ws://localhost:8080/api/ws/weight"

    # Set up headers with API key
    extra_headers = {"X-API-Key": api_key}

    while True:
        try:
            async with websockets.connect(
                uri, extra_headers=extra_headers
            ) as websocket:
                print(f"Connected to WebSocket server at {uri}")

                while True:
                    # Generate mock weight data
                    weight = await generate_mock_weight()

                    # Create data payload (no API key needed here anymore)
                    data = {
                        "weight": weight,
                        "unit": "kg",
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Convert to JSON and send
                    message = json.dumps(data)
                    await websocket.send(message)
                    print(f"Sent: {message}")

                    # Wait before sending next reading
                    await asyncio.sleep(1.5)

        except websockets.exceptions.ConnectionClosed:
            print("Connection lost. Attempting to reconnect...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(5)


async def main():
    print("Starting desktop client...")
    api_key = input("Please enter the API key: ")

    # Validate API key
    if not api_key.strip():
        print("Error: API key cannot be empty")
        return

    print(f"Using API key: {api_key}")
    await send_weight_data(api_key)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
