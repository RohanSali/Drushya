using UnityEngine;

public class DepthCapture : MonoBehaviour
{
    [Header("Camera")]
    [SerializeField]
    private Camera targetCamera;

    [Header("Depth")]
    [SerializeField]
    private Material depthMaterial;

    [SerializeField]
    private int width = 640;

    [SerializeField]
    private int height = 480;

    [Header("RGB Synchronization")]
    [SerializeField]
    private CameraStreamer cameraStreamer;

    private RenderTexture depthRenderTexture;
    private Texture2D depthTexture;
    private int captureCount;

    private void Start()
    {
        if (targetCamera == null)
        {
            Debug.LogError(
                $"[{name}] Target Camera is not assigned."
            );
            return;
        }

        if (depthMaterial == null)
        {
            Debug.LogError(
                $"[{name}] Depth Material is not assigned."
            );
            return;
        }

        CreateDepthResources();
    }

    private void CreateDepthResources()
    {
        depthRenderTexture = new RenderTexture(
            width,
            height,
            24,
            RenderTextureFormat.ARGBFloat
        );

        depthRenderTexture.name =
            $"{targetCamera.name}_Depth";

        depthRenderTexture.Create();

        depthTexture = new Texture2D(
            width,
            height,
            TextureFormat.RGBAFloat,
            false
        );
    }

    public float[] GetDepthData()
    {
        if (depthTexture == null)
            return null;

        Color[] pixels = depthTexture.GetPixels();

        float[] depthData = new float[pixels.Length];

        for (int i = 0; i < pixels.Length; i++)
        {
            depthData[i] = pixels[i].r;
        }

        return depthData;
    }

    public float[] CaptureDepthFrame()
    {
        if (targetCamera == null ||
            depthMaterial == null ||
            depthRenderTexture == null)
        {
            return null;
        }

        // Save the camera's current target and active RenderTexture
        RenderTexture previousActive = RenderTexture.active;
        RenderTexture previousCameraTarget = targetCamera.targetTexture;
        CameraClearFlags previousClearFlags = targetCamera.clearFlags;
        Color previousBackgroundColor = targetCamera.backgroundColor;

        float[] depthData;
        try
        {
            targetCamera.targetTexture = depthRenderTexture;
            targetCamera.clearFlags = CameraClearFlags.SolidColor;
            targetCamera.backgroundColor = Color.clear;

            RenderTexture.active = depthRenderTexture;
            GL.Clear(true, true, Color.clear);

            targetCamera.RenderWithShader(
                depthMaterial.shader,
                "RenderType"
            );

            RenderTexture.active = depthRenderTexture;
            depthTexture.ReadPixels(
                new Rect(0, 0, width, height),
                0,
                0
            );

            depthTexture.Apply();
            depthData = GetDepthData();
        }
        finally
        {
            RenderTexture.active = previousActive;
            targetCamera.targetTexture = previousCameraTarget;
            targetCamera.clearFlags = previousClearFlags;
            targetCamera.backgroundColor = previousBackgroundColor;
        }

        if (depthData == null)
        {
            return null;
        }

        captureCount++;
        if (captureCount == 1 || captureCount % 150 == 0)
        {
            LogDepthDiagnostics(depthData);
        }

        return depthData;
    }

    private void LogDepthDiagnostics(float[] depthData)
    {
        int validCount = 0;
        float minDepth = float.PositiveInfinity;
        float maxDepth = 0f;

        for (int i = 0; i < depthData.Length; i++)
        {
            float depth = depthData[i];
            if (float.IsNaN(depth) || float.IsInfinity(depth) || depth <= 0f)
            {
                continue;
            }

            validCount++;
            minDepth = Mathf.Min(minDepth, depth);
            maxDepth = Mathf.Max(maxDepth, depth);
        }

        int centerIndex = (height / 2) * width + width / 2;
        string range = validCount > 0
            ? $"{minDepth:F3}-{maxDepth:F3} m"
            : "no valid geometry";
        Debug.Log(
            $"[DepthCapture] Camera={targetCamera.name} " +
            $"Frame={captureCount} Size={width}x{height} " +
            $"Valid={validCount}/{depthData.Length} " +
            $"Zero/invalid={depthData.Length - validCount} " +
            $"Range={range} Center={depthData[centerIndex]:F3} m"
        );
    }

    private void OnDestroy()
    {
        if (depthRenderTexture != null)
        {
            depthRenderTexture.Release();
            Destroy(depthRenderTexture);
        }

        if (depthTexture != null)
        {
            Destroy(depthTexture);
        }
    }
}