import cv2

def display_frame(camera_id, frame):
    """
    Display the latest frame from a camera.
    """

    if frame is None:
        return

    cv2.imshow(
        f"Camera {camera_id}",
        frame
    )

    cv2.waitKey(1)