import asyncio
import websockets

from cameras.receiver import (
    parse_rgbd_packet,
    parse_metadata
)
from cameras.display import display_frame
from config.settings import HOST, PORT
from processing.helpers import calculate_intrinsics

# Latest RGB-D frame for each camera and its metadata
camera_frames = {}
camera_metadata = {}

async def handle_client(websocket):

    print("Unity client connected")

    try:
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

                    print(f"Received metadata for Camera {camera_id}")
                    # print(metadata)
                else:
                    print(f"Received text: {message}")

                continue

            # Binary message → RGB frame
            if isinstance(message, bytes):
                rgbd_data = parse_rgbd_packet(message)

                if rgbd_data is None:
                    return

                camera_id = rgbd_data["camera_id"]
                frame_id = rgbd_data["frame_id"]
                rgb_frame = rgbd_data["rgb"]
                depth_frame = rgbd_data["depth"]

                camera_frames[camera_id] = {
                    "frame_id": frame_id,
                    "rgb": rgb_frame,
                    "depth": depth_frame
                }

                # print(
                #     f"[RGB-D] "
                #     f"Camera={camera_id} "
                #     f"Frame={frame_id} "
                #     f"RGB={rgb_frame.shape} "
                #     f"Depth={depth_frame.shape}"
                # )

                # print(
                #     f"[Storage] Camera={camera_id} "
                #     f"Frame={camera_frames[camera_id]['frame_id']} "
                #     f"RGB={camera_frames[camera_id]['rgb'].shape} "
                #     f"Depth={camera_frames[camera_id]['depth'].shape}"
                # )

                if camera_id is None:
                    print("Invalid binary packet")
                    continue


                display_frame(camera_id, rgb_frame)

    except websockets.ConnectionClosed:

        print("Unity client disconnected")

def get_camera_frame(camera_id):
    """
    Return the latest RGB-D frame for a camera.
    Returns None if no frame has been received.
    """
    return camera_frames.get(camera_id)

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