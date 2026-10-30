import asyncio
import numpy as np
import open3d as o3d
import cv2

from websocket.server import start_server, get_camera_frame, camera_metadata
from processing.pipeline import reconstruct_single_camera
from processing.helpers import unity_position_to_open3d


TARGET_CAMERA_IDS = [0, 1, 2, 3]
STRIDE = 1
MAX_DEPTH = 50.0
DEBUG = True

CAMERA_NAMES = {
    0: "North",
    1: "East",
    2: "South",
    3: "West",
}

EXPECTED_FORWARD = {
    0: np.array([0.0, 0.0, 1.0]),   # North
    1: np.array([1.0, 0.0, 0.0]),   # East
    2: np.array([0.0, 0.0, -1.0]),  # South
    3: np.array([-1.0, 0.0, 0.0]),  # West
}

def camera_position_from_metadata(metadata):
    """
    Extract the camera position from Unity metadata and convert it to the
    right-handed Open3D coordinate system (Z-flip).
    """
    position = metadata["position"]
    unity_pos = np.array(
        [position["x"], position["y"], position["z"]],
        dtype=np.float64,
    )
    return unity_position_to_open3d(unity_pos)


def print_camera_summary(camera_id, frame, metadata, result):
    camera_points = result["camera_points"]
    world_points = result["world_points"]

    def vector_to_array(key):
        vector = metadata[key]
        return np.array(
            [vector["x"], vector["y"], vector["z"]],
            dtype=np.float64,
        )

    position = vector_to_array("position")
    forward = vector_to_array("forward")
    right = vector_to_array("right")
    up = vector_to_array("up")

    expected = EXPECTED_FORWARD[camera_id]

    print(f"\n{'=' * 20} CAMERA {camera_id}: "
          f"{CAMERA_NAMES[camera_id]} {'=' * 20}")

    print(f"Frame ID: {frame['frame_id']}")

    print("\n--- Unity Camera Metadata ---")
    print("Position:", position.round(4))
    print("Rotation:", metadata["rotation"])
    print("Forward:", forward.round(4))
    print("Right:", right.round(4))
    print("Up:", up.round(4))
    print("Resolution:", metadata["width"], "x", metadata["height"])
    print("FOV:", metadata["fov"])

    print("\n--- Direction Check ---")
    print("Expected forward:", expected)
    print("Actual forward:  ", forward.round(4))
    print(
        "Direction dot product:",
        round(float(np.dot(expected, forward)), 4),
    )

    print("\n--- Point Cloud Statistics (Open3D right-handed world space) ---")
    print("Camera-space points:", len(camera_points))
    print("World-space points:", len(world_points))

    if len(camera_points):
        print("Camera-space minimum:", camera_points.min(axis=0).round(4))
        print("Camera-space maximum:", camera_points.max(axis=0).round(4))
        print("Camera-space mean:", camera_points.mean(axis=0).round(4))

    if len(world_points):
        print("World-space minimum:", world_points.min(axis=0).round(4))
        print("World-space maximum:", world_points.max(axis=0).round(4))
        print("World-space mean:", world_points.mean(axis=0).round(4))

    print("\n--- Camera-to-World Matrix (Unity space) ---")
    print(result["camera_transform"].round(4))
    print("=" * 65)


