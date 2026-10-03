using System;
using System.Text;
using UnityEngine;
using NativeWebSocket;

public class WebSocketClient : MonoBehaviour
{
    [Header("WebSocket")]
    [SerializeField]
    private string serverUrl = "ws://localhost:8765";

    private WebSocket websocket;

    public bool IsConnected =>
        websocket != null &&
        websocket.State == WebSocketState.Open;

    private async void Start()
    {
        await Connect();
    }

    private async System.Threading.Tasks.Task Connect()
    {
        Debug.Log($"Connecting to {serverUrl}...");

        websocket = new WebSocket(serverUrl);

        websocket.OnOpen += () =>
        {
            Debug.Log("WebSocket connected!");

            _ = SendHello();
        };

        websocket.OnError += (errorMsg) =>
        {
            Debug.LogError($"WebSocket error: {errorMsg}");
        };

        websocket.OnClose += (closeCode) =>
        {
            Debug.Log($"WebSocket closed: {closeCode}");
        };

        websocket.OnMessage += (bytes) =>
        {
            Debug.Log($"Received {bytes.Length} bytes from server.");
        };

        await websocket.Connect();
    }

    private async System.Threading.Tasks.Task SendHello()
    {
        if (!IsConnected)
        {
            Debug.LogWarning("Cannot send hello: WebSocket is not connected.");
            return;
        }

        string message = "Hello from Unity";

        await websocket.SendText(message);

        Debug.Log($"Sent: {message}");
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null)
        {
            await websocket.Close();
        }
    }

    
    public async System.Threading.Tasks.Task Send(byte[] data)
    {
        if (!IsConnected)
        {
            Debug.LogWarning("Cannot send binary data: WebSocket is not connected.");
            return;
        }

        await websocket.Send(data);

        Debug.Log($"Sent binary data: {data.Length} bytes");
    }
}
