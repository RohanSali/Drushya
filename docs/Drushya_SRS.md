# Software Requirements Specification (SRS)

## Project Information

| Field | Details |
|---|---|
| Project Title | Real-Time Simplified 3D Environment Reconstruction from Multi-Camera Feeds |
| Project Name | Drushya |
| Document Type | Software Requirements Specification |
| Version | 2.0 |
| Status | Real-time multi-camera RGB-D acquisition, point-cloud generation and fusion foundation implemented; AI scene understanding and simplified world generation are the next phase |
| Last Updated | 13 November 2026 |

---

# 1. INTRODUCTION

## 1.1 Purpose

Drushya is a prototype system that observes an environment through multiple camera feeds and generates a simplified, spatially meaningful 3D representation of that environment.

The initial implementation uses a Unity-based simulated environment with four virtual RGB-D cameras. A Python application receives the camera streams, processes RGB and depth data, generates per-camera point clouds, combines observations from the cameras, and displays the live camera feeds and fused point cloud.

The next major phase moves beyond point-cloud visualization. The system will interpret information extracted from the camera observations and independently generate a simplified 3D world model. The generated model should preserve important spatial properties—such as object identity, position, dimensions, orientation and approximate color—without reproducing every surface detail.

The objective is not photorealistic reconstruction or a pixel-perfect digital twin. It is a lightweight, understandable 3D representation that captures the important structure of the observed environment.

## 1.2 Scope

### Implemented foundation

- Create and configure a Unity simulation environment.
- Place four virtual RGB-D cameras around the environment.
- Capture RGB frames, depth frames and camera metadata.
- Stream camera data from Unity to Python using WebSocket communication.
- Receive and decode continuous camera data.
- Calculate camera intrinsics from configured camera parameters.
- Interpret camera extrinsics and Unity world-coordinate conventions.
- Convert RGB-D frames into individual camera point clouds.
- Use spatial calibration to relate observations from different cameras.
- Combine point-cloud observations from the four cameras.
- Display four camera feeds and the fused point cloud in a live 2×2 monitoring window.
- Continuously update the display as new frames arrive.

### Planned AI-assisted scene understanding and world generation

- Detect relevant objects and structural regions in camera images.
- Extract geometric and semantic information from RGB-D observations.
- Identify major environmental structures such as floors and walls.
- Estimate object positions, dimensions and orientations.
- Estimate a representative, preferably uniform, color for each reconstructed object.
- Associate observations of the same object across different cameras.
- Combine multi-camera evidence into a consistent scene description.
- Generate a new, simplified 3D environment from the extracted information.
- Update the generated environment as new observations are processed.
- Develop a 3D-world heatmap or spatial-confidence visualization.
- Evaluate the generated model against the Unity source scene.

### Out of scope for the current prototype

- Photorealistic reconstruction.
- Pixel-perfect texture reproduction.
- Exact digital-twin generation.
- Physical camera deployment in the current implementation.
- Autonomous control of physical machines.
- Full semantic understanding of every possible object.
- Object manipulation or command execution through the viewer.
- Production-scale deployment.

## 1.3 Intended Users

- Project developer and researcher.
- Engineering students working in computer vision, AI and 3D reconstruction.
- Researchers experimenting with multi-camera perception.
- Future users of environment-monitoring and spatial-understanding systems.

## 1.4 Definitions and Acronyms

| Term | Meaning |
|---|---|
| RGB | Red, Green and Blue image data |
| RGB-D | RGB image accompanied by depth information |
| Point cloud | A collection of 3D points representing observed surfaces |
| Camera intrinsics | Internal camera parameters, including focal lengths and principal point |
| Camera extrinsics | Camera position and orientation relative to a reference coordinate system |
| FOV | Field of View |
| WebSocket | Communication protocol used for continuous data exchange |
| Scene understanding | Extraction of structural, geometric and semantic information from observations |
| Scene representation | Structured description of the objects and geometry in the environment |
| World generation | Creation of a new simplified 3D scene using the extracted scene representation |
| Near real-time | Continuous processing and updates with a delay suitable for monitoring and understanding scene changes |
| FPS | Frames Per Second |
| YOLO | You Only Look Once, a family of object-detection models |
| ICP | Iterative Closest Point, an algorithm used for point-cloud registration |

