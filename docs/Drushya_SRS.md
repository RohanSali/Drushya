# Software Requirements Specification (SRS)

## Project Information
- **Project Title:** 
Real-Time Simplified 3D Environment Reconstruction from Multi-Camera Feeds

- **Document Type:** 
Software Requirements Specification

- **Version:** 
1.0

- **Project Status:** 
Prototype / Final-Year Engineering Project Subsystem

## 1. INTRODUCTION

### 1.1 Purpose

This project aims to develop a prototype system capable of converting observations of a real-world environment into a simplified 3D representation in near real time.

The initial implementation will use a Unity-based simulated environment instead of physical cameras or IoT hardware. Four virtual cameras will observe a common scene from different viewpoints. Camera data will be processed by a Python-based perception and reconstruction pipeline to generate a unified, simplified 3D representation of the observed environment.

The project intentionally does not attempt to create a photorealistic or perfectly accurate digital twin. The objective is to create a spatially meaningful, lightweight and visually understandable approximation of the environment that can be freely viewed using a 3D camera.

### 1.2 Scope

The prototype will cover:

- Creation of a simple simulated environment in Unity.
- Placement of four virtual cameras with overlapping fields of view.
- Generation/capture of RGB and depth information.
- Transmission of camera data from Unity to Python.
- Camera calibration and coordinate-system handling.
- Conversion of RGB-D observations into 3D point clouds.
- Transformation of individual camera point clouds into a common coordinate system.
- Multi-camera point-cloud fusion.
- Point-cloud filtering and downsampling.
- Optional voxel/primitive-based simplification.
- Optional object detection and basic 3D localization.
- Real-time or near-real-time updates.
- Interactive 3D visualization with rotation, zoom and pan.
- Evaluation of reconstruction quality, processing speed and system stability.

The following are outside the initial scope:

- Photorealistic reconstruction.
- Exact digital-twin generation.
- Physical IoT camera deployment.
- Advanced semantic understanding of every object.
- Autonomous control of physical machines.
- User actions such as object selection, manipulation or command execution.
- Full-scale production deployment.

### 1.3 Intended Users

Primary users:

- Project developer/researcher.
- Engineering students working on computer vision and 3D reconstruction.
- Researchers experimenting with multi-camera perception.
- Future users of a larger machine/environment monitoring system.

### 1.4 Definitions and Acronyms

RGB:
Red-Green-Blue image data.

RGB-D:
RGB image combined with depth information.

3D:
Three-dimensional spatial representation.

Point Cloud:
Collection of points representing the geometry/surface of an environment.

Voxel:
A volumetric element representing a small region of 3D space.

Camera Intrinsics:
Internal camera parameters such as focal length and principal point.

Camera Extrinsics:
Camera position and orientation relative to a reference coordinate system.

FOV:
Field of View.

ICP:
Iterative Closest Point, an algorithm commonly used for point-cloud registration.

FPS:
Frames Per Second.

YOLO:
You Only Look Once, an object-detection model family.

Scene Reconstruction:
Process of generating a 3D representation from sensor/camera observations.

Near Real-Time:
A system response/update rate sufficiently fast for continuous monitoring, even if reconstruction is not performed at the full rendering frame rate.


## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective

The system will consist of three major layers:

A. Simulation Layer
B. Perception and Reconstruction Layer
C. Visualization Layer

High-Level Architecture:

+--------------------------------------+
|          UNITY SIMULATION            |
|                                      |
|  Environment + Objects + 4 Cameras   |
+------------------+-------------------+
|
RGB / Depth Data
|
v
+--------------------------------------+
|       PYTHON PERCEPTION LAYER        |
|                                      |
| Calibration                          |
| Depth Processing                     |
| Point Cloud Generation               |
| Coordinate Transformation            |
| Multi-Camera Registration             |
| Point Cloud Fusion                   |
| Simplification                       |
| Optional Object Detection            |
+------------------+-------------------+
|
Simplified 3D Scene
|
v
+--------------------------------------+
|           3D VIEWER                  |
|                                      |
| Rotate / Zoom / Pan / View           |
+--------------------------------------+

### 2.2 Simulation Environment

