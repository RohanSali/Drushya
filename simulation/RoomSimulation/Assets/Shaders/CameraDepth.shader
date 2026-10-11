Shader "Custom/CameraDepth"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" }

        Pass
        {
            ZWrite On
            ZTest LEqual
            Cull Back

            CGPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float3 viewRay : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;

                o.vertex = UnityObjectToClipPos(v.vertex);

                // Transform the vertex into camera space.
                float3 viewPos = UnityObjectToViewPos(v.vertex);

                // Store the view-space position for interpolation.
                o.viewRay = viewPos;

                return o;
            }

            float4 frag(v2f i) : SV_Target
            {
                // Recover the interpolated camera-space position.
                float depth = -i.viewRay.z;

                return float4(depth, depth, depth, 1.0);
            }

            ENDCG
        }
    }
}