---

# 2. OVERALL DESCRIPTION

## 2.1 Product Perspective

Drushya consists of four logical layers:

1. **Simulation and Camera Layer** – Unity generates the environment and provides RGB-D observations from four virtual cameras.
2. **Data Acquisition and Perception Layer** – Python receives the streams and extracts visual and geometric information.
3. **Scene Understanding and World Generation Layer** – AI and geometric processing combine extracted information into a structured scene description and generate a simplified 3D world.
4. **Monitoring and Visualization Layer** – A live dashboard presents camera feeds, point-cloud observations, the generated world and, later, a spatial heatmap.

### High-Level Architecture

```text
+------------------------------------------------------+
|                 UNITY SIMULATION                     |
|       Environment + Objects + Four RGB-D Cameras     |
+----------------------------+-------------------------+
                             | RGB + Depth + Metadata
                             v
+------------------------------------------------------+
|           PYTHON DATA ACQUISITION LAYER               |
|       WebSocket Receiver | Frame Handling            |
+----------------------------+-------------------------+
                             v
+------------------------------------------------------+
|             PERCEPTION / GEOMETRY LAYER               |
| RGB-D Processing | Calibration | Point Clouds        |
|             Multi-Camera Observation Fusion           |
+----------------------------+-------------------------+
                             v
+------------------------------------------------------+
|          AI SCENE UNDERSTANDING LAYER                 |
| Object Detection | Structural Detection               |
| Depth Association | Geometry Estimation               |
| Multi-View Association | Scene Information            |
+----------------------------+-------------------------+
                             v
+------------------------------------------------------+
|             WORLD GENERATION LAYER                    |
| Structured Scene Description | Simplified Geometry   |
|             Generated 3D Environment                  |
+----------------------------+-------------------------+
                             v
+------------------------------------------------------+
|             MONITORING / VISUALIZATION                |
| Camera Feeds | Fused Point Cloud                      |
| Generated 3D World | 3D Spatial Heatmap              |
+------------------------------------------------------+
```

The point cloud is an intermediate observation and geometric-evidence source. It is not intended to be the final reconstructed world.

## 2.2 Simulation Environment

Unity acts as the initial source environment. It contains a configurable room or scene with elements such as floors, walls, tables, platforms, cubes, boxes, cylinders and optional moving objects. Four virtual cameras observe the scene from different directions.

The Unity scene provides known geometry and camera parameters, making it suitable for validating the perception and reconstruction pipeline before moving to physical cameras.

## 2.3 Camera Configuration and Naming Convention

The four cameras use fixed IDs and directional names:

| Camera ID | Camera Name | Direction Faced | Unity Forward Direction |
|---:|---|---|---|
| 0 | North | North | +Z |
| 1 | East | East | +X |
| 2 | South | South | −Z |
| 3 | West | West | −X |

A camera name describes the direction in which the camera is looking, not the side of the room on which it is mounted.

Each camera provides its ID, position, rotation, forward/right/up direction vectors, image dimensions, field of view, RGB frame and depth frame. Python must identify cameras by camera ID rather than assuming metadata or frames always arrive in numerical order.

## 2.4 Reconstruction Philosophy

Drushya follows an **observation → understanding → generation** approach.

It does not simply combine all camera point clouds and treat the resulting points as the final 3D world.

1. Each camera observes a portion of the environment.
2. RGB and depth data provide visual and geometric evidence.
3. Point clouds provide 3D measurements of observed surfaces.
4. Perception algorithms extract useful information from these observations.
5. Information from different cameras is associated and combined.
6. A structured description of the environment is produced.
7. The system generates its own simplified 3D world using that description.

For example, if the cameras collectively observe a room containing four walls and a cube near its centre, the system should infer the walls and cube, estimate their positions, orientations, dimensions and representative colors, and then create a new simplified room and cube from those properties. It does not need to reproduce the original meshes, textures or every point captured by the cameras.

| Point-cloud observation | Generated world |
|---|---|
| Dense set of measured 3D points | Small set of meaningful objects and surfaces |
| Directly derived from camera depth | Constructed from interpreted scene information |
| May contain noise, redundancy and incomplete surfaces | Intended to be cleaner, simpler and spatially consistent |
| Intermediate representation for inspection and analysis | Main intended reconstruction output |

