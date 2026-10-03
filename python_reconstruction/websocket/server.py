import asyncio
import websockets

from cameras.receiver import (
    parse_packet,
    decode_image,
    parse_metadata
)
from cameras.display import display_frame
from config.settings import HOST, PORT
from processing.helpers import calculate_intrinsics


async def handle_client(websocket):

    print("Unity client connected")

    try:
        camera_metadata = {}

        async for message in websocket:
            # Text message → Metadata
            if isinstance(message, str):

                metadata = parse_metadata(message)

                if metadata is not None:

                    camera_id = metadata["camera_id"]

                    width = metadata["width"]
                    height = metadata["height"]
                    fov = metadata["fov"]

                    K = calculate_intrinsics(
                        width,
                        height,
                        fov
                    )

                    metadata["intrinsics"] = K

                    camera_metadata[camera_id] = metadata

                    print(
                        f"Received metadata for Camera {camera_id}"
                    )

                    print(metadata)

                else:

                    print(f"Received text: {message}")

                continue

            # Binary message → RGB frame
            if isinstance(message, bytes):

                camera_id, jpeg_data = parse_packet(message)

                if camera_id is None:
                    print("Invalid binary packet")
                    continue

                frame = decode_image(jpeg_data)

                if frame is None:
                    print(
                        f"Failed to decode image from Camera {camera_id}"
                    )
                    continue

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