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

        // Save current active RenderTexture
        RenderTexture previous =
            RenderTexture.active;

        // Render this specific camera
        targetCamera.targetTexture =
            depthRenderTexture;

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

        // Restore previous state
        RenderTexture.active =
            previous;

        targetCamera.targetTexture = null;

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