A shared coordinate reference may be used to compare observations and estimate where objects and surfaces belong. This does not make the fused point cloud the final world model.

## 2.5 Current Dashboard Concept

The application uses a single monitoring window arranged as a 2×2 grid.

| Panel | Content | Status |
|---|---|---|
| 1 | Four live camera feeds | Implemented |
| 2 | Current fused point cloud | Implemented |
| 3 | Generated simplified 3D world | Future development |
| 4 | 3D-world heatmap / spatial-confidence view | Future development |

At the current stage, the first two panels are active. The remaining panels are reserved for the AI and world-generation phase. The point-cloud view is a monitoring view; the underlying data and display should continue updating as new observations are processed.

---

# 3. SYSTEM OBJECTIVES

1. Maintain a working four-camera RGB-D simulation.
2. Receive continuous camera data in Python.
3. Generate point clouds from RGB-D observations.
4. Combine observations from multiple cameras using consistent calibration and spatial references.
5. Provide a live monitoring interface for camera feeds and fused point clouds.
6. Develop AI-assisted object and structural perception.
7. Extract approximate 3D properties from camera observations.
8. Associate observations of the same structure or object across cameras.
9. Generate a simplified 3D environment independently of the source scene's detailed geometry.
10. Update the generated world as the observed environment changes.
11. Provide visual tools to inspect reconstruction quality and spatial confidence.
12. Keep the architecture modular so Unity cameras can eventually be replaced by physical camera sources.

---

# 4. FUNCTIONAL REQUIREMENTS

## 4.1 Completed Foundation Requirements

- **FR-01: Unity Environment.** The system shall use a Unity scene as the initial simulated environment.
- **FR-02: Four-Camera Configuration.** The system shall support four cameras with the fixed North, East, South and West ID convention.
- **FR-03: RGB Capture.** Each camera shall provide an RGB frame.
- **FR-04: Depth Capture.** Each camera shall provide a depth frame suitable for metric 3D point generation.
- **FR-05: Camera Metadata.** The system shall transmit camera ID, position, orientation/direction vectors, resolution and field of view.
- **FR-06: Continuous Data Transfer.** Unity shall stream camera data to Python using WebSocket communication.
- **FR-07: Frame Reception and Decoding.** Python shall receive and decode RGB-D frames and associate them with the correct camera.
- **FR-08: Camera Calibration.** The system shall calculate or obtain camera intrinsics and use supplied extrinsics.
- **FR-09: Point-cloud Generation.** The system shall generate a colored point cloud from each camera's RGB-D observation.
- **FR-10: Multi-Camera Fusion.** The system shall combine observations from the configured cameras using calibration and spatial information.
- **FR-11: Live Monitoring.** The system shall continuously update the camera-feed and fused-point-cloud panels as new frames are received.

## 4.2 Scene Understanding Requirements — Next Development Phase

- **FR-12: Object Detection.** Detect relevant objects in RGB camera frames using a suitable computer-vision or AI model.
- **FR-13: Structural Region Detection.** Identify major environmental structures such as floors, walls and large planar surfaces.
- **FR-14: Depth Association.** Associate detected image regions with corresponding depth measurements or 3D observations.
- **FR-15: Geometric Property Estimation.** Estimate approximate 3D position, dimensions and orientation of detected objects and structures.
- **FR-16: Representative Color Estimation.** Estimate a representative color for each reconstructed object or structural element. The initial model may use one uniform color per object rather than detailed textures.
- **FR-17: Multi-Camera Observation Association.** Identify and combine observations that refer to the same object or structure across camera views.
- **FR-18: Scene Information Generation.** Produce a structured representation containing object classes, spatial properties and appearance information.
- **FR-19: Spatial Consistency.** Use calibration and multi-view evidence to reduce duplicate objects and improve consistency of estimated positions and dimensions.

## 4.3 World Generation Requirements — Planned

