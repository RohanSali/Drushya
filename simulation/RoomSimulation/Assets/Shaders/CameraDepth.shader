Shader "Custom/CameraDepth"
{
    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
        }

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
                float depth : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;

                o.vertex = UnityObjectToClipPos(v.vertex);

                // Eye-space depth
                float3 viewPos = UnityObjectToViewPos(v.vertex);
                o.depth = -viewPos.z;

                return o;
            }

            float4 frag(v2f i) : SV_Target
            {
                return float4(
                    i.depth,
                    i.depth,
                    i.depth,
                    1.0
                );
            }

            ENDCG
        }
    }
}