Unity will represent the initial "real world".

The scene will contain simple objects such as:

- Floor
- Walls
- Tables
- Boxes
- Cylinders
- Other simple objects
- Optional moving objects

Four virtual cameras will be positioned around the environment.

The cameras should have overlapping fields of view rather than pointing to exactly the same location.

### 2.3 Camera Configuration

Each camera will have:

- Position
- Rotation
- Resolution
- Field of View
- Intrinsic parameters
- Extrinsic parameters
- RGB output
- Depth output where supported

The initial camera parameters can be obtained directly from Unity because the simulation provides exact camera information.

### 2.4 Reconstruction Philosophy

The system will prioritize:

- Approximate geometry
- Low computational complexity
- Real-time/near-real-time operation
- Spatial consistency
- Visual clarity

The system will NOT prioritize:

- Photorealism
- Fine surface details
- Texture-perfect reconstruction
- Pixel-level similarity to the source environment


## 3. SYSTEM OBJECTIVES

The main objectives are:

1. Develop a simulated multi-camera perception environment.
2. Capture synchronized or near-synchronized camera observations.
3. Process RGB-D information using Python.
4. Convert camera observations into 3D points.
5. Transform multiple point clouds into a common coordinate system.
6. Fuse observations from all four cameras.
7. Produce a simplified 3D representation.
8. Optionally detect and localize objects in 3D.
9. Display the reconstructed environment interactively.
10. Maintain near-real-time processing.
11. Create an architecture that can later accept physical camera feeds.
12. Establish a foundation for a larger real-world monitoring/digital-environment project.


## 4. FUNCTIONAL REQUIREMENTS

- **FR requirement:** Unity Environment Creation

The system shall provide a Unity scene containing a simple environment with static and optional dynamic objects.

- **FR requirement:** Multi-Camera Setup

The system shall support four virtual cameras positioned around the environment with overlapping viewpoints.

- **FR requirement:** Camera Data Generation

Each virtual camera shall generate RGB frames and depth information for reconstruction.

- **FR requirement:** Camera Metadata

The system shall provide camera intrinsic and extrinsic information to the Python pipeline.

- **FR requirement:** Camera Data Transfer

The system shall support transferring camera data from Unity to Python.

Initial implementation may use saved frames/files for development. The target implementation shall support real-time streaming through an appropriate communication mechanism such as TCP or WebSocket.

- **FR requirement:** RGB-D Processing

The Python pipeline shall process RGB and depth data.

- **FR requirement:** 3D Point Generation

The system shall convert image pixels and depth information into 3D coordinates.

- **FR requirement:** Point Cloud Generation

The system shall generate a point cloud for each camera.

- **FR requirement:** Coordinate Transformation

The system shall transform individual camera point clouds into a common world coordinate system.

- **FR requirement:** Multi-Camera Fusion

The system shall merge point clouds generated from the four cameras.

- **FR requirement:** Point Cloud Filtering

The system shall support removal of invalid, noisy or unnecessary points.

- **FR requirement:** Point Cloud Downsampling

The system shall reduce point density while attempting to preserve important geometry.

- **FR requirement:** Voxel Representation

The system should optionally support voxelization for lightweight spatial representation.

- **FR requirement:** Primitive Simplification

The system should support conversion of suitable geometric regions into simple primitives such as:

- Planes
- Cuboids
- Cylinders
- Basic geometric structures

- **FR requirement:** Object Detection

The system may use an object detection model such as YOLO to identify relevant objects.

- **FR requirement:** 3D Object Localization

For detected objects, the system should estimate:

- 3D position
- Approximate dimensions
- Approximate orientation where possible

- **FR requirement:** Scene Representation

The system shall maintain a representation of the reconstructed environment that can be rendered by the visualization layer.

- **FR requirement:** Real-Time Updates

The system shall continuously process incoming camera observations and update the reconstructed environment.

- **FR requirement:** Interactive Viewer

The viewer shall support:

- Rotation
- Zoom
- Pan
- Free camera movement
- Basic viewpoint changes

- **FR requirement:** View-Only Interaction

The viewer shall be primarily for visualization. Object selection, manipulation and physical control actions are outside the initial scope.