- **FR-20: Simplified Geometry Generation.** Generate a new 3D scene using the structured scene representation.
- **FR-21: Primitive-Based Representation.** Where appropriate, represent structures and objects using simple primitives such as planes, cuboids and cylinders.
- **FR-22: Independent Scene Construction.** Construct the generated scene from extracted scene information rather than copying the original Unity geometry or displaying the fused point cloud as the final result.
- **FR-23: Approximate Appearance.** Use representative colors and simple materials. Detailed texture reproduction is not required.
- **FR-24: Continuous World Updates.** Update the generated scene when sufficiently meaningful changes are detected in incoming observations.
- **FR-25: Spatial Heatmap.** Provide a 3D heatmap or equivalent visualization for selected spatial information, such as observation coverage, confidence or reconstruction uncertainty. Its exact meaning and encoding will be finalized during implementation.

## 4.4 Dashboard and Monitoring Requirements

- **FR-26: Four-Panel Dashboard.** Provide a single 2×2 monitoring window.
- **FR-27: Camera Feed Panel.** The first panel shall display the four camera feeds.
- **FR-28: Fused Point-cloud Panel.** The second panel shall display the current fused point cloud.
- **FR-29: Generated World Panel.** The third panel shall display the generated simplified 3D world when implemented.
- **FR-30: Heatmap Panel.** The fourth panel shall display the 3D-world heatmap when implemented.
- **FR-31: Processing Statistics.** Expose useful information such as frame IDs, camera availability, processing time, point count, update rate and errors.
- **FR-32: Graceful Frame Handling.** A missing or delayed camera frame shall not unnecessarily stop processing of other available cameras.

---

# 5. NON-FUNCTIONAL REQUIREMENTS

- **NFR-01: Performance.** Process incoming camera observations continuously and update monitoring outputs with sufficiently low latency for live inspection. Actual throughput and latency shall be measured on the development hardware.
- **NFR-02: Independent Visualization.** Visualization should not unnecessarily block camera reception or reconstruction processing.
- **NFR-03: Spatial Accuracy.** The generated world should preserve important spatial relationships, approximate positions, dimensions and orientations. Fine surface detail is secondary.
- **NFR-04: Simplicity.** The generated world should use a lightweight representation and avoid unnecessary geometric complexity.
- **NFR-05: Modularity.** Camera input, RGB-D processing, point-cloud generation, perception, scene association, world generation and visualization should remain separate components.
- **NFR-06: Scalability.** Support four cameras initially while permitting additional camera sources in the future.
- **NFR-07: Reliability.** Temporary frame loss, invalid depth values or an unavailable camera should not crash the entire application.
- **NFR-08: Extensibility.** The Unity camera source should eventually be replaceable by physical RGB/RGB-D cameras with limited downstream changes.
- **NFR-09: Resource Efficiency.** Avoid unnecessary repeated processing and control point-cloud density and AI inference frequency where needed.
- **NFR-10: Maintainability.** Python modules should be organized by responsibility and expose clear interfaces between pipeline stages.
- **NFR-11: Evaluation.** Reconstruction quality and runtime performance shall be evaluated using measurable tests rather than assumed accuracy or speed.
- **NFR-12: Safety.** The current prototype is software-only and shall not directly control physical machinery.

---

# 6. SYSTEM ARCHITECTURE

## 6.1 Unity Simulation and Camera Streaming

**Responsibilities:** generate the environment and objects; position and configure four virtual cameras; capture RGB and depth; provide camera metadata; and stream data continuously to Python.

## 6.2 WebSocket Data Interface

**Responsibilities:** accept the Unity client connection; receive metadata and RGB-D payloads; decode and associate messages with camera IDs; maintain the latest available frame for each camera; and handle incomplete or delayed updates.

## 6.3 Camera Calibration and Spatial Reference

**Responsibilities:** calculate camera intrinsics from image dimensions and FOV or use supplied calibration values; interpret camera positions and orientation vectors; maintain Unity coordinate conventions; provide spatial transforms needed for multi-camera comparison and fusion; and validate camera direction and placement.

This module supports geometric reasoning across cameras. It does not imply that the fused point cloud is the final reconstructed world.

## 6.4 RGB-D Processing and Point-cloud Generation

**Responsibilities:** validate RGB and depth frames; interpret depth values in metric units; reject invalid or out-of-range depth; project valid pixels into camera-space 3D points; associate RGB colors with points; and generate a point cloud for each camera.

