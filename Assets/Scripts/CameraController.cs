using UnityEngine;

namespace LifeSim.World
{
    [RequireComponent(typeof(Camera))]
    public class CameraController : MonoBehaviour
    {
        [Header("Velocidad de Movimiento")]
        [Tooltip("Velocidad de desplazamiento con las flechas o WASD")]
        public float moveSpeed = 22f;
        public float fastMoveMultiplier = 2.5f;

        [Header("Zoom")]
        public float zoomSpeed = 8f;
        public float minZoom = 2.5f;
        public float maxZoom = 60f;

        [Header("Límites de Cámara (Mundo 160x120)")]
        public bool clampToBounds = true;
        public Vector2 minBounds = new Vector2(-80f, -60f);
        public Vector2 maxBounds = new Vector2(80f, 60f);

        private Camera cam;

        private void Awake()
        {
            cam = GetComponent<Camera>();
            if (cam != null)
            {
                cam.orthographic = true;
                // Fondo oscuro verde bosque para combinar con el prado
                cam.backgroundColor = new Color(0.04f, 0.07f, 0.05f, 1f);
                if (cam.orthographicSize < 10f)
                {
                    cam.orthographicSize = 18f;
                }
            }
        }

        private void Update()
        {
            HandleMovement();
            HandleZoom();
            HandleShortcuts();
        }

        private void HandleMovement()
        {
            float horizontal = Input.GetAxisRaw("Horizontal"); // Flechas izq/der o A/D
            float vertical = Input.GetAxisRaw("Vertical");     // Flechas arr/abj o W/S

            if (horizontal != 0 || vertical != 0)
            {
                float currentSpeed = moveSpeed;
                if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
                {
                    currentSpeed *= fastMoveMultiplier;
                }

                Vector3 direction = new Vector3(horizontal, vertical, 0f).normalized;
                transform.position += direction * currentSpeed * Time.deltaTime;

                if (clampToBounds)
                {
                    float clampedX = Mathf.Clamp(transform.position.x, minBounds.x, maxBounds.x);
                    float clampedY = Mathf.Clamp(transform.position.y, minBounds.y, maxBounds.y);
                    transform.position = new Vector3(clampedX, clampedY, transform.position.z);
                }
            }
        }

        private void HandleZoom()
        {
            if (cam == null) return;

            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (scroll != 0)
            {
                cam.orthographicSize -= scroll * zoomSpeed * 3f;
            }

            if (Input.GetKey(KeyCode.KeypadPlus) || Input.GetKey(KeyCode.E))
            {
                cam.orthographicSize -= zoomSpeed * Time.deltaTime;
            }
            if (Input.GetKey(KeyCode.KeypadMinus) || Input.GetKey(KeyCode.Q))
            {
                cam.orthographicSize += zoomSpeed * Time.deltaTime;
            }

            cam.orthographicSize = Mathf.Clamp(cam.orthographicSize, minZoom, maxZoom);
        }

        private void HandleShortcuts()
        {
            // Atajo 'R' para regenerar el prado con otra semilla
            if (Input.GetKeyDown(KeyCode.R))
            {
                MeadowGenerator generator = FindObjectOfType<MeadowGenerator>();
                if (generator != null)
                {
                    generator.seed = Random.Range(1, 999999);
                    generator.GenerateMeadow();
                }
            }
        }

        private void OnGUI()
        {
            // Panel HUD informativo retro en pantalla
            GUI.color = new Color(1f, 1f, 1f, 0.95f);
            
            GUILayout.BeginArea(new Rect(16, 16, 440, 120), GUI.skin.box);
            GUILayout.Label("🌿 <b>SIMULADOR DE VIDA - MUNDO 160x120 (4X)</b>", GetRichTextStyle(14, new Color(0.4f, 1f, 0.4f)));
            GUILayout.Label("• <b>Especies:</b> Alien Gelatinoso (saltarín) & Makón con Garrote (andar cómico)", GetRichTextStyle(11, Color.white));
            GUILayout.Label("• <b>Entorno:</b> Mosaicos de Rocas infranqueables y Arboledas", GetRichTextStyle(11, new Color(0.8f, 0.8f, 0.8f)));
            GUILayout.Label("• <b>[Flechas / WASD]</b> Desplazar cámara  |  <b>[Shift]</b> Rápido", GetRichTextStyle(11, Color.white));
            GUILayout.Label("• <b>[Rueda Ratón / Q-E]</b> Zoom (x" + (cam != null ? cam.orthographicSize.ToString("F1") : "-") + ")", GetRichTextStyle(11, Color.white));
            GUILayout.Label("• <b>[Tecla R]</b> Regenerar mundo con nueva semilla", GetRichTextStyle(11, Color.yellow));
            GUILayout.EndArea();
        }

        private GUIStyle GetRichTextStyle(int size, Color color)
        {
            GUIStyle style = new GUIStyle(GUI.skin.label);
            style.fontSize = size;
            style.normal.textColor = color;
            style.richText = true;
            return style;
        }
    }
}
