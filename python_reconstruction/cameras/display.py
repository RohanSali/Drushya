import cv2
import numpy as np

# Theme
FONT = cv2.FONT_HERSHEY_SIMPLEX

BG = (26, 23, 21)          # window / gaps between panels
SURFACE = (36, 32, 29)     # placeholder panel body
HEADER = (46, 42, 38)      # panel header strip
BORDER = (78, 72, 66)      # panel / tile outlines
ACCENT = (255, 178, 80)    # blue accent
TEXT = (236, 233, 230)     # primary text
MUTED = (160, 154, 148)    # secondary text
OK = (110, 200, 110)       # "live" indicator
WARN = (60, 170, 240)      # "waiting" indicator
CLOUD_BG = (255, 255, 255) # point-cloud canvas (white)
TILE_BG = (14, 13, 12)     # letterbox colour behind camera frames

HEADER_H = 26
GAP = 4


# Drawing helpers
def _fit_frame(frame, width, height):
    """Resize a frame to fit a panel while preserving aspect ratio."""
    canvas = np.empty((height, width, 3), dtype=np.uint8)
    canvas[:] = TILE_BG
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


def _label(image, text, origin=(10, 24), color=TEXT, scale=0.55, thickness=1):
    """Draw text exactly once (no outline / shadow pass, so nothing looks doubled)."""
    cv2.putText(image, text, origin, FONT, scale, color, thickness, cv2.LINE_AA)