## 6.5 Multi-Camera Observation Fusion

**Responsibilities:** use calibration and spatial information to relate observations from different viewpoints; combine available point-cloud observations; retain color and geometric information; and support downstream multi-view scene understanding.

The fused cloud is an intermediate representation for visualization and geometric analysis, not the final world-generation output.

## 6.6 AI and Scene Understanding

**Responsibilities:** detect objects and structural regions; associate detections with depth and point-cloud evidence; estimate object and structure properties; associate the same object across multiple cameras; resolve duplicate and conflicting observations; and produce structured scene information.

## 6.7 World Generation

**Responsibilities:** consume structured scene information; create simplified geometry; assign position, scale, orientation and representative color; maintain relationships between generated objects; and update the generated world when the observed scene changes.

## 6.8 Visualization and Dashboard

**Responsibilities:** display all four camera feeds, the current fused point cloud, the generated 3D world when available, the 3D heatmap when available, and useful runtime information.

## 6.9 Logging and Evaluation

**Responsibilities:** record frame reception and processing information; record camera availability and errors; measure latency and update rate; record point counts and detected-object counts; and support comparison between the Unity source scene and generated scene.

---

# 7. TECHNOLOGY STACK

| Area | Technology |
|---|---|
| Simulation | Unity |
| Unity-side development | C# |
| Main processing | Python 3.x |
| Computer vision | OpenCV |
| Numerical processing | NumPy |
| 3D point-cloud processing | Open3D |
| Communication | WebSocket |
| Initial object detection | To be selected during AI implementation; YOLO/Ultralytics is a candidate |
| Scene representation | Structured Python data / JSON-compatible representation |
| Initial visualization | Open3D and a Python dashboard/window |
| Future visualization | Dedicated 3D rendering layer, subject to implementation needs |
| Development formats | JPEG/RGB image payloads, depth payloads, JSON metadata, PLY/PCD for point-cloud inspection |

The final AI model and rendering technology for the generated world are implementation decisions and are not fixed requirements at this stage.

---

# 8. DATA FLOW

## 8.1 Current Implemented Data Flow

```text
Unity Environment
   +--> North Camera (ID 0) -- RGB + Depth + Metadata
   +--> East Camera  (ID 1) -- RGB + Depth + Metadata
   +--> South Camera (ID 2) -- RGB + Depth + Metadata
   +--> West Camera  (ID 3) -- RGB + Depth + Metadata
                              |
                       WebSocket Streaming
                              |
                       Python Frame Receiver
                              |
                         RGB-D Validation
                              |
                      Per-Camera Point Clouds
                              |
                 Multi-Camera Observation Fusion
                              |
                      Live 2×2 Dashboard
                       /              \
                Camera Feeds      Fused Point Cloud
```

## 8.2 Planned AI and World-Generation Data Flow

```text
RGB Frames + Depth Frames + Camera Metadata
                    |
            Perception Processing
                    |
          +---------+----------+
          |                    |
    Object Detection     Structural Detection
          |                    |
          +---------+----------+
                    |
           Depth / 3D Association
                    |
         Geometric Property Estimation
                    |
       Multi-Camera Observation Association
                    |
         Structured Scene Description
                    |
          Simplified World Generation
                    |
          +---------+----------+
          |                    |
    Generated 3D World    Spatial Heatmap
```

## 8.3 RGB-D Point Generation

For an image pixel `(u, v)` with depth `Z`, camera-space coordinates are calculated using camera intrinsics:

```text
X = (u - cx) * Z / fx
Y = (cy - v) * Z / fy
Z = Z
```

Where `fx` and `fy` are focal lengths, `cx` and `cy` are the principal point coordinates, and `Z` is the measured depth in the configured metric unit.

The resulting point is `P_camera = (X, Y, Z)`. It is retained as a camera observation. Calibration and spatial transforms may be used to compare or fuse observations from multiple cameras in a shared reference frame.

## 8.4 Structured Scene Description

The AI and geometry pipeline is expected to produce a structured representation similar to the following. This is illustrative; exact fields may change during implementation.

