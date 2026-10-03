using System.Collections;
using UnityEngine;

public class CameraStreamer : MonoBehaviour
{
    [Header("Camera")]
    [SerializeField]
    private Camera targetCamera;

    [Header("Capture")]
    [SerializeField]
    private int width = 640;

    [SerializeField]
    private int height = 480;

    [SerializeField]
    private int jpegQuality = 75;

    [SerializeField]
    private int targetFPS = 15;

    [SerializeField]
    private int cameraId = 0;

    [Header("Networking")]
    [SerializeField]
    private WebSocketClient websocketClient;

    [Header("Metadata")]
    [SerializeField]
    private CameraMetadata cameraMetadata;


    private RenderTexture renderTexture;
    private Texture2D texture;

    private bool captured = false;

    private void Start()
    {
        if (targetCamera == null)
        {
            Debug.LogError("CameraStreamer: Target Camera is not assigned.");
            return;
        }

        StartCoroutine(InitializeAndCapture());
    }

    private IEnumerator InitializeAndCapture()
    {
        // Wait until WebSocket is connected
        while (websocketClient == null || !websocketClient.IsConnected)
        {
            yield return null;
        }

        Debug.Log("WebSocket ready. Starting camera capture.");

        if (cameraMetadata != null)
        {
            string metadataJson = cameraMetadata.ToJson();

            _ = websocketClient.SendTextMessage(metadataJson);

            Debug.Log(
                $"Sent metadata for Camera {cameraMetadata.CameraId}"
            );
        }
        else
        {
            Debug.LogWarning(
                $"CameraStreamer on {gameObject.name}: " +
                "CameraMetadata is not assigned."
            );
        }

        // Create RenderTexture
        renderTexture = new RenderTexture(
            width,
            height,
            24,
            RenderTextureFormat.ARGB32
        );

        renderTexture.Create();

        // Create CPU-readable Texture2D
        texture = new Texture2D(
            width,
            height,
            TextureFormat.RGB24,
            false
        );

        targetCamera.targetTexture = renderTexture;

        Debug.Log(
            $"CameraStreamer initialized for {targetCamera.name} " +
            $"({width}x{height})"
        );

        // Start continuous streaming
        StartCoroutine(StreamFrames());
    }

    private IEnumerator StreamFrames()
    {
        float frameInterval = 1f / targetFPS;

        while (true)
        {
            float startTime = Time.time;

            yield return StartCoroutine(CaptureAndSend());

            float elapsed = Time.time - startTime;
            float remaining = frameInterval - elapsed;

            if (remaining > 0)
            {
                yield return new WaitForSeconds(remaining);
            }
        }
    }

    private IEnumerator CaptureAndSend()
    {
        // Wait until Unity has rendered the frame
        yield return new WaitForEndOfFrame();

        // Remember current active RenderTexture
        RenderTexture previous = RenderTexture.active;

        // Make our camera's RenderTexture active
        RenderTexture.active = renderTexture;

        // Copy pixels from RenderTexture → Texture2D
        texture.ReadPixels(
            new Rect(0, 0, width, height),
            0,
            0
        );

        texture.Apply();

        // Restore previous RenderTexture
        RenderTexture.active = previous;

        // Encode image as JPEG
        byte[] jpegData = texture.EncodeToJPG(jpegQuality);

        Debug.Log(
            $"Captured {targetCamera.name}: " +
            $"{jpegData.Length} bytes JPEG"
        );

        byte[] packet = CreatePacket(jpegData);

        _ = websocketClient.Send(packet);

        captured = true;
    }

    private byte[] CreatePacket(byte[] jpegData)
    {   
        byte[] packet = new byte[4 + jpegData.Length];

        packet[0] = (byte)((cameraId >> 24) & 0xFF);
        packet[1] = (byte)((cameraId >> 16) & 0xFF);
        packet[2] = (byte)((cameraId >> 8) & 0xFF);
        packet[3] = (byte)(cameraId & 0xFF);

        System.Buffer.BlockCopy(
            jpegData,
            0,
            packet,
            4,
            jpegData.Length
        );

        return packet;
    }

    private void OnDestroy()
    {
        if (targetCamera != null)
        {
            targetCamera.targetTexture = null;
        }

        if (renderTexture != null)
        {
            renderTexture.Release();
            Destroy(renderTexture);
        }

        if (texture != null)
        {
            Destroy(texture);
        }
    }
}