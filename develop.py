import asyncio
import json
import websockets
from datetime import datetime
import random

async def generate_mock_weight():
    """Generate mock weight data between 100-9999"""
    return round(random.uniform(100, 9999))

async def send_weight_data():
    """Connect to WebSocket server and send weight data"""
    uri = "ws://localhost:8080/api/ws/weight"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to WebSocket server at {uri}")
                
                while True:
                    # Generate mock weight data
                    weight = await generate_mock_weight()
                    # print(f"Generated weight: {weight}")
                    
                    # Create data payload
                    data = {
                        "weight": weight,
                        "unit": "kg",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Convert to JSON and send
                    message = json.dumps(data)
                    await websocket.send(message)
                    print(f"Sent: {message}")
                    
                    # Wait before sending next reading
                    await asyncio.sleep(1.5)  # Matches server's broadcast interval
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection lost. Attempting to reconnect...")
            await asyncio.sleep(5)  # Wait 5 seconds before reconnecting
            
        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(5)  # Wait 5 seconds before retrying

async def main():
    print("Starting desktop client...")
    await send_weight_data()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")