import cv2
import numpy as np
import json

from config.settings import (
    FRAME_WIDTH,
    FRAME_HEIGHT
)

def parse_rgbd_packet(message: bytes):
    """
    Parse the binary RGB-D packet sent by Unity.

    Packet layout:
        0-3    : Camera ID
        4-7    : Frame ID
        8-11   : RGB JPEG length
        12-15  : Depth data length
        16-... : RGB JPEG
        ...    : uint16 depth data
    """

    HEADER_SIZE = 16

    if len(message) < HEADER_SIZE:
        print("[RGB-D] Packet too small.")
        return None

    # Header
    camera_id = int.from_bytes(
        message[0:4],
        byteorder="big"
    )

    frame_id = int.from_bytes(
        message[4:8],
        byteorder="big"
    )

    rgb_length = int.from_bytes(
        message[8:12],
        byteorder="big"
    )

    depth_length = int.from_bytes(
        message[12:16],
        byteorder="big"
    )

    # Validate packet size
    expected_size = (
        HEADER_SIZE +
        rgb_length +
        depth_length
    )

    if len(message) != expected_size:
        print(
            f"[RGB-D] Invalid packet size. "
            f"Expected={expected_size}, "
            f"Received={len(message)}"
        )
        return None

    # Extract RGB
    rgb_start = HEADER_SIZE
    rgb_end = rgb_start + rgb_length

    jpeg_data = message[
        rgb_start:rgb_end
    ]

    # Extract depth
    depth_start = rgb_end
    depth_end = depth_start + depth_length

    depth_bytes = message[
        depth_start:depth_end
    ]

    # Decode RGB
    rgb_array = np.frombuffer(
        jpeg_data,
        dtype=np.uint8
    )

    rgb_frame = cv2.imdecode(
        rgb_array,
        cv2.IMREAD_COLOR
    )

    if rgb_frame is None:
        print(
            f"[RGB-D] Failed to decode RGB "
            f"for Camera {camera_id}"
        )
        return None

    # Decode depth
    if depth_length % 2 != 0:
        print(
            f"[RGB-D] Invalid depth length: "
            f"{depth_length}"
        )
        return None

    depth_data = np.frombuffer(
        depth_bytes,
        dtype="<u2"
    )

    # Convert big-endian uint16 to native
    depth_data = depth_data.astype(
        np.uint16
    )

    # Convert from millimeters to Unity world units
    depth_data = (
        depth_data.astype(np.float32)
        / 1000.0
    )

    # Reshape depth
    expected_depth_values = (
        FRAME_WIDTH * FRAME_HEIGHT
    )

    if len(depth_data) != expected_depth_values:
        print(
            f"[RGB-D] Unexpected depth size. "
            f"Expected={expected_depth_values}, "
            f"Received={len(depth_data)}"
        )
        return None

    depth_frame = depth_data.reshape(
        (FRAME_HEIGHT, FRAME_WIDTH)
    )

    return {
        "camera_id": camera_id,
        "frame_id": frame_id,
        "rgb": rgb_frame,
        "depth": depth_frame
    }

def parse_metadata(message: str):
    """
    Parse a camera metadata JSON message.
    """

    try:
        data = json.loads(message)

    except json.JSONDecodeError:
        return None

    if data.get("type") != "camera_metadata":
        return None

    return data

def parse_packet(message: bytes):
    """
    Parse:
        [4-byte camera ID][JPEG data]

    Returns:
        camera_id, jpeg_data
    """

    if len(message) < 4:
        return None, None

    camera_id = int.from_bytes(
        message[0:4],
        byteorder="big"
    )

    jpeg_data = message[4:]

    return camera_id, jpeg_data


def decode_image(jpeg_data: bytes):
    """
    Decode JPEG bytes into an OpenCV image.
    """

    jpeg_array = np.frombuffer(
        jpeg_data,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        jpeg_array,
        cv2.IMREAD_COLOR
    )

    return frame