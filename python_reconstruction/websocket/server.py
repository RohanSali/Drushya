import asyncio
import websockets

from cameras.receiver import parse_packet, decode_image
from cameras.display import display_frame
from config.settings import HOST, PORT


async def handle_client(websocket):

    print("Unity client connected")

    try:

        async for message in websocket:

            if not isinstance(message, bytes):
                print(f"Received: {message}")
                continue

            camera_id, jpeg_data = parse_packet(message)

            if camera_id is None:
                print("Invalid packet")
                continue

            frame = decode_image(jpeg_data)

            if frame is None:
                print(
                    f"Failed to decode image from Camera {camera_id}"
                )
                continue

            print(
                f"Camera {camera_id}: "
                f"{frame.shape[1]}x{frame.shape[0]}"
            )

            display_frame(camera_id, frame)

    except websockets.ConnectionClosed:

        print("Unity client disconnected")


async def start_server():

    print(
        f"Starting WebSocket server "
        f"on ws://{HOST}:{PORT}"
    )

    async with websockets.serve(
        handle_client,
        HOST,
        PORT
    ):

        print("Server is listening...")

        await asyncio.Future()