- **FR requirement:** Reconstruction Output

The system shall be capable of producing at least one of:

- Point cloud
- Voxel representation
- Simplified 3D scene
- Primitive-based 3D scene

- **FR requirement:** Logging

The system should record basic processing information such as:

- Frame rate
- Reconstruction update rate
- Processing time
- Number of points
- Number of detected objects
- System errors


## 5. NON-FUNCTIONAL REQUIREMENTS

- **NFR requirement:** Performance

The system should target near-real-time reconstruction updates.

The rendering/viewer should ideally operate independently of the reconstruction update rate.

Target prototype architecture:

Camera capture:
Approximately 15-30 FPS

Reconstruction:
Approximately 5-10 updates/sec where hardware permits

Viewer:
Target approximately 30-60 FPS

These values are engineering targets, not strict minimum requirements.

- **NFR requirement:** Scalability

The architecture should allow four cameras initially and support additional cameras in future versions.

- **NFR requirement:** Modularity

The following components should remain independently replaceable:

- Simulation
- Camera input
- Depth processing
- Object detection
- Reconstruction
- Scene simplification
- Visualization

- **NFR requirement:** Extensibility

The Unity cameras should eventually be replaceable by physical RGB/RGB-D cameras without redesigning the complete reconstruction pipeline.

- **NFR requirement:** Reliability

Temporary camera-frame failures should not crash the entire system.

- **NFR requirement:** Maintainability

Python modules should be separated according to their responsibility.

- **NFR requirement:** Usability

The viewer should provide intuitive camera controls without requiring complex user interaction.

- **NFR requirement:** Resource Efficiency

The reconstruction pipeline should avoid unnecessary processing of high-density data.

- **NFR requirement:** Accuracy

The reconstructed scene should preserve major spatial relationships and object locations even if fine geometry is lost.

- **NFR requirement:** Safety

The prototype is software-only and will not directly control physical machinery.


## 6. SYSTEM ARCHITECTURE

### 6.1 Major Components

### Component 1: Unity Simulation

Responsibilities:

- Generate environment.
- Generate objects.
- Position cameras.
- Generate RGB images.
- Generate depth maps.
- Provide camera metadata.
- Simulate optional object movement.

### Component 2: Camera Data Interface

Responsibilities:

- Package camera frames.
- Synchronize camera data.
- Transfer data to Python.
- Handle frame timestamps.

### Component 3: Camera Calibration Module

Responsibilities:

- Store intrinsic parameters.
- Store extrinsic parameters.
- Convert camera coordinates to world coordinates.
- Handle coordinate-system conventions.

### Component 4: RGB-D Processing Module

Responsibilities:

- Validate RGB frames.
- Validate depth frames.
- Remove invalid depth.
- Convert depth values into metric distances where applicable.

### Component 5: Point Cloud Generator

Responsibilities:

- Convert RGB-D pixels into 3D points.
- Attach RGB/color information.
- Generate per-camera point clouds.

### Component 6: Registration and Fusion Module

Responsibilities:

- Transform point clouds into a common coordinate frame.
- Align point clouds if required.
- Fuse observations.
- Remove redundant points.

### Component 7: Simplification Module

Responsibilities:

- Downsample point clouds.
- Voxelize data.
- Detect planes.
- Fit basic primitives.
- Produce lightweight scene representation.

### Component 8: Object Perception Module

Optional in the first version.

Responsibilities:

- Detect objects.
- Estimate object location.
- Combine detection with depth.
- Produce semantic object information.

### Component 9: Visualization Module

Responsibilities:

- Render reconstructed environment.
- Support rotate, zoom and pan.
- Display point clouds or simplified geometry.
- Update the scene continuously.

### Component 10: Monitoring/Logging Module

Responsibilities:

- Record processing statistics.
- Record errors.
- Measure latency.
- Measure reconstruction update rate.


## 7. TECHNOLOGY STACK

Simulation:
- Unity
- C# for Unity-side scripts

Main Processing:
- Python 3.x

Computer Vision:
- OpenCV

3D Processing:
- Open3D

Numerical Processing:
- NumPy

Optional Machine Learning:
- YOLO / Ultralytics