```json
{
  "objects": [
    {
      "id": "wall_north",
      "class": "wall",
      "position": [0.0, 2.0, 5.0],
      "dimensions": [10.0, 4.0, 0.2],
      "orientation": [0.0, 0.0, 0.0],
      "color": [1.0, 0.0, 0.0],
      "confidence": 0.96
    },
    {
      "id": "object_001",
      "class": "cube",
      "position": [0.0, 0.5, 0.0],
      "dimensions": [1.0, 1.0, 1.0],
      "orientation": [0.0, 0.0, 0.0],
      "color": [0.2, 0.5, 0.9],
      "confidence": 0.91
    }
  ]
}
```

The values are examples only, not fixed scene dimensions or measured results.

---

# 9. REPRESENTATION LEVELS

| Level | Representation | Purpose | Status |
|---|---|---|---|
| 1 | Individual camera RGB-D observations | Capture visual and depth evidence | Completed |
| 2 | Individual camera point clouds | Convert depth observations into 3D measurements | Completed |
| 3 | Multi-camera fused point cloud | Combine geometric observations for inspection and analysis | Implemented and validated in the current simulation |
| 4 | Perception outputs | Detect objects and structural regions | Next phase |
| 5 | Structured scene description | Store object identity and estimated spatial/appearance properties | Planned |
| 6 | Simplified generated 3D world | Rebuild the environment using inferred geometry and object information | Planned |
| 7 | Spatial heatmap / confidence view | Visualize coverage, confidence or uncertainty | Planned |

The fused point cloud is an intermediate representation. The primary intended output of the advanced system is Level 6: a simplified generated 3D world.

---

# 10. PROJECT DEVELOPMENT STAGES

## Stage 0: Project Foundation — Completed

Set up Unity, Python, required libraries, project structure and development environment.

## Stage 1: Unity Simulation Environment — Completed for the current test scene

Create the room and environment elements; add walls and objects; configure North, East, South and West cameras; establish camera IDs and directional conventions; and configure resolution and field of view.

## Stage 2: RGB-D Camera Output — Completed and tested

Capture RGB and depth frames; capture camera position, orientation and direction vectors; transmit camera settings; and verify frame dimensions and depth values.

## Stage 3: Python Data Reception — Completed

Implement WebSocket communication; receive metadata and RGB/depth payloads; decode and validate frames; and associate data with the correct camera ID. Continuous streaming from all four cameras has been tested.

## Stage 4: Camera Calibration and Spatial Validation — Implemented and validated for the current Unity setup

Calculate camera intrinsics; read camera extrinsics; establish coordinate conventions; validate camera positions and viewing directions; and inspect individual camera observations.

## Stage 5: RGB-D to Point Cloud — Completed and tested

Interpret depth values in metric units; project image pixels into camera-space coordinates; attach RGB colors; filter invalid depth; generate per-camera point clouds; and inspect individual clouds.

## Stage 6: Multi-Camera Fusion — Implemented and validated in the current Unity test environment

Use camera calibration and spatial information to relate observations, combine point clouds, preserve color information and inspect the fused result for spatial consistency.

## Stage 7: Real-Time Monitoring Dashboard — Current two-panel functionality implemented and tested

Maintain the latest available frame from each camera; process incoming frames continuously; update the four camera-feed views and fused point-cloud view; organize the interface into a 2×2 layout; and reserve the remaining two panels for future outputs.

## Stage 8: Object and Structural Perception — Next major development phase

Select suitable detection and segmentation approaches; detect objects in RGB frames; identify major structures such as floors and walls; associate detections with depth; extract geometric evidence; estimate positions, dimensions, orientations and representative colors; and record confidence or quality information.

## Stage 9: Multi-Camera Scene Understanding — Planned

Associate the same object across camera views; remove duplicate hypotheses; combine geometric estimates; resolve conflicting estimates; maintain object identities across updates where feasible; and build a structured scene description.

## Stage 10: Simplified 3D World Generation — Planned

Define the scene-description data model; generate walls, floors and major structures; generate detected objects using suitable primitives; apply estimated position, dimensions, orientation and representative colors; maintain spatial relationships; and update the world when meaningful changes occur.

## Stage 11: 3D World Visualization and Heatmap — Planned

Add the generated world to panel three; add a 3D heatmap or spatial-confidence visualization to panel four; define the heatmap's meaning and visual encoding; and update both views from the latest scene representation.

