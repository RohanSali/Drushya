import asyncio
import time
import cv2
import numpy as np

from websocket.server import start_server, camera_frames, camera_metadata
from processing.pipeline import reconstruct_single_camera
from cameras.display import (
    build_dashboard,
    render_point_cloud_preview,
    draw_placeholder,
)
from config.settings import FRAME_WIDTH, FRAME_HEIGHT


TARGET_CAMERA_IDS = [0, 1, 2, 3]
POINT_STRIDE = 3
MAX_DEPTH = 50.0
DASHBOARD_WIDTH = 1540
DASHBOARD_HEIGHT = 800
PROCESS_EVERY_SECONDS = 0.01


def snapshot_latest_frames():
    """Copy the current frame references so one processing pass uses a stable snapshot."""
    frames = {}
    metadata = {}
    for camera_id in TARGET_CAMERA_IDS:
        frame = camera_frames.get(camera_id)
        info = camera_metadata.get(camera_id)
        if frame is not None and info is not None:
            frames[camera_id] = frame
            metadata[camera_id] = info
    return frames, metadata


def frame_signature(frames):
    return tuple(
        (camera_id, frames[camera_id]["frame_id"])
        for camera_id in sorted(frames)
    )


def reconstruct_snapshot(frames, metadata):
    """Reconstruct each available camera cloud and concatenate world-space points."""
    point_arrays = []
    color_arrays = []
    summaries = {}

    for camera_id in TARGET_CAMERA_IDS:
        if camera_id not in frames or camera_id not in metadata:
            continue

        result = reconstruct_single_camera(
            frames[camera_id],
            metadata[camera_id],
            stride=POINT_STRIDE,
            max_depth=MAX_DEPTH,
        )

        points = result["world_points"]
        colors = result["colors"]
        if len(points):
            point_arrays.append(points)
            if colors is not None:
                color_arrays.append(colors)

        summaries[camera_id] = {
            "frame_id": frames[camera_id]["frame_id"],
            "point_count": len(points),
        }

    if not point_arrays:
        return np.empty((0, 3)), None, summaries

    fused_points = np.concatenate(point_arrays, axis=0)
    fused_colors = (
        np.concatenate(color_arrays, axis=0)
        if len(color_arrays) == len(point_arrays)
        else None
    )
    return fused_points, fused_colors, summaries


async def main():
    server_task = asyncio.create_task(start_server())
    window_name = "Drushya - Real-Time Monitor"
    last_signature = None
    fused_points = np.empty((0, 3), dtype=np.float32)
    fused_colors = None
    summaries = {}
    fps_start = time.perf_counter()
    displayed_frames = 0
    fps = 0.0

    print("Drushya real-time monitor starting.")
    print("Waiting for Unity cameras 0, 1, 2, and 3...")
    print("Press Q or Esc in the dashboard window to exit.")

    try:
        while True:
            frames, metadata = snapshot_latest_frames()

            if frames:
                signature = frame_signature(frames)
                if signature != last_signature and len(frames) == len(TARGET_CAMERA_IDS):
                    # Keep the WebSocket event loop responsive while CPU-heavy point-cloud generation runs in a worker thread.
                    fused_points, fused_colors, summaries = await asyncio.to_thread(
                        reconstruct_snapshot, frames, metadata
                    )
                    last_signature = signature

            camera_panel = build_dashboard(
                frames=frames,
                target_camera_ids=TARGET_CAMERA_IDS,
                width=DASHBOARD_WIDTH // 2,
                height=DASHBOARD_HEIGHT // 2,
            )

            if len(fused_points):
                cloud_panel = render_point_cloud_preview(
                    fused_points,
                    fused_colors,
                    width=DASHBOARD_WIDTH // 2,
                    height=DASHBOARD_HEIGHT // 2,
                )
            else:
                cloud_panel = draw_placeholder(
                    DASHBOARD_WIDTH // 2,
                    DASHBOARD_HEIGHT // 2,
                    "Fused point cloud",
                    "Waiting for all camera feeds...",
                )

            world_panel = draw_placeholder(
                DASHBOARD_WIDTH // 2,
                DASHBOARD_HEIGHT // 2,
                "Generated 3D World",
                "Future stage: object-based scene generation",
            )
            heatmap_panel = draw_placeholder(
                DASHBOARD_WIDTH // 2,
                DASHBOARD_HEIGHT // 2,
                "3D Spatial Heatmap",
                "Future stage: coverage / confidence visualization",
            )

            dashboard = np.vstack((
                np.hstack((camera_panel, cloud_panel)),
                np.hstack((world_panel, heatmap_panel)),
            ))

            displayed_frames += 1
            elapsed = time.perf_counter() - fps_start
            if elapsed >= 1.0:
                fps = displayed_frames / elapsed
                displayed_frames = 0
                fps_start = time.perf_counter()

            status = (
                f"Display FPS: {fps:.1f} | "
                f"Cameras ready: {len(frames)}/{len(TARGET_CAMERA_IDS)} | "
                f"Fused points: {len(fused_points)}"
            )
            cv2.putText(
                dashboard, status, (12, DASHBOARD_HEIGHT - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 230, 230), 1,
                cv2.LINE_AA,
            )

            cv2.imshow(window_name, dashboard)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break

            await asyncio.sleep(PROCESS_EVERY_SECONDS)

    finally:
        cv2.destroyAllWindows()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        print("Drushya real-time monitor stopped.")


if __name__ == "__main__":
    asyncio.run(main())