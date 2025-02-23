import asyncio
import json
import websockets
from datetime import datetime
import random
import os
import subprocess


def print_receipt(data):
    """
    macOS implementation of print_receipt
    Prints receipt data to console and creates a text file
    """
    receipt_content = (
        "\n=== RECEIPT ===\n"
        f"Timestamp: {data.get('timestamp', 'N/A')}\n"
        f"Weight: {data.get('weight', 'N/A')} {data.get('unit', 'N/A')}\n"
        "==============\n"
    )

    # Print to console
    print(receipt_content)

    # Save to file in a receipts directory
    try:
        # Create receipts directory if it doesn't exist
        if not os.path.exists("receipts"):
            os.makedirs("receipts")

        # Generate filename with timestamp
        filename = f"receipts/receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Write receipt to file
        with open(filename, "w") as f:
            f.write(receipt_content)

        # Optionally, you can uncomment the following lines to automatically print using 'lpr'
        # subprocess.run(['lpr', filename])
        print(f"Receipt saved to: {filename}")

    except Exception as e:
        print(f"Error saving receipt: {str(e)}")


async def generate_mock_weight():
    """Generate mock weight data between 100-9999"""
    return round(random.uniform(100, 9999), 2)


async def handle_server_message(message):
    """Handle incoming messages from the server"""
    try:
        print("Received from server:", message)
        data = json.loads(message)

        # Handle specific message types
        if data.get("command") == "print-bill":
            print_receipt(data)

    except json.JSONDecodeError:
        print("Error: Received invalid JSON message from server")
    except Exception as e:
        print(f"Error handling server message: {str(e)}")


async def send_weight_data(api_key):
    """Connect to WebSocket server and send weight data"""
    uri = "ws://localhost:8080/api/ws/weight"
    extra_headers = {"X-API-Key": api_key}

    while True:
        try:
            async with websockets.connect(
                uri, extra_headers=extra_headers
            ) as websocket:
                print(f"Connected to WebSocket server at {uri}")

                # Create two tasks: one for sending data, one for receiving
                async def send_loop():
                    while True:
                        weight = await generate_mock_weight()
                        data = {
                            "command": "weight",
                            "data": {
                                "weight": weight,
                                "unit": "kg",
                                "timestamp": datetime.now().isoformat(),
                            },
                        }
                        message = json.dumps(data)
                        await websocket.send(message)
                        print(f"Sent: {message}")
                        await asyncio.sleep(1.5)

                async def receive_loop():
                    while True:
                        message = await websocket.recv()
                        print(f"Received: {message}")
                        await handle_server_message(message)

                # Run both tasks concurrently
                await asyncio.gather(
                    send_loop(),
                    receive_loop(),
                )

        except websockets.exceptions.ConnectionClosed:
            print("Connection lost. Attempting to reconnect...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(5)


async def main():
    print("Starting macOS desktop client...")

    # You can hardcode the API key here for development
    api_key = "yxB-RehKYilKtuxlkIFUc-znp-0M9cBuAVNXGJTZlbM"
    # Or uncomment the following line to input it manually:
    # api_key = input("Please enter the API key: ")

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
