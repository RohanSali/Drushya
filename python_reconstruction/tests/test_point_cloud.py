import asyncio

from websocket.server import (
    start_server,
    get_camera_frame,
    camera_frames,
    camera_metadata,
)

from processing.pipeline import (
    test_single_camera,
    visualize_point_cloud
)

# Camera ID 0 = North Camera
TARGET_CAMERA_ID = 0


async def run_test():
    server_task = asyncio.create_task(
        start_server()
    )

    print("Waiting for Unity RGB-D frames...")

    try:
        while True:
            frame_data = get_camera_frame(
                TARGET_CAMERA_ID
            )

            if frame_data is not None:
                break

            await asyncio.sleep(0.1)

        print(
            f"Received Camera {TARGET_CAMERA_ID}, "
            f"Frame {frame_data['frame_id']}"
        )

        # Wait for metadata from Unity
        while TARGET_CAMERA_ID not in camera_metadata:
            await asyncio.sleep(0.1)

        points, colors = test_single_camera(
            frame_data,
            camera_metadata[TARGET_CAMERA_ID]
        )

        # Visualize the generated point cloud
        visualize_point_cloud(points, colors)

        print("Point-cloud visualization test finished.")

    finally:
        server_task.cancel()


if __name__ == "__main__":
    asyncio.run(run_test())