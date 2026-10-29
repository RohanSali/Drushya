import asyncio
import websockets

from cameras.receiver import parse_rgbd_packet, parse_metadata
from config.settings import HOST, PORT
from processing.helpers import calculate_intrinsics


# Latest RGB-D frame and metadata per camera.
# The receiver only updates these buffers; the main app owns all visualization.
camera_frames = {}
camera_metadata = {}


async def handle_client(websocket):
    print("Unity client connected")
    try:
        async for message in websocket:
            if isinstance(message, str):
                metadata = parse_metadata(message)
                if metadata is None:
                    continue

                camera_id = metadata["camera_id"]
                metadata["intrinsics"] = calculate_intrinsics(
                    metadata["width"],
                    metadata["height"],
                    metadata["fov"],
                )
                camera_metadata[camera_id] = metadata
                print(f"Received metadata for Camera {camera_id}")
                continue

            if isinstance(message, bytes):
                rgbd_data = parse_rgbd_packet(message)
                if rgbd_data is None:
                    continue

                camera_id = rgbd_data["camera_id"]
                if camera_id is None:
                    continue

                # Replacing the old record keeps only the latest frame.
                camera_frames[camera_id] = {
                    "frame_id": rgbd_data["frame_id"],
                    "rgb": rgbd_data["rgb"],
                    "depth": rgbd_data["depth"],
                    "received_at": asyncio.get_running_loop().time(),
                }

    except websockets.ConnectionClosed:
        print("Unity client disconnected")


def get_camera_frame(camera_id):
    return camera_frames.get(camera_id)


async def start_server():
    print(f"Starting WebSocket server on ws://{HOST}:{PORT}")
    async with websockets.serve(handle_client, HOST, PORT, max_size=None):
        print("Server is listening...")
        await asyncio.Future()