def _chip(image, text, origin, scale=0.45, fg=TEXT, bg=(15, 14, 13),
          alpha=0.72, dot=None):
    """
    Draw text on a semi-transparent rounded-looking badge.
    `origin` is the top-left corner of the badge. Returns the badge width.
    """
    (tw, th), _ = cv2.getTextSize(text, FONT, scale, 1)
    pad_x, pad_y = 6, 4
    dot_w = 12 if dot is not None else 0
    w = tw + 2 * pad_x + dot_w
    h = th + 2 * pad_y

    img_h, img_w = image.shape[:2]
    x0, y0 = origin
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x0 + w, img_w), min(y0 + h, img_h)
    if xb <= xa or yb <= ya:
        return w

    roi = image[ya:yb, xa:xb]
    overlay = np.empty_like(roi)
    overlay[:] = bg
    image[ya:yb, xa:xb] = cv2.addWeighted(overlay, alpha, roi, 1.0 - alpha, 0)

    if dot is not None:
        cv2.circle(image, (x0 + pad_x + 3, y0 + h // 2), 3, dot, -1, cv2.LINE_AA)
    _label(image, text, (x0 + pad_x + dot_w, y0 + pad_y + th), color=fg, scale=scale)
    return w


def _dashed_rect(image, p1, p2, color, dash=8, gap=6):
    x1, y1 = p1
    x2, y2 = p2
    for x in range(x1, x2, dash + gap):
        xe = min(x + dash, x2)
        cv2.line(image, (x, y1), (xe, y1), color, 1, cv2.LINE_AA)
        cv2.line(image, (x, y2), (xe, y2), color, 1, cv2.LINE_AA)
    for y in range(y1, y2, dash + gap):
        ye = min(y + dash, y2)
        cv2.line(image, (x1, y), (x1, ye), color, 1, cv2.LINE_AA)
        cv2.line(image, (x2, y), (x2, ye), color, 1, cv2.LINE_AA)


def _panel_header(panel, title, subtitle=None, tag=None, tag_color=MUTED, tag_dot=None):
    """
    Title strip used by every panel (same height, font and accent bar).
    `tag` is small right-aligned status text; `tag_dot` adds a status dot before it.
    """
    width = panel.shape[1]
    cv2.rectangle(panel, (1, 1), (width - 2, HEADER_H), HEADER, -1)
    cv2.line(panel, (1, HEADER_H), (width - 2, HEADER_H), BORDER, 1)

    ty = HEADER_H // 2 + 6
    _label(panel, title, (6, ty), color=TEXT, scale=0.5)
    if subtitle:
        tw = cv2.getTextSize(title, FONT, 0.5, 1)[0][0]
        _label(panel, subtitle, (12 + tw + 10, ty), color=MUTED, scale=0.4)

    if tag:
        tw = cv2.getTextSize(tag, FONT, 0.4, 1)[0][0]
        x = width - tw - 10
        _label(panel, tag, (x, ty), color=tag_color, scale=0.4)
        if tag_dot is not None:
            cv2.circle(panel, (x - 9, HEADER_H // 2 + 1), 3, tag_dot, -1, cv2.LINE_AA)
    return HEADER_H


# Panels
def build_dashboard(frames, target_camera_ids, width, height):
    """Build the first dashboard panel: a 2x2 grid of latest RGB camera frames."""
    panel = np.empty((height, width, 3), dtype=np.uint8)
    panel[:] = BG
    cv2.rectangle(panel, (0, 0), (width - 1, height - 1), BORDER, 1)

    live = sum(1 for cid in target_camera_ids if frames.get(cid))
    total = len(target_camera_ids)
    _panel_header(
        panel, "Camera Feeds", "RGB",
        tag=f"{live}/{total} online",
        tag_color=TEXT if live == total else MUTED,
        tag_dot=OK if live == total else WARN,
    )

    top = HEADER_H + 1 + GAP
    cell_w = (width - GAP * 3) // 2
    cell_h = (height - top - GAP * 2) // 2

    for index, camera_id in enumerate(target_camera_ids):
        row, col = divmod(index, 2)
        x = GAP + col * (cell_w + GAP)
        y = top + row * (cell_h + GAP)
        frame_record = frames.get(camera_id)
        frame = frame_record["rgb"] if frame_record else None
        fitted = _fit_frame(frame, cell_w, cell_h)
        panel[y:y + cell_h, x:x + cell_w] = fitted
        cv2.rectangle(panel, (x, y), (x + cell_w - 1, y + cell_h - 1), BORDER, 1)

        if frame_record:
            _chip(panel, f"Camera {camera_id}  |  Frame {frame_record['frame_id']}",
                  (x + 6, y + 6), dot=OK)
        else:
            _chip(panel, f"Camera {camera_id}  |  Waiting...", (x + 6, y + 6), dot=WARN)
            msg = "No signal"
            (tw, th), _ = cv2.getTextSize(msg, FONT, 0.55, 1)
            _label(panel, msg, (x + (cell_w - tw) // 2, y + (cell_h + th) // 2),
                   color=MUTED, scale=0.55)

    return panel


def draw_placeholder(width, height, title, message):
    """Render a panel reserved for a future application stage."""
    panel = np.empty((height, width, 3), dtype=np.uint8)
    panel[:] = SURFACE
    cv2.rectangle(panel, (0, 0), (width - 1, height - 1), BORDER, 1)
    _panel_header(panel, title, tag="Coming soon", tag_color=ACCENT)

    # Reserved-slot outline (kept clear of the status text drawn at the bottom).
    left, top, right, bottom = 12, HEADER_H + 12, width - 12, height - 30
    _dashed_rect(panel, (left, top), (right, bottom), BORDER)

    # Word-wrap using real text metrics so lines never overflow.
    max_w = (right - left) - 40
    lines, current = [], ""
    for word in message.split():
        candidate = f"{current} {word}".strip()
        if cv2.getTextSize(candidate, FONT, 0.55, 1)[0][0] > max_w and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    line_h = 28
    y = (top + bottom) // 2 - (len(lines) - 1) * line_h // 2 + 5
    for line in lines:
        tw = cv2.getTextSize(line, FONT, 0.55, 1)[0][0]
        _label(panel, line, ((width - tw) // 2, y), color=MUTED, scale=0.55)
        y += line_h
    return panel


# Cache so an unchanged cloud isn't re-projected on every display tick.
_cloud_cache = {"key": None, "panel": None}


def render_point_cloud_preview(points, colors=None, width=640, height=450):
    """
    Render a stable isometric 2D preview of a 3D point cloud using OpenCV.

    This keeps the dashboard in one window. It is a preview projection, not
    an interactive 3D viewport; the underlying points remain 3D coordinates.
    """
    # Cheap identity-based cache key (main.py only swaps the array on new data).
    try:
        key = (
            id(points), id(colors), len(points), width, height,
            np.asarray(points[0]).tobytes() if len(points) else b"",
            np.asarray(points[-1]).tobytes() if len(points) else b"",
        )
    except Exception:
        key = None
    if key is not None and key == _cloud_cache["key"]:
        return _cloud_cache["panel"]

    panel = np.empty((height, width, 3), dtype=np.uint8)
    panel[:] = CLOUD_BG
    cv2.rectangle(panel, (0, 0), (width - 1, height - 1), BORDER, 1)
    points = np.asarray(points, dtype=np.float32)
    n_valid = len(points) if (points.ndim == 2 and points.shape[1] == 3) else 0
    _panel_header(
        panel, "Fused Point Cloud", "isometric preview",
        tag=f"{n_valid:,} pts" if n_valid else "no data",
        tag_dot=OK if n_valid else WARN,
    )

    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        msg = "Waiting for valid points"
        tw = cv2.getTextSize(msg, FONT, 0.6, 1)[0][0]
        _label(panel, msg, ((width - tw) // 2, height // 2), color=(120, 120, 120), scale=0.6)
        return panel

    # Fixed isometric-like view: rotate world coordinates for display only.
    yaw = np.deg2rad(42.0)
    pitch = np.deg2rad(25.0)
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    rotation_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    rotation_x = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)
    rotation = rotation_x @ rotation_y
    view = (rotation @ (points - points.mean(axis=0)).T).T

    # Map view coordinates to pixels, centred inside the area under the header.
    xy = view[:, :2]
    mins = xy.min(axis=0)
    span = np.ptp(xy, axis=0)
    span[span < 1e-5] = 1.0
    margin_x, margin_top, margin_bottom = 20, HEADER_H + 12, 24
    avail_w = width - 2 * margin_x
    avail_h = height - margin_top - margin_bottom
    scale = min(avail_w / span[0], avail_h / span[1])
    off_x = margin_x + (avail_w - span[0] * scale) / 2.0
    base_y = height - margin_bottom - (avail_h - span[1] * scale) / 2.0
    px = ((xy[:, 0] - mins[0]) * scale + off_x).astype(np.int32)
    py = (base_y - (xy[:, 1] - mins[1]) * scale).astype(np.int32)

    if colors is not None and len(colors) == len(points):
        rgb = np.clip(np.asarray(colors) * 255.0, 0, 255).astype(np.uint8)
        bgr = rgb[:, ::-1]
    else:
        bgr = np.tile(np.array([[190, 150, 95]], dtype=np.uint8), (len(points), 1))

    # Subtle depth cueing: points closer to the viewer are brighter.
    depth = view[:, 2]
    dz = float(depth.max() - depth.min())
    if dz > 1e-6:
        shade = 0.6 + 0.4 * (depth - depth.min()) / dz
        bgr = (bgr.astype(np.float32) * shade[:, None]).astype(np.uint8)

    # Back-to-front, vectorised, with a 2x2 splat so the cloud reads as solid.
    valid = (px >= 0) & (px < width - 1) & (py >= 0) & (py < height - 1)
    order = np.argsort(depth)
    order = order[valid[order]]
    px_o, py_o, col_o = px[order], py[order], bgr[order]
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        panel[py_o + dy, px_o + dx] = col_o

    # Axis gizmo (bottom-right), drawn with the same rotation as the cloud.
    gx, gy, glen = width - 44, height - 30, 22
    for axis, color, name in (
        (np.array([1, 0, 0], np.float32), (90, 90, 240), "X"),
        (np.array([0, 1, 0], np.float32), (110, 210, 110), "Y"),
        (np.array([0, 0, 1], np.float32), (250, 160, 80), "Z"),
    ):
        v = rotation @ axis
        end = (int(gx + v[0] * glen), int(gy - v[1] * glen))
        cv2.line(panel, (gx, gy), end, color, 2, cv2.LINE_AA)
        _label(panel, name, (end[0] + 4, end[1] + 4), color=color, scale=0.4)

    if key is not None:
        _cloud_cache["key"] = key
        _cloud_cache["panel"] = panel
    return panel


def display_frame(camera_id, frame):
    """Legacy single-camera preview helper; the real-time dashboard uses build_dashboard."""
    if frame is None:
        return
    cv2.imshow(f"Camera {camera_id}", frame)
    cv2.waitKey(1)