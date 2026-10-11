import asyncio
import numpy as np

from websocket.server import start_server, get_camera_frame, camera_metadata
from processing.pipeline import reconstruct_single_camera, visualize_point_cloud


# Camera ID
TARGET_CAMERA_ID = 2

# Select "camera" to visualize camera-space points or "world" for world-space points.
POINT_SPACE = "world"  # "camera" or "world"

# Set True to print diagnostic information while testing.
DEBUG = True


def debug_depth_frame(depth):
    """Print compact depth diagnostics for the selected frame."""
    height, width = depth.shape
    sample_points = {
        "Top-left": (height // 4, width // 4),
        "Center": (height // 2, width // 2),
        "Top-right": (height // 4, 3 * width // 4),
        "Bottom-left": (3 * height // 4, width // 4),
        "Bottom-right": (3 * height // 4, 3 * width // 4),
    }

    print("\n========== DEPTH DIAGNOSTICS ==========")
    for name, (y, x) in sample_points.items():
        print(f"{name:12s}: {depth[y, x]:.3f} m")

    valid = np.isfinite(depth) & (depth > 0)
    if np.any(valid):
        values = depth[valid]
        print(f"Valid pixels: {valid.sum()} / {depth.size}")
        print(f"Depth min / median / max: {values.min():.3f} / "
              f"{np.median(values):.3f} / {values.max():.3f} m")
    print("======================================\n")


def debug_depth_profile(depth, row_ratio=0.5, samples=11):
    height, width = depth.shape
    row = int((height - 1) * row_ratio)
    columns = np.linspace(0, width - 1, samples, dtype=int)

    print("\n========== HORIZONTAL DEPTH PROFILE ==========")
    print(f"Frame: {width} x {height}; row: {row}")
    for col in columns:
        value = depth[row, col]
        print(f"x={col:4d} | depth={value:.3f} m" if np.isfinite(value) and value > 0
              else f"x={col:4d} | INVALID")
    print("==============================================\n")


def debug_reconstruction(result, metadata):
    camera_points = result["camera_points"]
    world_points = result["world_points"]

    print("\n========== RECONSTRUCTION DIAGNOSTICS ==========")
    print(f"Camera: {metadata['camera_id']}")
    print(f"Camera-space points: {len(camera_points)}")
    print(f"World-space points:  {len(world_points)}")
    print("Intrinsics:")
    print(result["intrinsics"])
    print("Camera-to-world transform:")
    print(result["camera_transform"])

    for label, points in (("Camera", camera_points), ("World", world_points)):
        if len(points):
            print(f"{label} XYZ min: {points.min(axis=0)}")
            print(f"{label} XYZ max: {points.max(axis=0)}")
    print("================================================\n")


async def run_test():
    if POINT_SPACE not in {"camera", "world"}:
        raise ValueError('POINT_SPACE must be either "camera" or "world".')

    server_task = asyncio.create_task(
        start_server()
    )
    
    try:
        print("Waiting for Unity RGB-D frames...")
        rgbd_frame = None

        while rgbd_frame is None:
            rgbd_frame = get_camera_frame(TARGET_CAMERA_ID)
            if rgbd_frame is None:
                await asyncio.sleep(0.1)

        while TARGET_CAMERA_ID not in camera_metadata:
            await asyncio.sleep(0.1)

        camera_info = camera_metadata[TARGET_CAMERA_ID]
        result = reconstruct_single_camera(rgbd_frame, camera_info)

        if DEBUG:
            print(f"Received Camera {TARGET_CAMERA_ID}, Frame {rgbd_frame['frame_id']}")
            debug_depth_frame(rgbd_frame["depth"])
            debug_depth_profile(rgbd_frame["depth"])
            debug_reconstruction(result, camera_info)

        points = result[f"{POINT_SPACE}_points"]
        camera_position = None
        if POINT_SPACE == "world":
            position = camera_info["position"]
            camera_position = [position["x"], position["y"], position["z"]]

        visualize_point_cloud(
            points,
            result["colors"],
            camera_position=camera_position,
            coordinate_space=POINT_SPACE,
        )

    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(run_test())