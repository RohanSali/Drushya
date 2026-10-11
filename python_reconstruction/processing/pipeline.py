import numpy as np
import open3d as o3d

from processing.helpers import (
    calculate_intrinsics,
    depth_to_point_cloud,
)


def test_single_camera(rgbd_frame, camera_metadata):
    """
    Test RGB-D to 3D point conversion for one camera.
    """

    rgb_frame = rgbd_frame["rgb"]
    depth_frame = rgbd_frame["depth"]

    inspect_depth_frame(depth_frame)

    width = rgb_frame.shape[1]
    height = rgb_frame.shape[0]

    # Obtain camera FOV from existing metadata
    fov = camera_metadata["fov"]

    # Calculate camera intrinsics
    K = calculate_intrinsics(
        width,
        height,
        fov
    )

    # Generate 3D points
    points, colors = depth_to_point_cloud(
        depth_frame=depth_frame,
        intrinsic_matrix=K,
        rgb_frame=rgb_frame,
        stride=2,
        max_depth=50.0
    )

    print("\n========== POINT CLOUD TEST ==========")
    print(f"Camera resolution: {width} x {height}")
    print(f"Depth shape: {depth_frame.shape}")
    print(f"Generated points: {len(points)}")

    if len(points) > 0:
        print(
            f"X range: {points[:, 0].min():.3f} "
            f"to {points[:, 0].max():.3f}"
        )

        print(
            f"Y range: {points[:, 1].min():.3f} "
            f"to {points[:, 1].max():.3f}"
        )

        print(
            f"Z range: {points[:, 2].min():.3f} "
            f"to {points[:, 2].max():.3f}"
        )

    print("======================================\n")

    return points, colors

def visualize_point_cloud(points, colors=None):
    """
    Visualize a single-camera point cloud using Open3D.

    Args:
        points: Nx3 array containing 3D point coordinates.
        colors: Optional Nx3 array containing RGB colors in [0, 1].
    """

    if points is None or len(points) == 0:
        print("[Visualization] No points available to visualize.")
        return

    # Create an Open3D point cloud
    point_cloud = o3d.geometry.PointCloud()

    # Assign 3D coordinates
    point_cloud.points = o3d.utility.Vector3dVector(
        np.asarray(points, dtype=np.float64)
    )

    # Assign RGB colors, if available
    if colors is not None:
        colors = np.asarray(colors, dtype=np.float64)

        if colors.shape != np.asarray(points).shape:
            raise ValueError(
                "Colors must have the same Nx3 shape as points."
            )

        point_cloud.colors = o3d.utility.Vector3dVector(colors)

    # Create coordinate axes at the camera origin
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=1.0,
        origin=[0.0, 0.0, 0.0]
    )

    print("\n========== OPEN3D VISUALIZATION ==========")
    print(f"Points displayed: {len(point_cloud.points)}")
    print(f"Colors available: {colors is not None}")
    print("Opening 3D visualization window...")
    print("==========================================\n")

    # Display the point cloud
    o3d.visualization.draw_geometries(
        [point_cloud, coordinate_frame],
        window_name="Drushya - Single Camera Point Cloud",
        width=1280,
        height=720
    )

    print("[Visualization] Window closed.")
    
def inspect_depth_frame(depth_frame):
    """
    Inspect depth values at selected image locations.
    """

    height, width = depth_frame.shape

    sample_points = {
        "Top-left": (height // 4, width // 4),
        "Center": (height // 2, width // 2),
        "Top-right": (height // 4, 3 * width // 4),
        "Bottom-left": (3 * height // 4, width // 4),
        "Bottom-right": (3 * height // 4, 3 * width // 4),
    }

    print("\n========== DEPTH INSPECTION ==========")

    for name, (y, x) in sample_points.items():
        print(
            f"{name:12s}: "
            f"Depth={depth_frame[y, x]:.3f}"
        )

    valid = (
        np.isfinite(depth_frame)
        & (depth_frame > 0)
    )

    if np.any(valid):
        valid_depths = depth_frame[valid]

        print(f"\nValid pixels: {valid.sum()}")
        print(f"Minimum: {valid_depths.min():.3f}")
        print(f"Maximum: {valid_depths.max():.3f}")
        print(
            f"Median:  "
            f"{np.median(valid_depths):.3f}"
        )

    print("======================================\n")