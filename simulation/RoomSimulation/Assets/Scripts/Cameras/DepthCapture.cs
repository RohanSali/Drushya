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

        // Render this specific camera into the depth RenderTexture
        targetCamera.targetTexture = depthRenderTexture;

        targetCamera.RenderWithShader(
            depthMaterial.shader,
            "RenderType"
        );

        // Read rendered depth
        RenderTexture.active =
            depthRenderTexture;

        depthTexture.ReadPixels(
            new Rect(
                0,
                0,
                width,
                height
            ),
            0,
            0
        );

        depthTexture.Apply();

        // Convert to float array
        float[] depthData =
            GetDepthData();

        // Restore the previous rendering state
        RenderTexture.active = previousActive;
        targetCamera.targetTexture = previousCameraTarget;

        return depthData;
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