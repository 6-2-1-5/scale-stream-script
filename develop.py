import asyncio
import json
import websockets
from datetime import datetime
import random
from printer.receipt import print_receipt, print_bill_payment_summary_receipt


async def generate_mock_weight():
    """Generate mock weight data between 100-9999"""
    return round(random.uniform(100, 9999))


async def handle_server_message(message):
    """Handle incoming messages from the server"""
    try:
        print("Received from server:", message)
        data = json.loads(message)

        # Handle specific message types
        # if data.get("command") == "print-bill":
        #     print_receipt(data)

        # switch case
        switcher = {
            "print-bill": print_receipt,
            "print-bill-payment-summary-receipt": print_bill_payment_summary_receipt,
        }

        # Get the function from switcher dictionary
        func = switcher.get(data.get("command"), lambda: "Invalid command")
        # Execute the function
        func(data)
    except json.JSONDecodeError:
        print("Error: Received invalid JSON message from server")
    except Exception as e:
        print(f"Error handling server message: {str(e)}")


async def send_weight_data(api_key):
    """Connect to WebSocket server and send weight data"""
    # uri = "ws://localhost:8080/api/ws/weight"
    uri = "wss://api.mangify.xyz/api/ws/weight"

    # Set up headers with API key
    # extra_headers = {"X-API-Key": api_key}
    extra_headers = {"X-API-Key": "yxB-RehKYilKtuxlkIFUc-znp-0M9cBuAVNXGJTZlbM"}

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