## Stage 12: Performance, Accuracy and System Testing — Ongoing; full evaluation follows AI/world-generation implementation

Measure reception, point-cloud generation, fusion, inference and world-generation times; compare generated properties with Unity ground truth; test different scene layouts, moving objects, partial frame loss, occlusion and duplicate observations; and evaluate long-run stability.

## Stage 13: Physical Camera Readiness — Future work

Define a camera-source abstraction; integrate physical RGB-D cameras where available; calibrate and synchronize real cameras; handle sensor noise, lighting changes and missing depth; and evaluate the pipeline outside Unity.

---

# 11. CURRENT IMPLEMENTATION STATUS

| Component | Current status | Notes |
|---|---|---|
| Unity test environment | Completed | Simulated room and camera arrangement |
| Four virtual cameras | Completed | North 0, East 1, South 2, West 3 |
| RGB capture | Completed | Camera frames are streamed |
| Depth capture | Completed | Metric depth is available to Python |
| Camera metadata | Completed | Position, orientation/direction, resolution and FOV |
| WebSocket streaming | Completed | Continuous Unity-to-Python communication |
| Python frame receiver | Completed | Frames are decoded and associated by camera ID |
| Camera intrinsics | Completed | Calculated from configured camera parameters |
| Camera spatial calibration | Validated | Tested with the current Unity setup |
| Per-camera point clouds | Completed | Generated from RGB-D data |
| Multi-camera point-cloud fusion | Implemented and validated | Used as an intermediate geometric representation |
| Real-time camera display | Completed | Four feeds in the dashboard |
| Real-time fused point-cloud display | Completed | Second active dashboard panel |
| Object detection | Not started | Next development phase |
| Structural detection | Not started | Next development phase |
| 3D property estimation | Not started | Requires perception and geometric analysis |
| Multi-camera object association | Not started | Required for consistent scene understanding |
| Structured scene representation | Not started | To be designed |
| Simplified world generation | Not started | Main upcoming reconstruction milestone |
| 3D-world heatmap | Not started | Future dashboard panel |

**Status interpretation:** The current foundation demonstrates that the system can receive continuous multi-camera RGB-D data and generate/update a fused point-cloud representation in real time in the tested Unity environment. This does not mean semantic scene understanding or final simplified-world generation is already complete.

---

# 12. MVP AND TARGET OUTPUT

## 12.1 Completed Foundation Milestone

1. Unity scene with four virtual cameras.
2. RGB and depth output.
3. Camera metadata transmission.
4. Continuous WebSocket streaming.
5. Python frame reception and decoding.
6. Camera calibration and spatial handling.
7. Per-camera point-cloud generation.
8. Multi-camera point-cloud fusion.
9. Live four-camera feed display.
10. Live fused point-cloud display.

## 12.2 Intended Functional Prototype

1. All completed foundation capabilities.
2. Object and structural detection.
3. Depth-based geometric property estimation.
4. Multi-camera observation association.
5. Structured scene representation.
6. Simplified 3D world generation.
7. Representative object colors and approximate geometry.
8. Continuous updates to the generated world.
9. Four-panel dashboard: camera feeds, fused point cloud, generated simplified 3D world and 3D spatial heatmap.

The final prototype does not require photorealistic output, perfect texture reproduction or support for every object category.

---

# 13. USER INTERFACE REQUIREMENTS

The monitoring application shall use one window with a 2×2 grid.

| Panel | Intended display | Current state |
|---|---|---|
| Top-left | Four live camera feeds | Active |
| Top-right | Fused point cloud | Active |
| Bottom-left | Generated simplified 3D world | Reserved |
| Bottom-right | 3D-world heatmap | Reserved |

The interface should make it possible to inspect camera connection status, latest frame ID or timestamp, processing/update rate, point count, detected-object count (when available), world-generation status and errors or unavailable camera feeds.

The viewer is intended for monitoring and inspection. Object manipulation and physical control are not part of the current scope.

---

# 14. PERFORMANCE AND EVALUATION REQUIREMENTS

Performance shall be measured on the actual development hardware. Important measurements include:

