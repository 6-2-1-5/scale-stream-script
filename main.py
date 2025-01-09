import serial
import binascii
import json
import asyncio
import websockets
from datetime import datetime

# Store connected clients
connected_clients = set()


def parse_weight_data(hex_data):
    """
    Parse weight data according to Toledo Format settings:
    - Weight position: 5
    - Weight size: 6
    - Total data size: 17
    """
    try:
        # Check for minimum complete packet
        if not (hex_data.startswith("02") and "0d0a" in hex_data):
            return None

        # Convert hex string to bytes
        data_bytes = bytes.fromhex(hex_data)
        data_str = data_bytes.decode("ascii")

        # Extract weight value starting from position 5 for 6 characters
        # Add 1 to skip the STX (02) character
        start_pos = 5 + 1  # Position 5 after STX
        end_pos = start_pos + 6  # 6 characters for weight

        if len(data_str) >= end_pos:
            weight_str = data_str[start_pos:end_pos].strip()
            if weight_str and any(c.isdigit() for c in weight_str):
                return float(weight_str)
        return None

    except Exception as e:
        print(f"Error parsing weight: {str(e)}")
        return None


async def broadcast_weight(weight):
    """
    Broadcast weight data to all connected clients
    """
    if not connected_clients:
        return

    # Create data object
    data = {"weight": weight, "unit": "kg", "timestamp": datetime.now().isoformat()}

    # Convert to JSON string
    message = json.dumps(data)

    # Broadcast to all connected clients
    if connected_clients:  # Only print if there are clients
        print(f"Broadcasting: {message}")

    # Send to all connected clients
    websockets_tasks = []
    for (
        websocket
    ) in connected_clients.copy():  # Use copy to avoid runtime modification issues
        try:
            websockets_tasks.append(asyncio.create_task(websocket.send(message)))
        except websockets.exceptions.ConnectionClosed:
            connected_clients.remove(websocket)

    if websockets_tasks:
        await asyncio.gather(*websockets_tasks)


async def handle_client(websocket, path):
    """
    Handle new WebSocket client connections
    """
    # Register new client
    print("Client connected")
    connected_clients.add(websocket)
    try:
        # Keep connection alive and handle any client messages
        async for message in websocket:
            # Here you can handle any messages from the client if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Unregister client on disconnect
        connected_clients.remove(websocket)
        print("Client disconnected")


async def run_serial_reader():
    """
    Handle serial port reading
    """
    try:
        ser = serial.Serial(
            port="COM3",
            baudrate=1200,
            timeout=1,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
        )
        print("Serial port opened successfully")

        buffer = ""

        while True:
            if ser.in_waiting:
                # Read available data
                data = ser.read(ser.in_waiting)

                # Add to buffer
                buffer += binascii.hexlify(data).decode("utf-8")

                # Process complete packets
                if "0d0a" in buffer:
                    packets = buffer.split("0d0a")
                    buffer = packets[-1]  # Keep the incomplete part

                    # Process complete packets
                    for packet in packets[:-1]:
                        packet += "0d0a"
                        weight = parse_weight_data(packet)
                        if weight is not None:
                            print(f"Weight: {weight:.1f} kg")
                            # Broadcast weight to all connected clients
                            await broadcast_weight(weight)

            await asyncio.sleep(1.0)

    except Exception as e:
        print(f"Serial port error: {str(e)}")
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")


async def main():
    # Start WebSocket server
    async with websockets.serve(handle_client, "localhost", 8081):
        print("WebSocket server running on ws://localhost:8081")
        # Run serial reader
        await run_serial_reader()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