Communication:
- TCP or WebSocket
- File-based exchange for early development/testing

Visualization:
- Open3D for initial prototype
- Unity as an optional/future visualization layer

Data Formats:
- PNG/JPEG for image data where appropriate
- Depth-map compatible format
- JSON for metadata and scene representation
- PLY/PCD for point clouds during development


## 8. DATA FLOW

### 8.1 Initial Data Flow

Unity Scene
|
+--> Camera 1 --> RGB + Depth
|
+--> Camera 2 --> RGB + Depth
|
+--> Camera 3 --> RGB + Depth
|
+--> Camera 4 --> RGB + Depth
|
v
Python Pipeline
|
v
RGB-D Processing
|
v
Point Cloud x 4
|
v
Coordinate Transform
|
v
Point Cloud Fusion
|
v
Filtering/Downsampling
|
v
Scene Simplification
|
v
Optional Object Detection
|
v
3D Scene Representation
|
v
3D Viewer

### 8.2 Point Generation

For a camera pixel:

Pixel = (u, v)
Depth = Z

Using camera intrinsics, the system calculates:

X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
Z = Z

Where:

fx = focal length in x direction
fy = focal length in y direction
cx = principal point x coordinate
cy = principal point y coordinate

The resulting point is:

P_camera = (X, Y, Z)

The point is then transformed using the camera's extrinsic parameters into the world coordinate system.


## 9. 3D REPRESENTATION LEVELS

The system will evolve through multiple representation levels.

- **Level 1:**
Individual camera point clouds.

- **Level 2:**
Unified multi-camera point cloud.

- **Level 3:**
Filtered/downsampled point cloud.

- **Level 4:**
Voxel-based environment.

- **Level 5:**
Simplified geometric primitives.

- **Level 6:**
Semantic scene containing detected objects and their approximate 3D properties.

The final prototype does not need to reach all levels if the earlier stages provide sufficient validation.


## 10. PROJECT DEVELOPMENT STAGES

### STAGE 0: PROJECT FOUNDATION

**Goal:**
Set up the development environment.

**Tasks:**

- Install Unity.
- Install Python.
- Create Python virtual environment.
- Install NumPy.
- Install OpenCV.
- Install Open3D.
- Install required Unity packages.
- Create Git repository.
- Establish project directory structure.

**Deliverable:**
Working development environment.


### STAGE 1: UNITY SIMULATION ENVIRONMENT

**Goal:**
Create a simple simulated world.

**Tasks:**

- Create floor.
- Create walls.
- Add simple objects.
- Add static objects.
- Add optional moving objects.
- Define Unity world coordinate system.
- Place four cameras.
- Ensure camera viewpoints overlap.
- Configure camera resolution and FOV.

**Deliverable:**
Unity scene with four functioning virtual cameras.


### STAGE 2: CAMERA OUTPUT

**Goal:**
Obtain camera observations.

**Tasks:**

- Capture RGB frames.
- Generate depth frames.
- Capture camera position.
- Capture camera rotation.
- Capture FOV/intrinsic information.
- Verify depth values.
- Verify frame timestamps.

**Deliverable:**
Four-camera RGB-D dataset/stream.


### STAGE 3: PYTHON CAMERA INPUT

**Goal:**
Receive camera data in Python.

**Tasks:**

- Implement input interface.
- Initially support saved image/depth files.
- Later implement real-time communication.
- Decode RGB and depth frames.
- Validate frame dimensions.
- Synchronize camera frames where possible.

**Deliverable:**
Python application receiving data from four cameras.


### STAGE 4: CAMERA CALIBRATION AND COORDINATES

**Goal:**
Establish consistent camera geometry.

**Tasks:**

- Store intrinsic parameters.
- Store extrinsic parameters.
- Define world coordinate system.
- Verify camera-to-world transformations.
- Test projection/reprojection.
- Visualize camera positions.

**Deliverable:**
Verified multi-camera coordinate system.


### STAGE 5: RGB-D TO POINT CLOUD

**Goal:**
Generate 3D information.

**Tasks:**