- Per-camera frame reception rate.
- RGB-D decoding time.
- Per-camera point-cloud generation time.
- Multi-camera fusion time.
- AI inference time per frame or processing cycle.
- Scene-understanding and object-association time.
- World-generation update time.
- End-to-end observation-to-display latency.
- Number of points and detected objects.
- CPU and GPU utilization.
- Stability during continuous operation.

The system should prioritize a stable, understandable update of the generated world over processing every incoming camera frame through every AI stage. Camera reception, AI inference, world generation and visualization may operate at different update rates if required.

Accuracy evaluation should compare estimated scene properties against known Unity ground truth where available. Relevant measurements include object position error, dimension/scale error, orientation error, wall/plane position error, object classification accuracy, duplicate or missed object rate, and temporal stability of generated objects.

No unmeasured accuracy or FPS value shall be treated as a guaranteed system result.

---

# 15. TESTING REQUIREMENTS

## 15.1 Camera and Streaming Tests

- Verify all four camera IDs and the North/East/South/West naming convention.
- Verify camera viewing directions.
- Verify RGB and depth dimensions and metadata values.
- Verify frames are associated with the correct camera.
- Verify continuous streaming and recovery from temporary disconnects.

## 15.2 Point-cloud Tests

- Verify depth-to-3D projection and camera intrinsics.
- Verify camera-space point-cloud geometry.
- Verify spatial placement using camera metadata.
- Verify color association and multi-camera fusion.
- Inspect individual camera observations and the fused result.

## 15.3 AI Perception Tests

- Test object detection under different viewpoints and partial occlusion.
- Test depth association and structural detection.
- Compare estimated dimensions and positions with Unity ground truth.
- Measure false detections and missed detections.

## 15.4 World Generation Tests

- Verify detected structures produce expected simplified geometry.
- Verify object positions, scales, orientations and representative colors.
- Verify multiple camera observations do not create duplicate generated objects.
- Verify changes in the Unity scene are reflected in the generated world.
- Verify spatial consistency over successive updates.

## 15.5 Dashboard Tests

- Verify the four camera feeds update.
- Verify the fused point cloud updates.
- Verify the generated-world panel updates when implemented.
- Verify the heatmap panel updates when implemented.
- Verify slow visualization or AI processing does not unnecessarily stop frame reception.

---

# 16. RISKS AND CONSIDERATIONS

| Risk | Potential impact | Mitigation direction |
|---|---|---|
| Object occlusion | Some objects may not be visible from every camera | Combine evidence from multiple viewpoints |
| Inaccurate depth | Incorrect size or position estimates | Validate depth and reject invalid measurements |
| Duplicate detections | One object may be represented multiple times | Multi-camera association and duplicate resolution |
| Conflicting camera estimates | Inconsistent object geometry | Use calibration, confidence and multi-view geometric checks |
| AI inference latency | Delayed world updates | Optimize models and control inference frequency |
| Changing scenes | Generated world may become unstable | Add temporal association and controlled update logic |
| Incomplete observations | Parts of the environment may be missing | Track observation coverage and confidence |
| High point density | Increased processing and memory usage | Filter and downsample intermediate geometry where appropriate |

---

# 17. FUTURE EXTENSIONS

Potential extensions beyond the intended prototype include additional camera support, physical RGB-D camera integration, RGB-only depth estimation, advanced segmentation, improved multi-object tracking, temporal scene consistency, change detection, confidence-aware reconstruction, better handling of dynamic objects, mesh generation for selected objects, web-based 3D visualization, scene history and environment-monitoring alerts.

These are future possibilities and are not mandatory requirements for the current development milestone.

---

# 18. CONCLUSION

The first major milestone of Drushya establishes a working real-time multi-camera perception foundation. Unity supplies RGB-D observations and camera metadata; Python receives the streams, generates per-camera point clouds, combines the observations and displays the live camera feeds and fused point cloud.

The next major milestone is not to make the point cloud increasingly detailed. It is to interpret the information contained in the observations and use it to construct a separate, simplified 3D representation of the environment.

Drushya will therefore progress from **camera observations**, to **scene understanding**, to **structured spatial information**, and finally to **independent simplified world generation**. The final generated world should be cleaner and easier to interpret than the raw observations while preserving the important geometry and spatial relationships of the source environment.
