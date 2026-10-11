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

    [Header("Depth")]
    [SerializeField]
    private DepthCapture depthCapture;

    private RenderTexture renderTexture;
    private Texture2D texture;

    private bool captured = false;
    private uint frameId = 0;

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

        RenderTexture.active = previous;

        // Capture depth for the same capture cycle
        float[] depthData = null;

        if (depthCapture != null)
        {
            depthData =
                depthCapture.CaptureDepthFrame();
        }

        byte[] jpegData =
            texture.EncodeToJPG(jpegQuality);

        frameId++;;
        if (depthData != null)
        {
            int centerIndex =
                (height / 2) * width +
                (width / 2);

            Debug.Log(
                $"[RGB-D] Camera={cameraId} " +
                $"Frame={frameId} " +
                $"DepthCenter={depthData[centerIndex]:F3}"
            );
        }

        Debug.Log(
            $"Captured {targetCamera.name}: " +
            $"{jpegData.Length} bytes JPEG"
        );

        byte[] packet = CreateRGBDPacket(
            jpegData,
            depthData,
            frameId
        );

        if (packet != null)
        {
            _ = websocketClient.Send(packet);
        }
        
        Debug.Log(
            $"[RGB-D Packet] " +
            $"Camera={cameraId} " +
            $"Frame={frameId} " +
            $"RGB={jpegData.Length} bytes " +
            $"Depth={depthData.Length * 2} bytes " +
            $"Total={packet.Length} bytes"
        );

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

    private byte[] CreateRGBDPacket(
        byte[] jpegData,
        float[] depthData,
        uint currentFrameId
    )
    {
        if (depthData == null)
        {
            Debug.LogWarning(
                $"Camera {cameraId}: " +
                "Depth data is null."
            );

            return null;
        }

        // Convert float depth → uint16
        ushort[] depthUint16 =
            new ushort[depthData.Length];

        for (int i = 0; i < depthData.Length; i++)
        {
            float depth = depthData[i];

            if (depth <= 0f)
            {
                depthUint16[i] = 0;
            }
            else
            {
                float scaled = depth * 1000f;

                scaled = Mathf.Clamp(
                    scaled,
                    0f,
                    65535f
                );

                depthUint16[i] =
                    (ushort)Mathf.RoundToInt(scaled);
            }
        }

        // Convert uint16 depth → bytes
        byte[] depthBytes =
            new byte[depthUint16.Length * 2];

        System.Buffer.BlockCopy(
            depthUint16,
            0,
            depthBytes,
            0,
            depthBytes.Length
        );

        int headerSize = 16;

        byte[] packet =
            new byte[
                headerSize +
                jpegData.Length +
                depthBytes.Length
            ];

        // Header
        WriteUInt32(
            packet,
            0,
            (uint)cameraId
        );

        WriteUInt32(
            packet,
            4,
            currentFrameId
        );

        WriteUInt32(
            packet,
            8,
            (uint)jpegData.Length
        );

        WriteUInt32(
            packet,
            12,
            (uint)depthBytes.Length
        );

        // RGB
        System.Buffer.BlockCopy(
            jpegData,
            0,
            packet,
            headerSize,
            jpegData.Length
        );

        // Depth
        System.Buffer.BlockCopy(
            depthBytes,
            0,
            packet,
            headerSize + jpegData.Length,
            depthBytes.Length
        );

        return packet;
    }

    private void WriteUInt32(
        byte[] buffer,
        int offset,
        uint value
    )
    {
        buffer[offset] =
            (byte)((value >> 24) & 0xFF);

        buffer[offset + 1] =
            (byte)((value >> 16) & 0xFF);

        buffer[offset + 2] =
            (byte)((value >> 8) & 0xFF);

        buffer[offset + 3] =
            (byte)(value & 0xFF);
    }

    public uint CurrentFrameId
    {
        get { return frameId; }
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