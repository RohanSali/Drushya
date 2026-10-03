using System;
using UnityEngine;

[Serializable]
public class CameraMetadataData
{
    public string type = "camera_metadata";

    public int camera_id;

    public Vector3Data position;
    public Vector3Data rotation;

    public Vector3Data forward;
    public Vector3Data right;
    public Vector3Data up;

    public int width;
    public int height;

    public float fov;
    public float near_clip;
    public float far_clip;
}

[Serializable]
public class Vector3Data
{
    public float x;
    public float y;
    public float z;

    public Vector3Data(Vector3 vector)
    {
        x = vector.x;
        y = vector.y;
        z = vector.z;
    }
}

public class CameraMetadata : MonoBehaviour
{
    [Header("Camera Identification")]
    [SerializeField]
    private int cameraId;

    [Header("Camera Parameters")]
    [SerializeField]
    private Camera targetCamera;

    public int CameraId => cameraId;
    public Camera TargetCamera => targetCamera;

    public Vector3 Position => targetCamera.transform.position;
    public Vector3 Rotation => targetCamera.transform.eulerAngles;

    public Vector3 Forward => targetCamera.transform.forward;
    public Vector3 Right => targetCamera.transform.right;
    public Vector3 Up => targetCamera.transform.up;

    public int Width => targetCamera.targetTexture != null
        ? targetCamera.targetTexture.width
        : Screen.width;

    public int Height => targetCamera.targetTexture != null
        ? targetCamera.targetTexture.height
        : Screen.height;

    public float FieldOfView => targetCamera.fieldOfView;
    public float NearClipPlane => targetCamera.nearClipPlane;
    public float FarClipPlane => targetCamera.farClipPlane;

    private void Start()
    {
        if (targetCamera == null)
        {
            Debug.LogError(
                $"CameraMetadata on {gameObject.name}: " +
                "Target Camera is not assigned."
            );

            return;
        }

        PrintMetadata();
    }

    public void PrintMetadata()
    {
        Debug.Log(
            $"[Camera Metadata] Camera {CameraId}\n" +
            $"Position: {Position}\n" +
            $"Rotation: {Rotation}\n" +
            $"Forward: {Forward}\n" +
            $"Right: {Right}\n" +
            $"Up: {Up}\n" +
            $"Resolution: {Width} x {Height}\n" +
            $"FOV: {FieldOfView}\n" +
            $"Near Clip: {NearClipPlane}\n" +
            $"Far Clip: {FarClipPlane}"
        );
    }

    public string ToJson()
    {
        CameraMetadataData data = new CameraMetadataData
        {
            camera_id = CameraId,

            position = new Vector3Data(Position),
            rotation = new Vector3Data(Rotation),

            forward = new Vector3Data(Forward),
            right = new Vector3Data(Right),
            up = new Vector3Data(Up),

            width = Width,
            height = Height,

            fov = FieldOfView,
            near_clip = NearClipPlane,
            far_clip = FarClipPlane
        };

        return JsonUtility.ToJson(data);
    }
}