import math
import numpy as np
import open3d as o3d

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