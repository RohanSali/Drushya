import cv2
import numpy as np
import json

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