- Convert depth pixels to metric depth.
- Calculate 3D coordinates.
- Attach RGB colors.
- Remove invalid depth.
- Generate point cloud for each camera.
- Visualize individual point clouds.

**Deliverable:**
Four independent 3D point clouds.


### STAGE 6: MULTI-CAMERA FUSION

**Goal:**
Create one unified 3D representation.

**Tasks:**

- Transform each point cloud to world coordinates.
- Verify spatial alignment.
- Merge point clouds.
- Remove duplicates/redundant points.
- Apply filtering.
- Test registration/ICP where necessary.

**Deliverable:**
Unified reconstructed point cloud.


### STAGE 7: POINT CLOUD OPTIMIZATION

**Goal:**
Reduce computational and visual complexity.

**Tasks:**

- Statistical/radius outlier removal.
- Voxel downsampling.
- Density reduction.
- Remove unnecessary background points.
- Benchmark processing time.

**Deliverable:**
Lightweight and cleaner reconstructed environment.


### STAGE 8: SIMPLE 3D SCENE REPRESENTATION

**Goal:**
Move from raw points toward simplified geometry.

**Tasks:**

- Detect dominant planes.
- Identify floor/walls.
- Fit basic geometric primitives.
- Convert suitable regions into boxes/cylinders/planes.
- Store scene objects in structured format.

Example scene representation:

{
"objects": [
{
"type": "box",
"position": [x, y, z],
"scale": [width, height, depth]
}
]
}

**Deliverable:**
Simplified 3D scene representation.


### STAGE 9: OBJECT DETECTION AND 3D LOCALIZATION

**Goal:**
Add semantic information.

**Tasks:**

- Integrate YOLO or another detector.
- Detect objects in RGB frames.
- Associate detections with depth.
- Estimate 3D center.
- Estimate approximate object dimensions.
- Track objects over time if required.

**Deliverable:**
Semantic 3D object representation.


### STAGE 10: REAL-TIME PIPELINE

**Goal:**
Process continuous camera data.

**Tasks:**

- Replace file-based input with streaming.
- Implement frame queues.
- Process cameras continuously.
- Avoid blocking the viewer.
- Add timestamps.
- Measure end-to-end latency.
- Optimize bottlenecks.
- Control reconstruction update frequency.

**Deliverable:**
Near-real-time reconstruction pipeline.


### STAGE 11: 3D VIEWER

**Goal:**
Provide an interactive visualization.

**Tasks:**

- Display reconstructed environment.
- Implement orbit/rotation.
- Implement zoom.
- Implement pan.
- Implement free camera movement.
- Update scene continuously.
- Avoid selection/manipulation actions.
- Display optional object labels.

**Deliverable:**
Interactive 3D reconstruction viewer.


### STAGE 12: PERFORMANCE AND TESTING

**Goal:**
Validate the system.

**Tasks:**

- Measure FPS.
- Measure reconstruction update rate.
- Measure latency.
- Measure point count.
- Measure CPU/GPU utilization.
- Test different scene sizes.
- Test camera configurations.
- Test moving objects.
- Test temporary frame loss.
- Compare reconstructed and original scene geometry.

**Deliverable:**
Performance and evaluation report.


### STAGE 13: PHYSICAL CAMERA READINESS

Future stage.

**Goal:**
Prepare the architecture for real-world cameras.

**Tasks:**

- Define camera interface abstraction.
- Replace Unity camera source with physical camera source.
- Perform real camera calibration.
- Synchronize physical cameras.
- Handle camera noise.
- Handle lighting changes.
- Test depth estimation if depth cameras are unavailable.

**Deliverable:**
Architecture capable of accepting physical camera feeds.


## 11. MVP DEFINITION

The Minimum Viable Prototype shall include:

1. Unity scene.
2. Four virtual cameras.
3. RGB and depth output.
4. Python input pipeline.
5. Camera parameters.
6. RGB-D to 3D conversion.
7. Four point clouds.
8. Common coordinate transformation.
9. Unified point cloud.
10. Basic filtering/downsampling.
11. Open3D visualization.
12. Rotate, zoom and pan controls.

The MVP does NOT require:

- YOLO.
- Full object recognition.
- Primitive reconstruction.
- Physical cameras.
- IoT devices.
- Photorealistic mesh generation.
- Advanced tracking.


