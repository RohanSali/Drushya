import numpy as np
import open3d as o3d

from processing.helpers import (
    build_camera_to_world,
    calculate_intrinsics,
    camera_points_to_world,
    depth_to_point_cloud,
)

def get_camera_transform(camera_metadata):
    """Build a camera-to-world transform from Unity camera metadata."""

    def vector3(key):
        vector = camera_metadata[key]
        return [vector["x"], vector["y"], vector["z"]]

    transform = build_camera_to_world(
        position=vector3("position"),
        right=vector3("right"),
        up=vector3("up"),
        forward=vector3("forward"),
    )

    return transform

def reconstruct_single_camera(rgbd_frame, camera_metadata, stride=2, max_depth=50.0):
    """
    Convert one RGB-D frame into camera-space and world-space point clouds.

    Returns a dictionary containing both coordinate spaces and point colors.
    """
    rgb_frame = rgbd_frame["rgb"]
    depth_frame = rgbd_frame["depth"]

    height, width = depth_frame.shape
    fov = camera_metadata["fov"]
    
    if rgb_frame.shape[:2] != (height, width):
        raise ValueError("RGB and depth resolutions must match.")

    intrinsic_matrix = calculate_intrinsics(
        width=width,
        height=height,
        vertical_fov_degrees=fov,
    )

    points_camera, colors = depth_to_point_cloud(
        depth_frame=depth_frame,
        intrinsic_matrix=intrinsic_matrix,
        rgb_frame=rgb_frame,
        stride=stride,
        max_depth=max_depth,
    )

    transform = get_camera_transform(camera_metadata)
    points_world = camera_points_to_world(points_camera, transform)

    return {
        "camera_points": points_camera,
        "world_points": points_world,
        "colors": colors,
        "intrinsics": intrinsic_matrix,
        "camera_transform": transform,
    }


def visualize_point_cloud(points, colors=None, camera_position=None, coordinate_space="world"):
    """Display a point cloud in Open3D, optionally marking the camera position."""
    if points is None or len(points) == 0:
        raise ValueError("No points available to visualize.")

    points = np.asarray(points, dtype=np.float64)
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    if colors is not None:
        colors = np.asarray(colors, dtype=np.float64)
        if colors.shape != points.shape:
            raise ValueError("Colors must have the same Nx3 shape as points.")
        point_cloud.colors = o3d.utility.Vector3dVector(np.clip(colors, 0.0, 1.0))

    geometries = [point_cloud]

    if coordinate_space == "world":
        geometries.append(
            o3d.geometry.TriangleMesh.create_coordinate_frame(
                size=1.0,
                origin=[0.0, 0.0, 0.0],
            )
        )

        if camera_position is not None:
            camera_marker = o3d.geometry.TriangleMesh.create_sphere(radius=0.10)
            camera_marker.translate(np.asarray(camera_position, dtype=np.float64))
            camera_marker.paint_uniform_color([1.0, 0.0, 0.0])
            geometries.append(camera_marker)

    o3d.visualization.draw_geometries(
        geometries,
        window_name=f"Drushya - {coordinate_space.capitalize()}-Space Point Cloud",
        width=1280,
        height=720,
    )