def visualize_fused_point_cloud(points, colors, camera_positions):
    if points is None or len(points) == 0:
        raise ValueError("The fused point cloud contains no points.")

    points = np.asarray(points, dtype=np.float64)

    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)

    if colors is not None:
        colors = np.asarray(colors, dtype=np.float64)

        if colors.shape != points.shape:
            raise ValueError(
                "Fused colors must have the same Nx3 shape as points."
            )

        cloud.colors = o3d.utility.Vector3dVector(
            np.clip(colors, 0.0, 1.0)
        )

    geometries = [
        cloud,
        o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=1.0,
            origin=[0.0, 0.0, 0.0],
        ),
    ]

    # camera_positions are already in Open3D right-handed space (converted in
    # camera_position_from_metadata) so no further conversion is needed here.
    for position in camera_positions:
        marker = o3d.geometry.TriangleMesh.create_sphere(radius=0.10)
        marker.translate(np.asarray(position, dtype=np.float64))
        marker.paint_uniform_color([1.0, 0.0, 0.0])
        geometries.append(marker)

    visualizer = o3d.visualization.Visualizer()

    visualizer.create_window(
        window_name="Drushya - Multi-Camera Fused Point Cloud",
        width=1280,
        height=800,
    )

    for geometry in geometries:
        visualizer.add_geometry(geometry)

    # Initialize the view after the window and geometries exist.
    visualizer.poll_events()
    visualizer.update_renderer()

    view_control = visualizer.get_view_control()

    # In the Open3D right-handed world (after Z-flip):
    #   +X = East (right in Unity)
    #   +Y = up
    #   +Z = South (was Unity -Z, i.e. the flipped axis)
    # Look at the scene centre from slightly above, front = -Z (looking toward +Z).
    view_control.set_lookat([0.0, 2.0, 0.0])
    view_control.set_front([0.0, 0.5, 1.0])   # South looking North, slightly elevated
    view_control.set_up([0.0, 1.0, 0.0])
    view_control.set_zoom(0.15)

    visualizer.update_renderer()
    visualizer.run()
    visualizer.destroy_window()


async def run_test():
    server_task = asyncio.create_task(start_server())

    try:
        print("Waiting for Unity RGB-D frames and metadata...")
        frames = {}

        while len(frames) < len(TARGET_CAMERA_IDS):
            for camera_id in TARGET_CAMERA_IDS:
                if camera_id in frames:
                    continue

                frame = get_camera_frame(camera_id)

                # Wait until both the frame and its metadata are available.
                if frame is None or camera_id not in camera_metadata:
                    continue

                frames[camera_id] = frame

            if len(frames) < len(TARGET_CAMERA_IDS):
                await asyncio.sleep(0.1)

        all_world_points = []
        all_colors = []
        camera_positions = []

        for camera_id in TARGET_CAMERA_IDS:
            frame = frames[camera_id]
            metadata = camera_metadata[camera_id]

            result = reconstruct_single_camera(
                frame,
                metadata,
                stride=STRIDE,
                max_depth=MAX_DEPTH,
            )

            if DEBUG:
                points_camera = result["camera_points"]
                points_world = result["world_points"]

                print(f"\n--- Camera {camera_id} projection check ---")

                # Inspect points from the left, center, and right of the image.
                sample_indices = [
                    0,
                    len(points_camera) // 2,
                    len(points_camera) - 1,
                ]

                for index in sample_indices:
                    print(
                        f"Index {index}: "
                        f"camera={points_camera[index].round(3)}, "
                        f"world={points_world[index].round(3)}"
                    )

            points_world = result["world_points"]
            colors = result["colors"]

            if len(points_world):
                all_world_points.append(points_world)
                if colors is not None:
                    all_colors.append(colors)

            # camera_position_from_metadata converts Unity → Open3D (Z-flip).
            camera_positions.append(camera_position_from_metadata(metadata))

            if DEBUG:
                print_camera_summary(camera_id, frame, metadata, result)

        if not all_world_points:
            raise RuntimeError("No valid points were generated by any camera.")

        fused_points = np.concatenate(all_world_points, axis=0)
        fused_colors = (
            np.concatenate(all_colors, axis=0)
            if len(all_colors) == len(all_world_points)
            else None
        )

        if DEBUG:
            print(f"Total points before fusion: {sum(len(p) for p in all_world_points)}")
            print(f"Fused point array shape: {fused_points.shape}")

        visualize_fused_point_cloud(
            points=fused_points,
            colors=fused_colors,
            camera_positions=camera_positions,
        )

    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(run_test())