## 12. ADVANCED VERSION

After the MVP, the following features can be added:

- YOLO-based object detection.
- 3D object localization.
- Object tracking.
- Primitive fitting.
- Voxel-based reconstruction.
- Mesh generation.
- Temporal consistency.
- Dynamic-object handling.
- Better registration.
- GPU acceleration.
- Real camera support.
- RGB-only depth estimation.
- Web-based 3D viewer.
- Scene history.
- Environment change detection.
- Machine monitoring.
- Alert generation.


## 13. USER INTERFACE REQUIREMENTS

The viewer should provide:

- Main 3D viewport.
- Orbit camera.
- Zoom control.
- Pan control.
- Reset viewpoint.
- Optional FPS display.
- Optional reconstruction update rate.
- Optional point count.
- Optional detected-object information.

The interface should prioritize visualization and should not expose physical control functionality.


## 14. PERFORMANCE REQUIREMENTS

The prototype should attempt to achieve:

- Four-camera input support.
- Continuous camera processing.
- Reconstruction update rate of approximately 5-10 updates/sec where feasible.
- Viewer rendering of approximately 30-60 FPS where feasible.
- Low enough latency to make environment changes visually understandable.
- Scalable point-cloud density.

Performance should be measured rather than assumed.


## 15. TESTING REQUIREMENTS

### 15.1 Unit Testing

Test:

- Depth conversion.
- Coordinate transformation.
- Point generation.
- Filtering.
- Voxelization.
- Scene-data serialization.

### 15.2 Integration Testing

Test:

- Unity to Python communication.
- Four-camera input.
- RGB-D processing.
- Point-cloud fusion.
- Viewer update.

### 15.3 Reconstruction Testing

Test:

- Static environment.
- Different camera positions.
- Partial camera overlap.
- Moving objects.
- Different object sizes.
- Different scene complexity.

### 15.4 Performance Testing

Measure:

- Input FPS.
- Processing time per camera.
- Fusion time.
- Visualization FPS.
- Memory usage.
- CPU usage.
- GPU usage.
- End-to-end latency.

### 15.5 Failure Testing

Test:

- Missing camera frame.
- Invalid depth.
- Delayed frame.
- Camera disconnect.
- Corrupted data.
- Excessive point density.


## 16. EVALUATION METRICS

The project will be evaluated using:

1. Reconstruction completeness.
2. Spatial alignment.
3. Approximate positional accuracy.
4. Point-cloud quality.
5. Processing latency.
6. Reconstruction update rate.
7. Viewer FPS.
8. CPU/GPU utilization.
9. Memory usage.
10. Stability during continuous operation.

For the simplified representation, structural correctness is more important than fine-grained geometric accuracy.


## 17. RISKS AND MITIGATION

Risk 1:
Four-camera point clouds do not align.

Mitigation:
Verify camera extrinsics and coordinate conventions before applying advanced registration.

Risk 2:
Depth data contains noise.

Mitigation:
Apply depth filtering, outlier removal and voxel downsampling.

Risk 3:
Real-time performance is low.

Mitigation:
Reduce image resolution, point density and reconstruction frequency; use asynchronous processing and GPU acceleration where appropriate.

Risk 4:
Data transfer becomes a bottleneck.

Mitigation:
Use compressed frames, efficient serialization and streaming rather than unnecessary file operations.

Risk 5:
Moving objects produce inconsistent reconstruction.

Mitigation:
Initially test static scenes; later introduce temporal processing and object tracking.

Risk 6:
Primitive fitting fails.

Mitigation:
Keep point-cloud representation as a valid fallback.

Risk 7:
Object detection is computationally expensive.

Mitigation:
Run detection at a lower frequency and use tracking between detections.

Risk 8:
Unity and Python coordinate systems differ.

Mitigation:
Define and document a single world-coordinate convention and implement explicit coordinate transformations.

Risk 9:
The system becomes too complex.

Mitigation:
Follow the staged development plan and validate each stage before moving to the next.


## 18. PROJECT DIRECTORY STRUCTURE

Suggested structure:

