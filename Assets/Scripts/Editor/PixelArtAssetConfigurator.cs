using UnityEditor;
using UnityEngine;

namespace LifeSim.Editor
{
    public static class PixelArtAssetConfigurator
    {
        [MenuItem("Tools/Pixel Art/Configurar Sprites de Hierba (32 PPU, Point, Sin Compresión)")]
        public static void ConfigureGrassSpritesMenu()
        {
            ConfigureGrassSprites(true);
        }

        public static void ConfigureGrassSprites(bool showDialog = false)
        {
            string[] folderPaths = new string[] 
            { 
                "Assets/Sprites/GrassTiles", "Assets/Resources/GrassTiles",
                "Assets/Sprites/Trees", "Assets/Resources/Trees",
                "Assets/Sprites/Creatures", "Assets/Resources/Creatures",
                "Assets/Sprites/Rocks", "Assets/Resources/Rocks",
                "Assets/Sprites/Mountains", "Assets/Resources/Mountains"
            };
            string[] guids = AssetDatabase.FindAssets("t:Texture2D", folderPaths);

            int count = 0;
            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;

                if (importer != null)
                {
                    bool changed = false;
                    int targetPPU = path.Contains("Creatures") ? 16 : 32;

                    if (importer.textureType != TextureImporterType.Sprite) { importer.textureType = TextureImporterType.Sprite; changed = true; }
                    if (importer.spritePixelsPerUnit != targetPPU) { importer.spritePixelsPerUnit = targetPPU; changed = true; }
                    if (importer.filterMode != FilterMode.Point) { importer.filterMode = FilterMode.Point; changed = true; }
                    if (importer.textureCompression != TextureImporterCompression.Uncompressed) { importer.textureCompression = TextureImporterCompression.Uncompressed; changed = true; }
                    if (importer.mipmapEnabled) { importer.mipmapEnabled = false; changed = true; }
                    if (!importer.alphaIsTransparency) { importer.alphaIsTransparency = true; changed = true; }
                    if (importer.npotScale != TextureImporterNPOTScale.None) { importer.npotScale = TextureImporterNPOTScale.None; changed = true; }

                    if (changed)
                    {
                        TextureImporterPlatformSettings settings = importer.GetDefaultPlatformTextureSettings();
                        settings.textureCompression = TextureImporterCompression.Uncompressed;
                        settings.format = TextureImporterFormat.RGBA32;
                        importer.SetPlatformTextureSettings(settings);

                        EditorUtility.SetDirty(importer);
                        importer.SaveAndReimport();
                        count++;
                    }
                }
            }

            AssetDatabase.Refresh();
            Debug.Log($"[PixelArtAssetConfigurator] Se verificaron/configuraron {count} sprites para Pixel Art (32 PPU, Point filter, RGBA32).");
            if (showDialog)
            {
                EditorUtility.DisplayDialog("Pixel Art Configurado", $"Se han configurado {count} sprites con éxito para pixel art perfecto.", "Aceptar");
            }
        }
    }
}
