import cv2
import numpy as np


def _fit_frame(frame, width, height):
    """Resize a frame to fit a panel while preserving aspect ratio."""
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    if frame is None:
        return canvas

    frame_h, frame_w = frame.shape[:2]
    scale = min(width / frame_w, height / frame_h)
    new_w = max(1, int(frame_w * scale))
    new_h = max(1, int(frame_h * scale))
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    x = (width - new_w) // 2
    y = (height - new_h) // 2
    canvas[y:y + new_h, x:x + new_w] = resized
    return canvas


def _label(image, text, origin=(10, 24), color=(245, 245, 245), scale=0.65):
    cv2.putText(
        image, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale,
        (20, 20, 20), 3, cv2.LINE_AA,
    )
    cv2.putText(
        image, text, origin, cv2.FONT_HERSHEY_SIMPLEX, scale,
        color, 1, cv2.LINE_AA,
    )


def build_dashboard(frames, target_camera_ids, width, height):
    """Build the first dashboard panel: a 2x2 grid of latest RGB camera frames."""
    panel = np.zeros((height, width, 3), dtype=np.uint8)
    gap = 6
    cell_w = (width - gap * 3) // 2
    cell_h = (height - gap * 3) // 2

    for index, camera_id in enumerate(target_camera_ids):
        row, col = divmod(index, 2)
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + gap)
        frame_record = frames.get(camera_id)
        frame = frame_record["rgb"] if frame_record else None
        fitted = _fit_frame(frame, cell_w, cell_h)
        panel[y:y + cell_h, x:x + cell_w] = fitted

        if frame_record:
            label = f"Camera {camera_id} | Frame {frame_record['frame_id']}"
        else:
            label = f"Camera {camera_id} | Waiting..."
        _label(panel, label, (x + 8, y + 23))

    return panel


def draw_placeholder(width, height, title, message):
    """Render a panel reserved for a future application stage."""
    panel = np.full((height, width, 3), 34, dtype=np.uint8)
    cv2.rectangle(panel, (1, 1), (width - 2, height - 2), (90, 90, 90), 1)
    _label(panel, title, (18, 34), scale=0.8)
    lines = []
    words = message.split()
    current = ""
    max_chars = max(20, width // 11)
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    y = height // 2
    for line in lines:
        text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)[0]
        x = max(12, (width - text_size[0]) // 2)
        _label(panel, line, (x, y), color=(170, 190, 205), scale=0.55)
        y += 28
    return panel


def render_point_cloud_preview(points, colors=None, width=640, height=450):
    """
    Render a stable isometric 2D preview of a 3D point cloud using OpenCV.

    This keeps the dashboard in one window. It is a preview projection, not
    an interactive 3D viewport; the underlying points remain 3D coordinates.
    """
    panel = np.full((height, width, 3), 248, dtype=np.uint8)
    cv2.rectangle(panel, (1, 1), (width - 2, height - 2), (210, 210, 210), 1)
    _label(panel, "Fused Point Cloud (isometric preview)", (12, 25), color=(55, 55, 55), scale=0.58)

    points = np.asarray(points, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        _label(panel, "Waiting for valid points", (20, height // 2), color=(70, 70, 70))
        return panel

    # Fixed isometric-like view: rotate world coordinates for display only.
    yaw = np.deg2rad(42.0)
    pitch = np.deg2rad(25.0)
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    rotation_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    rotation_x = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)
    view = (rotation_x @ rotation_y @ (points - points.mean(axis=0)).T).T

    # Map the view's horizontal/vertical coordinates to panel pixels.
    xy = view[:, [0, 1]]
    span = np.ptp(xy, axis=0)
    span[span < 1e-5] = 1.0
    margin_x, margin_y = 24, 48
    scale = min((width - 2 * margin_x) / span[0], (height - 2 * margin_y) / span[1])
    px = ((xy[:, 0] - xy[:, 0].min()) * scale + margin_x).astype(np.int32)
    py = (height - margin_y - (xy[:, 1] - xy[:, 1].min()) * scale).astype(np.int32)

    if colors is not None and len(colors) == len(points):
        rgb = np.clip(np.asarray(colors) * 255.0, 0, 255).astype(np.uint8)
        bgr = rgb[:, ::-1]
    else:
        bgr = np.tile(np.array([[190, 150, 95]], dtype=np.uint8), (len(points), 1))

    # Vectorized drawing keeps the preview responsive for larger clouds.
    valid_pixels = (
        (px >= 0) & (px < width) &
        (py >= 0) & (py < height)
    )
    order = np.argsort(view[:, 2])
    order = order[valid_pixels[order]]
    panel[py[order], px[order]] = bgr[order]

    _label(panel, f"Points: {len(points):,}", (12, height - 12), color=(55, 55, 55), scale=0.52)
    return panel


def display_frame(camera_id, frame):
    """Legacy single-camera preview helper; the real-time dashboard uses build_dashboard."""
    if frame is None:
        return
    cv2.imshow(f"Camera {camera_id}", frame)
    cv2.waitKey(1)