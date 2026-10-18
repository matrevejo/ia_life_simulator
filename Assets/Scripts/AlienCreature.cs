using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using LifeSim.World;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace LifeSim.Creatures
{
    public enum AlienSpecies
    {
        Gelatinous, // Especie 1: Alienígena gelatinoso saltarín y flexible
        Makon       // Especie 2: Makón peludo con gran nariz, ojos minimalistas, garrote y andar cómico
    }

    public enum AlienState
    {
        Idle,           // Descansando / respirando en el sitio
        Wandering,      // Caminando hacia un punto aleatorio
        EatingGrass,    // Comiendo hierba o curioseando el suelo
        LookingAround,  // Mirando a los lados con curiosidad
        Attacking,      // Blandiendo y golpeando con el garrote de forma cómica
        Fleeing         // Huyendo de una perturbación o límite
    }

    public enum AlienFacing
    {
        Right,
        Left,
        Front,
        Back
    }

    [RequireComponent(typeof(SpriteRenderer))]
    public class AlienCreature : MonoBehaviour
    {
        [Header("Especie de Criatura")]
        public AlienSpecies species = AlienSpecies.Gelatinous;

        [Header("Personalización de Color")]
        [Tooltip("Color de tinte del ser alienígena. Fácilmente editable en Inspector o por código")]
        public Color bodyColor = Color.white;
        public bool randomColorOnStart = false;

        [Header("Configuración del Makón (Sin Armas)")]
        [Tooltip("Si el garrote es visible o si está oculto en el pelaje")]
        public bool hasWeaponVisible = false;
        [Range(0f, 0.5f)]
        [Tooltip("Probabilidad aleatoria de asestar un golpe con el garrote (0 = pacífico)")]
        public float attackChance = 0f;

        [Header("Sprites Gelatinoso (16x16)")]
        public Sprite gelIdle1;
        public Sprite gelIdle2;
        public Sprite gelWalk1;
        public Sprite gelWalk2;

        [Header("Sprites Makón (24x24 - Todas las Poses)")]
        // Vista lateral (Side)
        public Sprite makonSideIdle;
        public Sprite makonSideWalk1;
        public Sprite makonSideWalk2;
        public Sprite makonSideClubIdle;
        public Sprite makonSideClubWalk1;
        public Sprite makonSideClubWalk2;
        public Sprite makonSideClubAttack;

        // Vista frontal (Front)
        public Sprite makonFrontIdle;
        public Sprite makonFrontWalk1;
        public Sprite makonFrontWalk2;
        public Sprite makonFrontAttack;

        // Vista trasera (Back)
        public Sprite makonBackIdle;
        public Sprite makonBackWalk1;
        public Sprite makonBackWalk2;

        [Header("Parámetros de Movimiento")]
        [Range(0.5f, 5f)]
        public float moveSpeed = 2.0f;
        public float animSpeed = 6.0f;
        public float bounceHeight = 0.15f;

        [Header("Límites del Mundo")]
        public Vector2 minBounds = new Vector2(-78f, -58f);
        public Vector2 maxBounds = new Vector2(78f, 58f);

        [Header("Estado Actual (Rutina de Comportamiento)")]
        [SerializeField]
        private AlienState currentState = AlienState.Idle;
        public AlienState State => currentState;

        [SerializeField]
        private AlienFacing currentFacing = AlienFacing.Right;
        public AlienFacing Facing => currentFacing;

        // Variables de estado interno
        private SpriteRenderer sr;
        private Vector2 targetPosition;
        private float stateTimer = 0f;
        private float animTimer = 0f;

        // Paleta de colores alienígenas vibrantes para Gelatinosos
        public static readonly Color[] PresetAlienColors = new Color[]
        {
            new Color(1.00f, 0.42f, 0.65f), // Rosa Neón
            new Color(0.75f, 0.45f, 1.00f), // Violeta Cósmico
            new Color(0.25f, 0.82f, 0.95f), // Cian Eléctrico
            new Color(0.60f, 0.90f, 0.30f), // Lima Alienígena
            new Color(1.00f, 0.65f, 0.15f), // Ámbar Solar
            new Color(0.30f, 0.88f, 0.62f)  // Menta Esmeralda
        };

        // Paleta de colores para Makones: Tonos grises de piedra y variantes llamativas
        public static readonly Color[] PresetMakonColors = new Color[]
        {
            new Color(0.85f, 0.85f, 0.88f), // Pelaje Gris Ceniza Claro
            new Color(0.70f, 0.72f, 0.76f), // Pizarra Roca Gris
            new Color(0.92f, 0.92f, 0.95f), // Blanco Grisáceo Glacial
            new Color(0.58f, 0.60f, 0.65f), // Gris Carbón Suave
            new Color(0.95f, 0.48f, 0.62f), // Pelaje Rosa Salvaje
            new Color(0.42f, 0.82f, 0.92f), // Pelaje Azul Escarcha
            new Color(0.88f, 0.58f, 0.95f), // Pelaje Lila Makón
            new Color(1.00f, 0.72f, 0.30f), // Pelaje Ámbar León
            new Color(0.55f, 0.85f, 0.45f)  // Pelaje Musgo Primitivo
        };

        private void Awake()
        {
            sr = GetComponent<SpriteRenderer>();
            EnsureSpritesLoaded();
        }

        private void Start()
        {
            if (randomColorOnStart)
            {
                if (species == AlienSpecies.Makon)
                {
                    SetColor(PresetMakonColors[Random.Range(0, PresetMakonColors.Length)]);
                }
                else
                {
                    SetColor(PresetAlienColors[Random.Range(0, PresetAlienColors.Length)]);
                }
            }
            else
            {
                SetColor(bodyColor);
            }

            ConfigureSpeciesBehavior();

            // Iniciar con un estado aleatorio
            ChangeState(AlienState.Idle, Random.Range(1f, 3f));
        }

        /// <summary>
        /// Configura los parámetros de movimiento y animación según la especie.
        /// </summary>
        public void ConfigureSpeciesBehavior()
        {
            if (species == AlienSpecies.Makon)
            {
                // Makón: andar cómico, NO salta, pasos firmes con balanceo
                bounceHeight = 0f;
                moveSpeed = Mathf.Clamp(moveSpeed, 1.2f, 1.8f);
                animSpeed = 5.0f;
            }
            else
            {
                // Gelatinoso: rebotes saltarines en Y y movimientos rápidos
                bounceHeight = 0.16f;
                moveSpeed = Mathf.Clamp(moveSpeed, 1.8f, 2.6f);
                animSpeed = 6.0f;
            }
        }

        private void Update()
        {
            stateTimer -= Time.deltaTime;
            animTimer += Time.deltaTime * animSpeed;

            // Ejecución modular de la rutina según el estado actual
            switch (currentState)
            {
                case AlienState.Idle:
                    UpdateIdleRoutine();
                    break;
                case AlienState.Wandering:
                    UpdateWanderingRoutine();
                    break;
                case AlienState.LookingAround:
                    UpdateLookingAroundRoutine();
                    break;
                case AlienState.EatingGrass:
                    UpdateEatingGrassRoutine();
                    break;
                case AlienState.Attacking:
                    UpdateAttackingRoutine();
                    break;
                case AlienState.Fleeing:
                    UpdateFleeingRoutine();
                    break;
            }

            // Actualizar profundidad visual (Y-sorting para perspectiva top-down)
            // Base 1000 garantiza que siempre sea un orden positivo muy por encima de la hierba (-500)
            if (sr != null)
            {
                sr.sortingOrder = 1000 - Mathf.RoundToInt(transform.position.y * 10);
            }
        }

        #region --- RUTINAS MODULARES DE COMPORTAMIENTO ---

        /// <summary>
        /// Rutina en Reposo: Respira suavemente en el sitio.
        /// </summary>
        protected virtual void UpdateIdleRoutine()
        {
            transform.localRotation = Quaternion.Lerp(transform.localRotation, Quaternion.identity, Time.deltaTime * 10f);

            if (species == AlienSpecies.Makon)
            {
                ApplyMakonSprite("idle", 0);
            }
            else
            {
                int frame = (Mathf.FloorToInt(animTimer * 0.5f) % 4 == 0) ? 1 : 0;
                sr.sprite = (frame == 0) ? gelIdle1 : gelIdle2;
            }

            if (stateTimer <= 0f)
            {
                float roll = Random.value;
                if (species == AlienSpecies.Makon && roll < attackChance)
                {
                    // Golpear de manera aleatoria con el garrote
                    TriggerAttack(Random.Range(0.6f, 0.9f));
                }
                else if (roll < 0.65f)
                {
                    PickRandomDestination();
                    ChangeState(AlienState.Wandering, Random.Range(3f, 7f));
                }
                else if (roll < 0.85f)
                {
                    ChangeState(AlienState.LookingAround, Random.Range(1.5f, 3f));
                }
                else
                {
                    ChangeState(AlienState.EatingGrass, Random.Range(2f, 4f));
                }
            }
        }

        /// <summary>
        /// Rutina de Paseo: Camina hacia el destino respetando rocas y obstáculos.
        /// </summary>
        protected virtual void UpdateWanderingRoutine()
        {
            Vector2 currentPos = transform.position;
            Vector2 toTarget = targetPosition - currentPos;

            // Determinar orientación espacial (Front, Back, Side)
            UpdateFacing(toTarget);

            int stepIndex = Mathf.FloorToInt(animTimer) % 2 + 1; // 1 ó 2

            if (species == AlienSpecies.Makon)
            {
                ApplyMakonSprite("walk", stepIndex);

                // Andar cómico: balanceo lateral rítmico (waddle) con los dos piececitos
                float waddleAngle = Mathf.Sin(animTimer * 1.5f) * 8.5f;
                transform.localRotation = Quaternion.Euler(0f, 0f, waddleAngle);
            }
            else
            {
                sr.sprite = (stepIndex == 1) ? gelWalk1 : gelWalk2;
                sr.flipX = toTarget.x < 0;
                transform.localRotation = Quaternion.identity;
            }

            // Llegada al destino
            if (toTarget.magnitude <= 0.25f)
            {
                transform.localRotation = Quaternion.identity;
                ChangeState(AlienState.Idle, Random.Range(1.5f, 4f));
                return;
            }

            Vector2 moveDir = toTarget.normalized;
            Vector2 nextStep = moveDir * (moveSpeed * Time.deltaTime);
            Vector2 anticipatedPos = currentPos + nextStep;
            Vector2 probePoint = currentPos + moveDir * 0.45f; // Sonda hacia adelante para detectar rocas

            // Verificación lógica de obstáculos (Rocas infranqueables)
            if (MeadowGenerator.Instance != null && !MeadowGenerator.Instance.IsWalkable(probePoint))
            {
                transform.localRotation = Quaternion.identity;
                PickRandomDestination();
                ChangeState(AlienState.LookingAround, Random.Range(1f, 2f));
                return;
            }

            transform.position = anticipatedPos;

            if (stateTimer <= 0f)
            {
                transform.localRotation = Quaternion.identity;
                ChangeState(AlienState.Idle, Random.Range(1f, 3f));
            }
        }

        /// <summary>
        /// Rutina de Ataque: El Makón blande cómicamente su garrote en el aire o suelo.
        /// </summary>
        protected virtual void UpdateAttackingRoutine()
        {
            if (species == AlienSpecies.Makon)
            {
                ApplyMakonSprite("attack", 1);
                // Pequeña sacudida cómica hacia adelante al golpear
                float attackTilt = Mathf.Sin(stateTimer * 15f) * 10f;
                transform.localRotation = Quaternion.Euler(0f, 0f, attackTilt);
            }

            if (stateTimer <= 0f)
            {
                transform.localRotation = Quaternion.identity;
                ChangeState(AlienState.Idle, Random.Range(1f, 2f));
            }
        }

        /// <summary>
        /// Rutina de Curiosear: Mira a izquierda y derecha girando sobre sí mismo.
        /// </summary>
        protected virtual void UpdateLookingAroundRoutine()
        {
            transform.localRotation = Quaternion.identity;
            bool lookLeft = (Mathf.FloorToInt(animTimer) % 2 == 0);

            if (species == AlienSpecies.Makon)
            {
                currentFacing = lookLeft ? AlienFacing.Left : AlienFacing.Right;
                ApplyMakonSprite("idle", 0);
            }
            else
            {
                sr.sprite = gelIdle1;
                sr.flipX = lookLeft;
            }

            if (stateTimer <= 0f)
            {
                PickRandomDestination();
                ChangeState(AlienState.Wandering, Random.Range(2.5f, 5.5f));
            }
        }

        /// <summary>
        /// Rutina de Pastar / Comer: Se agacha rítmicamente simulando masticar hierba.
        /// </summary>
        protected virtual void UpdateEatingGrassRoutine()
        {
            transform.localRotation = Quaternion.identity;
            if (species == AlienSpecies.Makon)
            {
                ApplyMakonSprite("idle", 0);
            }
            else
            {
                sr.sprite = (Mathf.FloorToInt(animTimer * 2f) % 2 == 0) ? gelIdle2 : gelWalk1;
            }

            if (stateTimer <= 0f)
            {
                ChangeState(AlienState.Idle, Random.Range(1f, 2.5f));
            }
        }

        /// <summary>
        /// Rutina de Huida: Corre en dirección opuesta con paso apresurado.
        /// </summary>
        protected virtual void UpdateFleeingRoutine()
        {
            Vector2 currentPos = transform.position;
            Vector2 toTarget = targetPosition - currentPos;
            UpdateFacing(toTarget);

            if (species == AlienSpecies.Makon)
            {
                int stepIndex = Mathf.FloorToInt(animTimer * 1.5f) % 2 + 1;
                ApplyMakonSprite("walk", stepIndex);
                float waddleAngle = Mathf.Sin(animTimer * 2.5f) * 12.0f;
                transform.localRotation = Quaternion.Euler(0f, 0f, waddleAngle);
            }
            else
            {
                sr.sprite = (Mathf.FloorToInt(animTimer * 2f) % 2 == 0) ? gelWalk1 : gelWalk2;
                sr.flipX = toTarget.x < 0;
                transform.localRotation = Quaternion.identity;
            }

            Vector2 moveDir = toTarget.normalized;
            Vector2 nextStep = moveDir * (moveSpeed * 1.6f * Time.deltaTime);

            Vector2 probePoint = currentPos + moveDir * 0.45f;
            if (MeadowGenerator.Instance != null && !MeadowGenerator.Instance.IsWalkable(probePoint))
            {
                PickRandomDestination();
                ChangeState(AlienState.Idle, 1.0f);
                return;
            }

            transform.position = currentPos + nextStep;

            if (stateTimer <= 0f || toTarget.magnitude < 0.25f)
            {
                transform.localRotation = Quaternion.identity;
                ChangeState(AlienState.Idle, Random.Range(1f, 2f));
            }
        }

        #endregion

        #region --- SELECCIÓN DE SPRITES DEL MAKÓN POR POSES Y DIRECCIONES ---

        private void UpdateFacing(Vector2 toTarget)
        {
            if (Mathf.Abs(toTarget.y) > Mathf.Abs(toTarget.x) * 1.25f)
            {
                currentFacing = (toTarget.y < 0) ? AlienFacing.Front : AlienFacing.Back;
            }
            else
            {
                currentFacing = (toTarget.x < 0) ? AlienFacing.Left : AlienFacing.Right;
            }
        }

        private void ApplyMakonSprite(string action, int frameIdx)
        {
            sr.flipX = false;

            if (currentFacing == AlienFacing.Front)
            {
                if (action == "attack") sr.sprite = makonFrontAttack ?? makonFrontIdle;
                else if (action == "walk") sr.sprite = (frameIdx == 1) ? makonFrontWalk1 : makonFrontWalk2;
                else sr.sprite = makonFrontIdle;
            }
            else if (currentFacing == AlienFacing.Back)
            {
                if (action == "walk") sr.sprite = (frameIdx == 1) ? makonBackWalk1 : makonBackWalk2;
                else sr.sprite = makonBackIdle;
            }
            else // Left o Right
            {
                sr.flipX = (currentFacing == AlienFacing.Left);

                if (action == "attack")
                {
                    sr.sprite = makonSideClubAttack ?? makonSideClubIdle;
                }
                else if (action == "walk")
                {
                    if (hasWeaponVisible)
                    {
                        sr.sprite = (frameIdx == 1) ? makonSideClubWalk1 : makonSideClubWalk2;
                    }
                    else
                    {
                        sr.sprite = (frameIdx == 1) ? makonSideWalk1 : makonSideWalk2;
                    }
                }
                else // idle
                {
                    sr.sprite = hasWeaponVisible ? makonSideClubIdle : makonSideIdle;
                }
            }
        }

        #endregion

        #region --- CONTROL DE COLISIONES Y OBSTÁCULOS ---

        private void OnCollisionEnter2D(Collision2D collision)
        {
            // Rebotar y cambiar destino si choca contra una roca
            if (collision.gameObject.name.StartsWith("Rock") || collision.gameObject.name.StartsWith("Tree"))
            {
                PickRandomDestination();
                ChangeState(AlienState.LookingAround, 1.2f);
            }
        }

        #endregion

        #region --- CONFIGURACIÓN PÚBLICA ---

        public void SetSpecies(AlienSpecies newSpecies, Color color)
        {
            species = newSpecies;
            EnsureSpritesLoaded();
            ConfigureSpeciesBehavior();
            SetColor(color);

            // Asignar inmediatamente el sprite para que sea visible de inmediato (tanto en Play como en Edit Mode)
            if (species == AlienSpecies.Makon)
            {
                sr.sprite = hasWeaponVisible 
                    ? (makonSideClubIdle ?? makonFrontIdle ?? makonSideIdle) 
                    : (makonSideIdle ?? makonFrontIdle);
            }
            else
            {
                sr.sprite = gelIdle1;
            }
        }

        public void SetColor(Color newColor)
        {
            bodyColor = newColor;
            if (sr == null) sr = GetComponent<SpriteRenderer>();
            sr.color = newColor;
        }

        public void ChangeState(AlienState newState, float duration)
        {
            currentState = newState;
            stateTimer = duration;
        }

        public void TriggerAttack(float duration = 0.7f)
        {
            ChangeState(AlienState.Attacking, duration);
        }

        /// <summary>
        /// Escoge un destino aleatorio transitable libre de rocas.
        /// </summary>
        public void PickRandomDestination()
        {
            for (int attempt = 0; attempt < 15; attempt++)
            {
                float targetX = Random.Range(minBounds.x, maxBounds.x);
                float targetY = Random.Range(minBounds.y, maxBounds.y);
                Vector2 candidate = new Vector2(targetX, targetY);

                if (MeadowGenerator.Instance == null || MeadowGenerator.Instance.IsWalkable(candidate))
                {
                    targetPosition = candidate;
                    return;
                }
            }

            Vector2 current = transform.position;
            Vector2 smallShift = Random.insideUnitCircle * 4f;
            Vector2 fallback = current + smallShift;
            fallback.x = Mathf.Clamp(fallback.x, minBounds.x, maxBounds.x);
            fallback.y = Mathf.Clamp(fallback.y, minBounds.y, maxBounds.y);
            targetPosition = fallback;
        }

        public void SetWorldBounds(Vector2 min, Vector2 max)
        {
            minBounds = min;
            maxBounds = max;
        }

        public void EnsureSpritesLoaded()
        {
            // Sprites Gelatinoso
            if (gelIdle1 == null) gelIdle1 = LoadSpriteWithFallback("Creatures/alien_idle1", "Assets/Sprites/Creatures/alien_idle1.png", 16);
            if (gelIdle2 == null) gelIdle2 = LoadSpriteWithFallback("Creatures/alien_idle2", "Assets/Sprites/Creatures/alien_idle2.png", 16);
            if (gelWalk1 == null) gelWalk1 = LoadSpriteWithFallback("Creatures/alien_walk1", "Assets/Sprites/Creatures/alien_walk1.png", 16);
            if (gelWalk2 == null) gelWalk2 = LoadSpriteWithFallback("Creatures/alien_walk2", "Assets/Sprites/Creatures/alien_walk2.png", 16);

            // Sprites Makón (256x360 con animación de pies)
            if (makonSideIdle == null) makonSideIdle = LoadSpriteWithFallback("Creatures/makon_side_idle", "Assets/Sprites/Creatures/makon_side_idle.png", 200);
            if (makonSideWalk1 == null) makonSideWalk1 = LoadSpriteWithFallback("Creatures/makon_side_walk1", "Assets/Sprites/Creatures/makon_side_walk1.png", 200);
            if (makonSideWalk2 == null) makonSideWalk2 = LoadSpriteWithFallback("Creatures/makon_side_walk2", "Assets/Sprites/Creatures/makon_side_walk2.png", 200);
            if (makonSideClubIdle == null) makonSideClubIdle = LoadSpriteWithFallback("Creatures/makon_side_club_idle", "Assets/Sprites/Creatures/makon_side_club_idle.png", 200);
            if (makonSideClubWalk1 == null) makonSideClubWalk1 = LoadSpriteWithFallback("Creatures/makon_side_club_walk1", "Assets/Sprites/Creatures/makon_side_club_walk1.png", 200);
            if (makonSideClubWalk2 == null) makonSideClubWalk2 = LoadSpriteWithFallback("Creatures/makon_side_club_walk2", "Assets/Sprites/Creatures/makon_side_club_walk2.png", 200);
            if (makonSideClubAttack == null) makonSideClubAttack = LoadSpriteWithFallback("Creatures/makon_side_club_attack", "Assets/Sprites/Creatures/makon_side_club_attack.png", 200);

            if (makonFrontIdle == null) makonFrontIdle = LoadSpriteWithFallback("Creatures/makon_front_idle", "Assets/Sprites/Creatures/makon_front_idle.png", 200);
            if (makonFrontWalk1 == null) makonFrontWalk1 = LoadSpriteWithFallback("Creatures/makon_front_walk1", "Assets/Sprites/Creatures/makon_front_walk1.png", 200);
            if (makonFrontWalk2 == null) makonFrontWalk2 = LoadSpriteWithFallback("Creatures/makon_front_walk2", "Assets/Sprites/Creatures/makon_front_walk2.png", 200);
            if (makonFrontAttack == null) makonFrontAttack = LoadSpriteWithFallback("Creatures/makon_front_attack", "Assets/Sprites/Creatures/makon_front_attack.png", 200);

            if (makonBackIdle == null) makonBackIdle = LoadSpriteWithFallback("Creatures/makon_back_idle", "Assets/Sprites/Creatures/makon_back_idle.png", 200);
            if (makonBackWalk1 == null) makonBackWalk1 = LoadSpriteWithFallback("Creatures/makon_back_walk1", "Assets/Sprites/Creatures/makon_back_walk1.png", 200);
            if (makonBackWalk2 == null) makonBackWalk2 = LoadSpriteWithFallback("Creatures/makon_back_walk2", "Assets/Sprites/Creatures/makon_back_walk2.png", 200);
        }

        private static Sprite LoadSpriteWithFallback(string resourcePath, string assetPath, int ppu)
        {
            Sprite sp = Resources.Load<Sprite>(resourcePath);
#if UNITY_EDITOR
            if (sp == null)
            {
                sp = AssetDatabase.LoadAssetAtPath<Sprite>(assetPath);
            }
#endif
            if (sp == null)
            {
                Texture2D tex = Resources.Load<Texture2D>(resourcePath);
#if UNITY_EDITOR
                if (tex == null)
                {
                    tex = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
                }
#endif
                if (tex != null)
                {
                    sp = Sprite.Create(tex, new Rect(0f, 0f, tex.width, tex.height), new Vector2(0.5f, 0.5f), ppu);
                }
            }
            return sp;
        }

        #endregion
    }
}
