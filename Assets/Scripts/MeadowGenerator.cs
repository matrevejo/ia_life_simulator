using System.Collections.Generic;
using UnityEngine;
using LifeSim.Creatures;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace LifeSim.World
{
    [ExecuteInEditMode]
    public class MeadowGenerator : MonoBehaviour
    {
        public static MeadowGenerator Instance { get; private set; }

        [Header("Dimensiones del Mundo (4X: 160x120 tiles)")]
        [Tooltip("Ancho del prado estático en tiles (4x de 40 = 160)")]
        [Range(20, 300)]
        public int width = 160;

        [Tooltip("Alto del prado estático en tiles (4x de 30 = 120)")]
        [Range(20, 300)]
        public int height = 120;

        [Header("Generación Aleatoria")]
        [Tooltip("Semilla para la distribución procedural")]
        public int seed = 777;

        [Tooltip("Generar automáticamente al iniciar el juego")]
        public bool generateOnStart = true;

        [Header("Frecuencia de Biomas (Ruido Perlin)")]
        [Range(0.01f, 0.2f)]
        public float organicNoiseScale = 0.06f;

        [Header("Sprites de Hierba (8 variantes 32x32)")]
        public Sprite[] grassSprites = new Sprite[8];

        [Header("Mosaico de Rocas (Obstáculos Coherentes 32x32)")]
        public Sprite[] rockSprites = new Sprite[8];
        [Range(0.01f, 0.1f)]
        public float rockNoiseScale = 0.045f;
        [Range(0.5f, 0.85f)]
        public float rockThreshold = 0.65f;
        [Tooltip("Rodea el mapa exterior con barreras rocosas")]
        public bool borderRocks = true;
        [Range(1, 4)]
        public int borderThickness = 2;

        [Header("Árboles Pardos (8 variantes 32x32 en grupos)")]
        public Sprite[] treeSprites = new Sprite[8];
        [Range(1, 30)]
        public int groveCount = 14;
        [Range(2, 10)]
        public int treesPerGroveMin = 3;
        [Range(3, 15)]
        public int treesPerGroveMax = 7;
        [Range(0f, 0.1f)]
        public float solitaryTreeChance = 0.02f;

        [Header("Población de Especies (Mundo Vivo)")]
        [Tooltip("Cantidad de alienígenas gelatinosos saltarines")]
        [Range(1, 80)]
        public int gelatinousCount = 18;

        [Tooltip("Cantidad de Makones peludos (sin armas, con animación de pies)")]
        [Range(1, 100)]
        public int makonCount = 36;

        [Range(0.8f, 4f)]
        public float baseMoveSpeed = 2.0f;

        [Header("Configuración de Renderizado")]
        public string sortingLayerName = "Default";

        // Cuadrícula lógica de transitabilidad para colisiones O(1)
        private bool[,] impassableGrid;
        private float currentOffsetX;
        private float currentOffsetY;

        private void Awake()
        {
            Instance = this;
            if (width < 160 || height < 120)
            {
                width = 160;
                height = 120;
            }
        }

        private void OnEnable()
        {
            Instance = this;
        }

        private void Start()
        {
            Instance = this;
            if (width < 160 || height < 120)
            {
                width = 160;
                height = 120;
            }

            if (Application.isPlaying && generateOnStart)
            {
                GenerateMeadow();
            }
        }

        /// <summary>
        /// Comprueba si una coordenada de mundo es transitable (libre de rocas, árboles y dentro de los límites).
        /// </summary>
        public bool IsWalkable(Vector2 worldPos)
        {
            int tx = Mathf.RoundToInt(worldPos.x - currentOffsetX);
            int ty = Mathf.RoundToInt(worldPos.y - currentOffsetY);

            if (tx < 0 || tx >= width || ty < 0 || ty >= height)
                return false;

            if (impassableGrid != null && impassableGrid[tx, ty])
                return false;

            return true;
        }

        [ContextMenu("Generar Prado en Escena")]
        public void GenerateMeadow()
        {
            Instance = this;

            if (width < 160 || height < 120)
            {
                width = 160;
                height = 120;
            }

            // 1. Cargar recursos si faltan
            EnsureSpritesLoaded();

            // 2. Limpiar elementos existentes
            ClearMeadow();

            // 3. Inicializar generador pseudo-aleatorio
            Random.InitState(seed);

            currentOffsetX = -width * 0.5f + 0.5f;
            currentOffsetY = -height * 0.5f + 0.5f;

            impassableGrid = new bool[width, height];
            HashSet<Vector2Int> occupiedTiles = new HashSet<Vector2Int>();

            // 4. Generar el fondo de hierba (160x120 tiles continuos)
            GenerateGrassTiles(currentOffsetX, currentOffsetY);

            // 5. Generar mosaicos y grupos de rocas que bloquean el paso
            GenerateRockMosaics(currentOffsetX, currentOffsetY, occupiedTiles);

            // 6. Generar arboledas en grupos de árboles pardos (32x32)
            GenerateTreeGroves(currentOffsetX, currentOffsetY, occupiedTiles);

            // 7. Generar las dos especies (Gelatinosos y Makones peludos)
            SpawnCreaturePopulations(currentOffsetX, currentOffsetY, occupiedTiles);

            Debug.Log($"[MeadowGenerator] ¡Mundo 4X generado con éxito! {width}x{height} tiles ({width * height} casillas), mosaicos de rocas infranqueables, {gelatinousCount} gelatinosos y {makonCount} makones.");
        }

        private void GenerateGrassTiles(float offsetX, float offsetY)
        {
            GameObject gridContainer = new GameObject("Meadow_Grass_Grid");
            gridContainer.transform.SetParent(transform);
            gridContainer.transform.localPosition = Vector3.zero;

            float flowerSeedX = (seed % 1000) * 17.31f;
            float flowerSeedY = (seed % 1000) * 31.17f;
            float cloverSeedX = (seed % 1000) * 43.19f;
            float cloverSeedY = (seed % 1000) * 59.83f;
            float detailSeedX = (seed % 1000) * 71.47f;
            float detailSeedY = (seed % 1000) * 89.23f;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    float flowerNoise = Mathf.PerlinNoise((x + flowerSeedX) * organicNoiseScale, (y + flowerSeedY) * organicNoiseScale);
                    float cloverNoise = Mathf.PerlinNoise((x + cloverSeedX) * organicNoiseScale, (y + cloverSeedY) * organicNoiseScale);
                    float detailNoise = Mathf.PerlinNoise((x + detailSeedX) * (organicNoiseScale * 2f), (y + detailSeedY) * (organicNoiseScale * 2f));
                    float randomJitter = Random.value;

                    int chosenIdx = 0;

                    if (flowerNoise > 0.68f)
                    {
                        chosenIdx = (randomJitter < 0.85f) ? 3 : 1; // Flores silvestres
                    }
                    else if (cloverNoise > 0.68f)
                    {
                        chosenIdx = (randomJitter < 0.85f) ? 4 : 1; // Tréboles
                    }
                    else if (detailNoise > 0.72f)
                    {
                        chosenIdx = 2; // Hierba densa
                    }
                    else
                    {
                        if (randomJitter < 0.48f) chosenIdx = 0;
                        else if (randomJitter < 0.78f) chosenIdx = 1;
                        else if (randomJitter < 0.88f) chosenIdx = 5;
                        else if (randomJitter < 0.94f) chosenIdx = 7;
                        else chosenIdx = 6;
                    }

                    chosenIdx = Mathf.Clamp(chosenIdx, 0, grassSprites.Length - 1);
                    Sprite spriteToUse = grassSprites[chosenIdx];

                    if (spriteToUse != null)
                    {
                        GameObject tileObj = new GameObject($"Grass_{x}_{y}");
                        tileObj.transform.SetParent(gridContainer.transform);
                        tileObj.transform.localPosition = new Vector3(x + offsetX, y + offsetY, 0f);

                        float spriteW = spriteToUse.rect.width / spriteToUse.pixelsPerUnit;
                        float spriteH = spriteToUse.rect.height / spriteToUse.pixelsPerUnit;
                        if (spriteW > 0 && spriteH > 0)
                        {
                            tileObj.transform.localScale = new Vector3((1.0f / spriteW) * 1.002f, (1.0f / spriteH) * 1.002f, 1f);
                        }

                        SpriteRenderer sr = tileObj.AddComponent<SpriteRenderer>();
                        sr.sprite = spriteToUse;
                        sr.sortingLayerName = sortingLayerName;
                        sr.sortingOrder = -500; // Capa base suelo: siempre al fondo por debajo de todo obstáculo o ser vivo
                    }
                }
            }
        }

        /// <summary>
        /// Genera formaciones de rocas variadas: rocas grandes, dos superpuestas, grupito de roquitas,
        /// losas y monolitos, formando barreras naturales coherentes.
        /// </summary>
        private void GenerateRockMosaics(float offsetX, float offsetY, HashSet<Vector2Int> occupiedTiles)
        {
            if (rockSprites == null || rockSprites.Length < 8 || rockSprites[0] == null) return;

            GameObject rocksContainer = new GameObject("Meadow_Rocks");
            rocksContainer.transform.SetParent(transform);
            rocksContainer.transform.localPosition = Vector3.zero;

            bool[,] isRock = new bool[width, height];
            float rSeedX = (seed % 1000) * 83.21f;
            float rSeedY = (seed % 1000) * 127.43f;

            // 1. Determinar celdas de roca (cordones rocosos interiores + bordes)
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    // Murallas exteriores protectoras del prado
                    if (borderRocks)
                    {
                        if (x < borderThickness || x >= width - borderThickness ||
                            y < borderThickness || y >= height - borderThickness)
                        {
                            isRock[x, y] = true;
                            continue;
                        }
                    }

                    // Afloramientos rocosos en grupos
                    float n = Mathf.PerlinNoise((x + rSeedX) * rockNoiseScale, (y + rSeedY) * rockNoiseScale);
                    float distFromCenter = Vector2.Distance(new Vector2(x, y), new Vector2(width * 0.5f, height * 0.5f));
                    float centerDampen = Mathf.Clamp01(distFromCenter / (width * 0.35f));

                    if (n > rockThreshold && centerDampen > 0.3f)
                    {
                        isRock[x, y] = true;
                    }
                }
            }

            // 2. Colocar los sprites de roca con variedad estética coherente
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    if (!isRock[x, y]) continue;

                    Vector2Int coord = new Vector2Int(x, y);
                    occupiedTiles.Add(coord);
                    impassableGrid[x, y] = true; // Bloqueo lógico O(1)

                    bool hasN = (y + 1 < height) && isRock[x, y + 1];
                    bool hasS = (y - 1 >= 0) && isRock[x, y - 1];
                    bool hasW = (x - 1 >= 0) && isRock[x - 1, y];
                    bool hasE = (x + 1 < width) && isRock[x + 1, y];

                    Sprite chosenSprite;

                    // Selección variada según densidad y vecinos:
                    // 0 = roca grande, 1 = dos superpuestas, 2 = grupito de roquitas,
                    // 3 = angular, 4 = losa musgosa, 5 = apiladas, 6 = plana, 7 = monolito
                    if (!hasN && !hasS && !hasW && !hasE)
                    {
                        // Roca aislada: 50% roca grande, 30% grupito, 20% monolito
                        float roll = Random.value;
                        if (roll < 0.50f) chosenSprite = rockSprites[0]; // rock_01_large_boulder
                        else if (roll < 0.80f) chosenSprite = rockSprites[2]; // rock_03_cluster_small
                        else chosenSprite = rockSprites[7]; // rock_08_monolith_pillar
                    }
                    else if (hasW || hasE)
                    {
                        // En cadena horizontal: alternar dos superpuestas y rocas angulares
                        float roll = Random.value;
                        if (roll < 0.45f) chosenSprite = rockSprites[1]; // rock_02_twin_overlapping
                        else if (roll < 0.75f) chosenSprite = rockSprites[3]; // rock_04_crag_angular
                        else chosenSprite = rockSprites[4]; // rock_05_mossy_slate
                    }
                    else
                    {
                        // En cadena vertical o centro: rocas apiladas o grandes
                        float roll = Random.value;
                        if (roll < 0.50f) chosenSprite = rockSprites[5]; // rock_06_stacked_stones
                        else if (roll < 0.80f) chosenSprite = rockSprites[0]; // rock_01_large_boulder
                        else chosenSprite = rockSprites[6]; // rock_07_flat_slab
                    }

                    if (chosenSprite == null) chosenSprite = rockSprites[0];

                    float worldX = x + offsetX;
                    float worldY = y + offsetY;

                    GameObject rockObj = new GameObject($"Rock_{x}_{y}");
                    rockObj.transform.SetParent(rocksContainer.transform);
                    rockObj.transform.localPosition = new Vector3(worldX, worldY, 0f);

                    float spriteW = chosenSprite.rect.width / chosenSprite.pixelsPerUnit;
                    float spriteH = chosenSprite.rect.height / chosenSprite.pixelsPerUnit;
                    if (spriteW > 0 && spriteH > 0)
                    {
                        rockObj.transform.localScale = new Vector3(1.0f / spriteW, 1.0f / spriteH, 1f);
                    }

                    SpriteRenderer sr = rockObj.AddComponent<SpriteRenderer>();
                    sr.sprite = chosenSprite;
                    sr.sortingLayerName = sortingLayerName;
                    sr.sortingOrder = 800 - Mathf.RoundToInt(worldY * 10);

                    // Colisionador físico que impide el paso de criaturas
                    BoxCollider2D boxCol = rockObj.AddComponent<BoxCollider2D>();
                    boxCol.size = new Vector2(0.95f, 0.95f);
                }
            }
        }

        private void GenerateTreeGroves(float offsetX, float offsetY, HashSet<Vector2Int> occupiedTiles)
        {
            if (treeSprites == null || treeSprites.Length == 0 || treeSprites[0] == null) return;

            GameObject treesContainer = new GameObject("Meadow_Trees");
            treesContainer.transform.SetParent(transform);
            treesContainer.transform.localPosition = Vector3.zero;

            // Arboledas en grupos
            for (int g = 0; g < groveCount; g++)
            {
                int centerGX = Random.Range(5, width - 6);
                int centerGY = Random.Range(5, height - 6);
                int treesInThisGrove = Random.Range(treesPerGroveMin, treesPerGroveMax + 1);

                for (int t = 0; t < treesInThisGrove; t++)
                {
                    int tx = centerGX + Random.Range(-3, 4);
                    int ty = centerGY + Random.Range(-3, 4);

                    tx = Mathf.Clamp(tx, 3, width - 4);
                    ty = Mathf.Clamp(ty, 3, height - 4);

                    Vector2Int coord = new Vector2Int(tx, ty);
                    if (occupiedTiles.Contains(coord)) continue;
                    occupiedTiles.Add(coord);
                    impassableGrid[tx, ty] = true;

                    CreateTreeInstance(tx, ty, offsetX, offsetY, treesContainer.transform);
                }
            }

            // Árboles solitarios dispersos
            for (int y = 4; y < height - 4; y += 4)
            {
                for (int x = 4; x < width - 4; x += 4)
                {
                    Vector2Int coord = new Vector2Int(x, y);
                    if (!occupiedTiles.Contains(coord) && Random.value < solitaryTreeChance)
                    {
                        occupiedTiles.Add(coord);
                        impassableGrid[x, y] = true;
                        CreateTreeInstance(x, y, offsetX, offsetY, treesContainer.transform);
                    }
                }
            }
        }

        private void CreateTreeInstance(int x, int y, float offsetX, float offsetY, Transform parent)
        {
            int treeIdx = Random.Range(0, treeSprites.Length);
            Sprite treeSprite = treeSprites[treeIdx];
            if (treeSprite == null) return;

            float worldX = x + offsetX;
            float worldY = y + offsetY;

            GameObject treeObj = new GameObject($"Tree_{x}_{y}");
            treeObj.transform.SetParent(parent);
            treeObj.transform.localPosition = new Vector3(worldX, worldY, 0f);

            float spriteW = treeSprite.rect.width / treeSprite.pixelsPerUnit;
            float spriteH = treeSprite.rect.height / treeSprite.pixelsPerUnit;
            if (spriteW > 0 && spriteH > 0)
            {
                treeObj.transform.localScale = new Vector3(1.0f / spriteW, 1.0f / spriteH, 1f);
            }

            SpriteRenderer sr = treeObj.AddComponent<SpriteRenderer>();
            sr.sprite = treeSprite;
            sr.sortingLayerName = sortingLayerName;
            sr.sortingOrder = 900 - Mathf.RoundToInt(worldY * 10);

            CircleCollider2D col = treeObj.AddComponent<CircleCollider2D>();
            col.offset = new Vector2(0f, -0.28f);
            col.radius = 0.25f;
        }

        /// <summary>
        /// Genera las poblaciones de ambas especies (Gelatinosos y Makones peludos con garrote)
        /// distribuidas en áreas transitables del mapa.
        /// </summary>
        private void SpawnCreaturePopulations(float offsetX, float offsetY, HashSet<Vector2Int> occupiedTiles)
        {
            GameObject creaturesContainer = new GameObject("Meadow_Creatures");
            creaturesContainer.transform.SetParent(transform);
            creaturesContainer.transform.localPosition = Vector3.zero;

            Vector2 minWorld = new Vector2(-width * 0.5f + 3f, -height * 0.5f + 3f);
            Vector2 maxWorld = new Vector2(width * 0.5f - 3f, height * 0.5f - 3f);

            // 1. Población de Gelatinosos (Especie 1)
            for (int i = 0; i < gelatinousCount; i++)
            {
                Vector2 spawnPos = FindValidWalkablePosition(offsetX, offsetY, occupiedTiles);
                Color gelColor = AlienCreature.PresetAlienColors[i % AlienCreature.PresetAlienColors.Length];

                CreateAlienInstance(creaturesContainer.transform, spawnPos, AlienSpecies.Gelatinous, gelColor,
                    $"Gelatinous_{i + 1}", minWorld, maxWorld, false);
            }

            // 2. Población de Makones Peludos (Especie 2, sin armas)
            for (int i = 0; i < makonCount; i++)
            {
                Vector2 spawnPos = FindValidWalkablePosition(offsetX, offsetY, occupiedTiles);
                Color makonColor = AlienCreature.PresetMakonColors[i % AlienCreature.PresetMakonColors.Length];
                // Makones sin armas
                bool hasClub = false;

                CreateAlienInstance(creaturesContainer.transform, spawnPos, AlienSpecies.Makon, makonColor,
                    $"Makon_{i + 1}", minWorld, maxWorld, hasClub);
            }
        }

        private Vector2 FindValidWalkablePosition(float offsetX, float offsetY, HashSet<Vector2Int> occupiedTiles)
        {
            for (int attempt = 0; attempt < 50; attempt++)
            {
                int sx = Random.Range(4, width - 5);
                int sy = Random.Range(4, height - 5);
                Vector2Int coord = new Vector2Int(sx, sy);

                if (!occupiedTiles.Contains(coord) && (impassableGrid == null || !impassableGrid[sx, sy]))
                {
                    occupiedTiles.Add(coord);
                    return new Vector2(sx + offsetX, sy + offsetY);
                }
            }

            return new Vector2(Random.Range(-5f, 5f), Random.Range(-5f, 5f));
        }

        private void CreateAlienInstance(Transform parent, Vector2 position, AlienSpecies species, Color color,
            string name, Vector2 minWorld, Vector2 maxWorld, bool hasWeapon)
        {
            GameObject alienObj = new GameObject(name);
            alienObj.transform.SetParent(parent);
            alienObj.transform.localPosition = new Vector3(position.x, position.y, 0f);

            SpriteRenderer sr = alienObj.AddComponent<SpriteRenderer>();
            sr.sortingLayerName = sortingLayerName;
            sr.sortingOrder = 1000 - Mathf.RoundToInt(position.y * 10);

            AlienCreature creature = alienObj.AddComponent<AlienCreature>();
            creature.hasWeaponVisible = hasWeapon;
            creature.SetWorldBounds(minWorld, maxWorld);
            creature.SetSpecies(species, color);

            CircleCollider2D col = alienObj.AddComponent<CircleCollider2D>();
            col.radius = 0.35f;

            Rigidbody2D rb = alienObj.AddComponent<Rigidbody2D>();
            rb.bodyType = RigidbodyType2D.Kinematic;
            rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        }

        [ContextMenu("Limpiar Todo")]
        public void ClearMeadow()
        {
            string[] containers = new string[] { "Meadow_Grass_Grid", "Meadow_Rocks", "Meadow_Mountains", "Meadow_Trees", "Meadow_Creatures", "Meadow_Grid" };
            foreach (var cName in containers)
            {
                Transform t = transform.Find(cName);
                if (t != null)
                {
                    if (Application.isPlaying) Destroy(t.gameObject);
                    else DestroyImmediate(t.gameObject);
                }
            }
        }

        public void EnsureSpritesLoaded()
        {
            // 1. Cargar Hierba
            string[] grassNames = new string[]
            {
                "grass_01_plain", "grass_02_tufts", "grass_03_dense", "grass_04_flowers",
                "grass_05_clover", "grass_06_wild_stalks", "grass_07_pebbles", "grass_08_morning_dew"
            };
            if (grassSprites == null || grassSprites.Length < 8) grassSprites = new Sprite[8];
            for (int i = 0; i < grassNames.Length; i++)
            {
                if (grassSprites[i] == null)
                {
                    grassSprites[i] = Resources.Load<Sprite>($"GrassTiles/{grassNames[i]}");
#if UNITY_EDITOR
                    if (grassSprites[i] == null)
                        grassSprites[i] = AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/GrassTiles/{grassNames[i]}.png");
#endif
                }
            }

            // 2. Cargar Árboles Pardos
            string[] treeNames = new string[]
            {
                "tree_01_autumn_oak", "tree_02_brown_pine", "tree_03_ancient_stump", "tree_04_copper_bush",
                "tree_05_gnarled_willow", "tree_06_tall_birch", "tree_07_amber_fruits", "tree_08_twin_trunk"
            };
            if (treeSprites == null || treeSprites.Length < 8) treeSprites = new Sprite[8];
            for (int i = 0; i < treeNames.Length; i++)
            {
                if (treeSprites[i] == null)
                {
                    treeSprites[i] = Resources.Load<Sprite>($"Trees/{treeNames[i]}");
#if UNITY_EDITOR
                    if (treeSprites[i] == null)
                        treeSprites[i] = AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Trees/{treeNames[i]}.png");
#endif
                }
            }

            // 3. Cargar Mosaico de Rocas (8 variantes coherentes en tonos grises)
            string[] rockNames = new string[]
            {
                "rock_01_large_boulder", "rock_02_twin_overlapping", "rock_03_cluster_small", "rock_04_crag_angular",
                "rock_05_mossy_slate", "rock_06_stacked_stones", "rock_07_flat_slab", "rock_08_monolith_pillar"
            };
            if (rockSprites == null || rockSprites.Length < 8) rockSprites = new Sprite[8];
            for (int i = 0; i < rockNames.Length; i++)
            {
                if (rockSprites[i] == null)
                {
                    rockSprites[i] = Resources.Load<Sprite>($"Rocks/{rockNames[i]}");
#if UNITY_EDITOR
                    if (rockSprites[i] == null)
                        rockSprites[i] = AssetDatabase.LoadAssetAtPath<Sprite>($"Assets/Sprites/Rocks/{rockNames[i]}.png");
#endif
                }
            }
        }
    }
}
