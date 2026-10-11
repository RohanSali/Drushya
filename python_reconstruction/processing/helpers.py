import math
import numpy as np
import open3d as o3d
import cv2

def calculate_intrinsics(width, height, vertical_fov_degrees):
    """
    Calculate the ideal pinhole-camera intrinsic matrix
    from image resolution and Unity's vertical FOV.
    """

    fov_y = math.radians(vertical_fov_degrees)

    fy = (height / 2.0) / math.tan(fov_y / 2.0)

    fx = fy * (width / height)

    cx = width / 2.0
    cy = height / 2.0

    K = np.array([
        [fx, 0.0, cx],
        [0.0, fy, cy],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    return K


def build_camera_to_world(position, right, up, forward):
    """
    Build a camera-to-world homogeneous transformation matrix.

    position, right, up, forward are 3-element vectors
    expressed in Unity world coordinates.
    """

    position = np.asarray(position, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)
    forward = np.asarray(forward, dtype=np.float64)

    R = np.column_stack([
        right,
        up,
        forward
    ])

    T = np.eye(4, dtype=np.float64)

    T[:3, :3] = R
    T[:3, 3] = position

    return T


def camera_to_world(point_camera, camera_to_world):
    """
    Transform a 3D camera-space point into world coordinates.
    """

    point = np.array([
        point_camera[0],
        point_camera[1],
        point_camera[2],
        1.0
    ], dtype=np.float64)

    point_world = camera_to_world @ point

    return point_world[:3]


def project_point(point_camera, K):
    """
    Project a camera-space 3D point onto the image plane.
    """

    X, Y, Z = point_camera

    if Z <= 0:
        return None

    fx = K[0, 0]
    fy = K[1, 1]

    cx = K[0, 2]
    cy = K[1, 2]

    u = fx * X / Z + cx
    v = fy * Y / Z + cy

    return np.array([u, v])


def create_camera_geometry(position, right, up, forward, scale=0.5):
    """
    Create a simple Open3D coordinate frame for a camera.
    """

    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=scale,
        origin=position
    )

    return frame

def depth_to_point_cloud(
    depth_frame,
    intrinsic_matrix,
    rgb_frame=None,
    stride=2,
    max_depth=50.0
):
    """
    Convert a depth image into a 3D point cloud.

    Parameters
    ----------
    depth_frame : np.ndarray
        Float depth map of shape (height, width).
        Depth values are in Unity world units.

    intrinsic_matrix : np.ndarray
        Camera intrinsic matrix K, shape (3, 3).

    rgb_frame : np.ndarray or None
        Optional OpenCV BGR image of shape (height, width, 3).

    stride : int
        Pixel sampling interval. stride=2 processes every
        second pixel in each direction.

    max_depth : float
        Ignore points farther than this distance.

    Returns
    -------
    points : np.ndarray
        3D points with shape (N, 3).

    colors : np.ndarray or None
        RGB colors normalized to [0, 1], shape (N, 3).
    """

    depth = np.asarray(depth_frame, dtype=np.float32)

    if depth.ndim != 2:
        raise ValueError(
            "Depth frame must be a 2D array."
        )

    if stride < 1:
        raise ValueError(
            "Stride must be at least 1."
        )

    height, width = depth.shape

    if rgb_frame is not None:
        if rgb_frame.shape[:2] != (height, width):
            raise ValueError(
                "RGB and depth resolutions must match."
            )

    # Extract camera intrinsics
    fx = intrinsic_matrix[0, 0]
    fy = intrinsic_matrix[1, 1]
    cx = intrinsic_matrix[0, 2]
    cy = intrinsic_matrix[1, 2]

    # Sample pixels
    sampled_depth = depth[::stride, ::stride]

    v, u = np.indices(sampled_depth.shape)

    u = u * stride
    v = v * stride

    # Remove invalid and excessively distant depths
    valid = (
        np.isfinite(sampled_depth)
        & (sampled_depth > 0)
        & (sampled_depth <= max_depth)
    )

    u = u[valid].astype(np.float32)
    v = v[valid].astype(np.float32)
    z = sampled_depth[valid]

    # Back-project pixels into camera-space 3D points
    x = (u - cx) * z / fx
    y = (cy - v) * z / fy

    points = np.column_stack((x, y, z))

    colors = None

    if rgb_frame is not None:
        sampled_rgb = rgb_frame[::stride, ::stride]

        # OpenCV images use BGR; Open3D expects RGB.
        sampled_rgb = cv2.cvtColor(
            sampled_rgb,
            cv2.COLOR_BGR2RGB
        )

        colors = (
            sampled_rgb[valid].astype(np.float32)
            / 255.0
        )

    return points, colors