Drushya/
|
+-- simulation/unity_simulation/
|   +-- Assets/
|   +-- Scenes/
|   +-- Scripts/
|   +-- Cameras/
|   +-- Shaders/
|
+-- python_reconstruction/
|   +-- main.py
|   +-- config.py
|   +-- camera/
|   |   +-- calibration.py
|   |   +-- transforms.py
|   |
|   +-- input/
|   |   +-- stream.py
|   |   +-- file_input.py
|   |
|   +-- perception/
|   |   +-- depth.py
|   |   +-- detection.py
|   |
|   +-- reconstruction/
|   |   +-- pointcloud.py
|   |   +-- registration.py
|   |   +-- fusion.py
|   |   +-- simplification.py
|   |
|   +-- visualization/
|   |   +-- viewer.py
|   |
|   +-- utils/
|       +-- logging.py
|       +-- metrics.py
|
+-- data/
|   +-- rgb/
|   +-- depth/
|   +-- calibration/
|   +-- pointclouds/
|   +-- scenes/
|
+-- docs/
|   +-- SRS.txt
|   +-- architecture/
|   +-- experiments/
|
+-- tests/
|
+-- README.md


## 19. FUTURE EXTENSION TO REAL WORLD

The final architecture should follow the abstraction:

Camera Source
|
+---- Unity Virtual Cameras
|
+---- Physical RGB Cameras
|
+---- RGB-D Cameras
|
+---- IP Cameras
|
v
Perception Pipeline
|
v
3D Reconstruction
|
v
Scene Representation
|
v
Visualization / Monitoring

This allows the current Unity-based prototype to become the foundation for a future physical-camera system.

Potential future applications include:

- Machine monitoring.
- Factory environment visualization.
- Industrial inspection.
- Robotics.
- Surveillance visualization.
- Smart environments.
- Digital-environment monitoring.
- Multi-camera spatial awareness.


## 20. PROJECT MILESTONE SUMMARY

Milestone 1:
Unity scene + four cameras.

Milestone 2:
RGB/depth capture.

Milestone 3:
Python camera input.

Milestone 4:
Camera calibration and coordinate system.

Milestone 5:
RGB-D to point cloud.

Milestone 6:
Multi-camera point-cloud fusion.

Milestone 7:
Filtering and downsampling.

Milestone 8:
Simplified 3D scene.

Milestone 9:
Optional object detection and 3D localization.

Milestone 10:
Near-real-time streaming pipeline.

Milestone 11:
Interactive 3D viewer.

Milestone 12:
Performance evaluation and documentation.

Milestone 13:
Future physical-camera integration.


## 21. FINAL EXPECTED OUTPUT

The completed prototype should demonstrate the following end-to-end workflow:

Simulated Real World
|
v
+----------------+
| Unity Scene    |
+----------------+
|
Four Cameras
|
v
RGB + Depth Data
|
v
+----------------+
| Python         |
| Perception     |
+----------------+
|
v
Individual 3D
Point Clouds
|
v
Coordinate
Transformation
|
v
Multi-Camera
Fusion
|
v
Filtering /
Simplification
|
v
Approximate 3D
Environment
|
v
+----------------+
| 3D Viewer      |
| Rotate         |
| Zoom           |
| Pan            |
+----------------+

The final prototype is considered successful when a Unity environment observed by four virtual cameras can be converted into a coherent simplified 3D representation in Python and displayed interactively with acceptable near-real-time performance.

## 22. CONCLUSION

This project establishes a modular foundation for converting multi-camera observations into a simplified 3D representation of an environment.

The development strategy intentionally begins with a controlled Unity simulation and RGB-D data. This reduces the complexity of physical camera calibration, sensor noise and hardware integration while allowing the core perception and reconstruction pipeline to be developed and tested.

The project will progress from individual point clouds to multi-camera fusion and eventually toward simplified semantic 3D scenes. Object detection, real-time streaming and physical-camera integration will be added only after the core reconstruction pipeline is validated.

The architecture is therefore designed not as a complete digital twin system, but as a practical prototype of the perception and visualization subsystem that can later become part of a larger real-world monitoring, robotics or industrial environment system.

END OF SRS