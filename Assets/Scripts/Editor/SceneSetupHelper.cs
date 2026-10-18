using UnityEditor;
using UnityEngine;
using LifeSim.World;

namespace LifeSim.Editor
{
    [InitializeOnLoad]
    public static class SceneSetupHelper
    {
        static SceneSetupHelper()
        {
            EditorApplication.delayCall += AutoSetupSceneIfEmpty;
        }

        private static void AutoSetupSceneIfEmpty()
        {
            // Solo actuar si no hay Meadow_Manager en la escena activa
            MeadowGenerator existing = Object.FindObjectOfType<MeadowGenerator>();
            if (existing == null && !Application.isPlaying)
            {
                SetupScene();
            }
        }

        [MenuItem("Tools/Pixel Art/Configurar Escena Completa (Meadow Manager + Cámara)")]
        public static void SetupScene()
        {
            // 0. Asegurar que las texturas estén importadas a 32 PPU y Point filter
            PixelArtAssetConfigurator.ConfigureGrassSprites();

            // 1. Configurar o buscar Meadow_Manager
            MeadowGenerator generator = Object.FindObjectOfType<MeadowGenerator>();
            if (generator == null)
            {
                GameObject meadowObj = new GameObject("Meadow_Manager");
                generator = meadowObj.AddComponent<MeadowGenerator>();
                Undo.RegisterCreatedObjectUndo(meadowObj, "Crear Meadow_Manager");
            }

            generator.width = 160;
            generator.height = 120;
            generator.seed = 777;
            generator.generateOnStart = true;
            generator.EnsureSpritesLoaded();

            // 2. Configurar Cámara Principal
            Camera mainCam = Camera.main;
            if (mainCam != null)
            {
                mainCam.orthographic = true;
                mainCam.orthographicSize = 18f;
                mainCam.transform.position = new Vector3(0f, 0f, -10f);
                mainCam.backgroundColor = new Color(0.05f, 0.08f, 0.06f, 1f);

                CameraController camCtrl = mainCam.GetComponent<CameraController>();
                if (camCtrl == null)
                {
                    camCtrl = Undo.AddComponent<CameraController>(mainCam.gameObject);
                }
                camCtrl.moveSpeed = 15f;
            }

            // 3. Generar una vista previa del prado en la escena del editor
            generator.GenerateMeadow();

            Debug.Log("[SceneSetupHelper] ¡Escena configurada con éxito con Meadow_Manager, los 8 Sprites y CameraController!");
            EditorUtility.SetDirty(generator);
        }
    }
}
