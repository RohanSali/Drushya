import cv2
import numpy as np


def calculate_intrinsics(width, height, vertical_fov_degrees):
    """
    Calculate the intrinsic matrix from image size and vertical FOV.

    Assumes:
        - Square pixels
        - No lens shift
        - No custom projection matrix
        - Principal point at the image center
    """

    fov_rad = np.deg2rad(vertical_fov_degrees)

    fy = (height / 2.0) / np.tan(fov_rad / 2.0)

    fx = fy    # Square pixels: horizontal and vertical focal lengths are equal.
    
    cx = width / 2.0
    cy = height / 2.0

    return np.array(
        [
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def build_camera_to_world(position, right, up, forward):
    """
    Build a 4x4 camera-to-world homogeneous transformation matrix.

    position, right, up, forward are 3-element vectors
    expressed in Unity world coordinates.

    The rotation part is laid out as column vectors:
        R = [right | up | forward]
    so that for a camera-space point p_c = (x, y, z):
        p_unity_world = R @ p_c + position
    where camera space is Unity convention (+X right, +Y up, +Z forward).
    """

    position = np.asarray(position, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)
    forward = np.asarray(forward, dtype=np.float64)

    transform = np.eye(4, dtype=np.float64)
    transform[:3, :3] = np.column_stack((right, up, forward))
    transform[:3, 3] = position

    return transform


def camera_points_to_world(points_camera, transform):
    """
    Transform an Nx3 array of camera-space points into world coordinates,
    then convert from Unity's left-handed world space to the right-handed
    coordinate system used by Open3D and standard computer-vision tools.

    Coordinate system conventions:
        Unity world:  LEFT-HANDED  — +X right, +Y up, +Z forward (into scene)
        Open3D world: RIGHT-HANDED — +X right, +Y up, +Z toward viewer

    X and Y are identical in both systems; only Z must be negated to flip
    the handedness.  Without this conversion, the reconstructed scene is
    mirrored (text appears backwards, walls appear on opposite sides).

    Args:
        points_camera: Nx3 array using +X right, +Y up, +Z forward (Unity
                       camera space, as produced by depth_to_point_cloud).
        transform: 4x4 camera-to-world transformation matrix built from
                   Unity world-space right / up / forward vectors.

    Returns:
        Nx3 array of world-space points in right-handed (Open3D) coordinates.
    """
    points_camera = np.asarray(points_camera, dtype=np.float64)

    if points_camera.ndim != 2 or points_camera.shape[1] != 3:
        raise ValueError("points_camera must have shape (N, 3)")

    rotation = transform[:3, :3]
    translation = transform[:3, 3]

    # Step 1: transform into Unity world space (left-handed).
    unity_world = (rotation @ points_camera.T).T + translation

    # Step 2: flip Z to convert Unity left-handed → Open3D right-handed.
    # X (right) and Y (up) are identical in both systems; only Z differs.
    unity_world[:, 2] *= -1

    return unity_world


def unity_position_to_open3d(position):
    """
    Convert a single Unity world-space position (left-handed) to the
    right-handed coordinate system used by Open3D.

    Args:
        position: array-like of shape (3,) — [x, y, z] in Unity world space.

    Returns:
        np.ndarray of shape (3,) with Z negated.
    """
    pos = np.asarray(position, dtype=np.float64).copy()
    pos[2] *= -1
    return pos


def depth_to_point_cloud(
    depth_frame,
    intrinsic_matrix,
    rgb_frame=None,
    stride=2,
    max_depth=50.0,
):
    """
    Convert a depth image into a 3D point cloud in Unity camera space.

    The output coordinate system matches Unity camera convention:
        +X = right  (pixel columns increasing to the right)
        +Y = up     (rows decrease upward — achieved by the (cy - v) flip)
        +Z = forward (depth along the optical axis)

    Parameters -
        depth_frame : Float depth map of shape (height, width).
        intrinsic_matrix : Camera intrinsic matrix K, shape (3, 3).
        rgb_frame : Optional OpenCV BGR image of shape (height, width, 3).
        stride : Pixel sampling interval. stride=2 processes every second pixel in each direction.
        max_depth : Ignore points farther than this distance.

    Returns -
        points : 3D points with shape (N, 3).
        colors : RGB colors normalized to [0, 1], shape (N, 3).
    """
    depth = np.asarray(depth_frame, dtype=np.float32)

    if depth.ndim != 2:
        raise ValueError("Depth frame must be a 2D array.")
    if stride < 1:
        raise ValueError("Stride must be at least 1.")

    height, width = depth.shape
    if rgb_frame is not None and rgb_frame.shape[:2] != (height, width):
        raise ValueError("RGB and depth resolutions must match.")

    fx = intrinsic_matrix[0, 0]
    fy = intrinsic_matrix[1, 1]
    cx = intrinsic_matrix[0, 2]
    cy = intrinsic_matrix[1, 2]

    sampled_depth = depth[::stride, ::stride]
    v, u = np.indices(sampled_depth.shape)
    u = u * stride
    v = v * stride

    valid = (
        np.isfinite(sampled_depth)
        & (sampled_depth > 0)
        & (sampled_depth <= max_depth)
    )

    u = u[valid].astype(np.float32)
    v = v[valid].astype(np.float32)
    z = sampled_depth[valid]

    x = (u - cx) * z / fx
    # (cy - v) flips the image Y axis so that +Y points up, matching Unity
    # camera space (where +Y is up, not down as in standard OpenCV convention).
    y = (cy - v) * z / fy
    points = np.column_stack((x, y, z))

    colors = None
    if rgb_frame is not None:
        sampled_rgb = cv2.cvtColor(
            rgb_frame[::stride, ::stride],
            cv2.COLOR_BGR2RGB,
        )
        colors = sampled_rgb[valid].astype(np.float32) / 255.0

    return points, colors
