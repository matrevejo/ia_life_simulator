import zlib
import struct
import os

def write_png(filename, width, height, rgba_data):
    """Guarda un buffer RGBA en archivo PNG usando compresión zlib."""
    def chunk(chunk_type, data):
        return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
    
    header = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    
    raw_lines = []
    for y in range(height):
        start = y * width * 4
        end = start + width * 4
        raw_lines.append(b'\x00' + rgba_data[start:end])
    compressed = zlib.compress(b''.join(raw_lines), 9)
    
    with open(filename, 'wb') as f:
        f.write(header + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b''))

# =====================================================================
# 1. GENERACIÓN DE SERES ALIENÍGENAS (16x16 PIXEL ART GRACIOSO)
# =====================================================================
# Se diseñan en tonos monocromos/grises de alta pureza con detalles blancos y
# pupilas oscuras para que el SpriteRenderer.color de Unity los tiña de
# cualquier color vibrante (rosa chicle, lila, cian, lima, naranja) a la perfección.

T = (0, 0, 0, 0)            # Transparente
B_SH = (140, 140, 155, 255) # Sombra base del cuerpo
B_MD = (200, 205, 215, 255) # Cuerpo medio
B_HI = (250, 252, 255, 255) # Iluminación cuerpo
EYE_W = (255, 255, 255, 255)# Blanco del ojo
EYE_P = (25, 25, 35, 255)   # Pupila cómica
GLOW  = (255, 230, 80, 255) # Orbe brillante en la antena
BLUSH = (255, 150, 170, 255)# Mejilla graciosa

def create_alien_frame(frame_type="idle1"):
    grid = [[T for _ in range(16)] for _ in range(16)]
    
    if frame_type == "idle1":
        # Pose de reposo: cuerpo gelatinoso redondeado, antena recta con orbe, patas cortas
        # Antena y orbe
        grid[1][8] = GLOW
        grid[2][8] = GLOW
        grid[3][8] = B_MD
        grid[4][8] = B_MD
        
        # Cabeza y cuerpo superior (forma de pera cómica)
        for x in range(6, 11): grid[5][x] = B_HI
        for x in range(5, 12): grid[6][x] = B_MD
        for x in range(4, 13): grid[7][x] = B_MD
        for x in range(3, 14): grid[8][x] = B_MD
        for x in range(3, 14): grid[9][x] = B_MD
        for x in range(3, 14): grid[10][x] = B_MD
        for x in range(4, 13): grid[11][x] = B_SH
        for x in range(4, 13): grid[12][x] = B_SH
        
        # Patitas gelatinosas
        grid[13][5] = B_SH; grid[13][6] = B_SH
        grid[13][10] = B_SH; grid[13][11] = B_SH
        
        # Ojo gigante cómico en el centro
        for y in range(7, 10):
            for x in range(6, 11):
                grid[y][x] = EYE_W
        grid[8][8] = EYE_P; grid[8][9] = EYE_P
        grid[9][8] = EYE_P; grid[9][9] = EYE_P
        grid[7][7] = EYE_W # Brillo
        
        # Sonrisa cómica
        grid[11][7] = EYE_P; grid[11][8] = EYE_P; grid[11][9] = EYE_P
        # Sonrojo
        grid[10][4] = BLUSH; grid[10][12] = BLUSH
        
    elif frame_type == "idle2":
        # Pose de respiración/parpadeo: cuerpo ligeramente aplastado (squash) y antena inclinada
        grid[2][9] = GLOW
        grid[3][9] = GLOW
        grid[4][8] = B_MD
        grid[5][8] = B_MD
        
        for x in range(5, 12): grid[6][x] = B_HI
        for x in range(4, 13): grid[7][x] = B_MD
        for x in range(3, 14): grid[8][x] = B_MD
        for x in range(2, 15): grid[9][x] = B_MD
        for x in range(2, 15): grid[10][x] = B_MD
        for x in range(3, 14): grid[11][x] = B_SH
        for x in range(4, 13): grid[12][x] = B_SH
        
        grid[13][4] = B_SH; grid[13][5] = B_SH
        grid[13][11] = B_SH; grid[13][12] = B_SH
        
        # Ojo parpadeando (línea horizontal curvada graciosa)
        for x in range(6, 11): grid[8][x] = EYE_P
        grid[9][6] = EYE_P; grid[9][10] = EYE_P
        grid[11][7] = EYE_P; grid[11][8] = EYE_P; grid[11][9] = EYE_P
        grid[10][3] = BLUSH; grid[10][13] = BLUSH
        
    elif frame_type == "walk1":
        # Paso 1: pata izquierda levantada, cuerpo inclinado a la derecha
        grid[1][7] = GLOW; grid[2][7] = GLOW
        grid[3][8] = B_MD; grid[4][8] = B_MD
        
        for x in range(6, 11): grid[5][x] = B_HI
        for x in range(5, 12): grid[6][x] = B_MD
        for x in range(4, 13): grid[7][x] = B_MD
        for x in range(3, 14): grid[8][x] = B_MD
        for x in range(4, 14): grid[9][x] = B_MD
        for x in range(4, 13): grid[10][x] = B_MD
        for x in range(5, 13): grid[11][x] = B_SH
        for x in range(5, 12): grid[12][x] = B_SH
        
        # Pata izq arriba, pata der plantada
        grid[12][4] = B_SH
        grid[13][10] = B_SH; grid[13][11] = B_SH
        
        for y in range(7, 10):
            for x in range(7, 12): grid[y][x] = EYE_W
        grid[8][9] = EYE_P; grid[8][10] = EYE_P
        grid[9][9] = EYE_P; grid[9][10] = EYE_P
        grid[7][8] = EYE_W
        grid[11][8] = EYE_P; grid[11][9] = EYE_P
        
    elif frame_type == "walk2":
        # Paso 2: pata derecha levantada, cuerpo inclinado a la izquierda
        grid[1][9] = GLOW; grid[2][9] = GLOW
        grid[3][8] = B_MD; grid[4][8] = B_MD
        
        for x in range(5, 10): grid[5][x] = B_HI
        for x in range(4, 11): grid[6][x] = B_MD
        for x in range(3, 12): grid[7][x] = B_MD
        for x in range(2, 13): grid[8][x] = B_MD
        for x in range(2, 12): grid[9][x] = B_MD
        for x in range(3, 12): grid[10][x] = B_MD
        for x in range(3, 11): grid[11][x] = B_SH
        for x in range(4, 11): grid[12][x] = B_SH
        
        # Pata der arriba, pata izq plantada
        grid[13][4] = B_SH; grid[13][5] = B_SH
        grid[12][11] = B_SH
        
        for y in range(7, 10):
            for x in range(5, 10): grid[y][x] = EYE_W
        grid[8][7] = EYE_P; grid[8][8] = EYE_P
        grid[9][7] = EYE_P; grid[9][8] = EYE_P
        grid[7][6] = EYE_W
        grid[11][7] = EYE_P; grid[11][8] = EYE_P

    rgba = bytearray()
    for y in range(16):
        for x in range(16):
            rgba.extend(grid[y][x])
    return rgba

# =====================================================================
# 2. GENERACIÓN DE 8 SPRITES DE ÁRBOLES (32x32 EN TONOS MARRONES)
# =====================================================================
# Paleta de tonos marrones otoñales / bosque arcilloso:
BR_DEEP = (38, 24, 16, 255)   # Sombra corteza profunda
BR_DARK = (64, 40, 24, 255)   # Corteza oscura
BR_TRUNK= (96, 62, 38, 255)   # Tronco medio
BR_LIGHT= (138, 92, 56, 255)  # Realce tronco madera
F_DARK  = (72, 44, 24, 255)   # Follaje sombra marrón
F_MID   = (112, 68, 34, 255)  # Follaje marrón castaño
F_WARM  = (160, 96, 44, 255)  # Follaje ámbar cálido
F_LIGHT = (208, 134, 62, 255) # Follaje brillante iluminado
F_GOLD  = (240, 172, 88, 255) # Puntas de hojas doradas

def create_tree_sprite(tree_index):
    grid = [[T for _ in range(32)] for _ in range(32)]
    
    # Sombra del árbol en el suelo (común a todos en la base y=29..30)
    def draw_ground_shadow(cx, width):
        for dx in range(-width, width + 1):
            for dy in range(2):
                py = 29 + dy
                px = cx + dx
                if 0 <= px < 32 and 0 <= py < 32:
                    grid[py][px] = (15, 25, 15, 140)

    if tree_index == 0:
        # Árbol 1: Roble Otoñal Copa Redonda (Copa marrón cobriza frondosa)
        draw_ground_shadow(16, 8)
        # Tronco
        for y in range(20, 30):
            for x in range(14, 18):
                grid[y][x] = BR_TRUNK
                if x == 14: grid[y][x] = BR_LIGHT
                if x == 17: grid[y][x] = BR_DARK
        grid[29][13] = BR_DARK; grid[29][18] = BR_DARK
        
        # Copa redonda en capas
        for y in range(5, 22):
            for x in range(6, 26):
                dist = ((x - 16)**2 / 81.0) + ((y - 13)**2 / 49.0)
                if dist <= 1.0:
                    if dist > 0.8: grid[y][x] = F_DARK
                    elif y < 11 and x < 16: grid[y][x] = F_GOLD if (x+y)%2==0 else F_LIGHT
                    elif y < 15 and x < 18: grid[y][x] = F_WARM
                    elif y > 16: grid[y][x] = F_DARK
                    else: grid[y][x] = F_MID
                    
    elif tree_index == 1:
        # Árbol 2: Pino / Conífera Pardo de 3 pisos cónicos
        draw_ground_shadow(16, 7)
        for y in range(22, 30):
            for x in range(14, 18): grid[y][x] = BR_TRUNK
            
        tiers = [(4, 10, 5), (10, 16, 7), (16, 23, 9)]
        for top_y, bot_y, max_r in tiers:
            for y in range(top_y, bot_y):
                progress = (y - top_y) / float(bot_y - top_y)
                cur_r = int(max_r * progress) + 1
                for dx in range(-cur_r, cur_r + 1):
                    x = 16 + dx
                    if 0 <= x < 32:
                        if y == bot_y - 1: grid[y][x] = F_DARK
                        elif dx < 0 and y < top_y + 3: grid[y][x] = F_GOLD
                        elif dx <= 0: grid[y][x] = F_WARM
                        else: grid[y][x] = F_MID

    elif tree_index == 2:
        # Árbol 3: Tocón Antiguo / Árbol Hueco con ramas desnudas
        draw_ground_shadow(16, 7)
        for y in range(16, 30):
            for x in range(11, 21):
                if y > 18 and (x == 15 or x == 16):
                    grid[y][x] = BR_DEEP # Hueco interior
                elif x <= 13:
                    grid[y][x] = BR_LIGHT
                elif x >= 18:
                    grid[y][x] = BR_DARK
                else:
                    grid[y][x] = BR_TRUNK
        # Raíces
        grid[29][10] = BR_DARK; grid[29][21] = BR_DARK
        # Pequeño brote con hojas doradas
        grid[14][12] = BR_TRUNK; grid[13][11] = F_GOLD; grid[12][11] = F_LIGHT
        grid[15][19] = BR_TRUNK; grid[14][20] = F_WARM; grid[13][20] = F_GOLD

    elif tree_index == 3:
        # Árbol 4: Arbusto Grande Frondoso Cobre (Low Bush Tree)
        draw_ground_shadow(16, 10)
        for y in range(14, 29):
            for x in range(5, 27):
                dist = ((x - 16)**2 / 110.0) + ((y - 21)**2 / 36.0)
                if dist <= 1.0:
                    if y > 24 and dist > 0.6: grid[y][x] = F_DARK
                    elif y < 19 and x < 15: grid[y][x] = F_GOLD if (x+y)%2==0 else F_LIGHT
                    elif x < 17: grid[y][x] = F_WARM
                    else: grid[y][x] = F_MID
        # Ramitas visibles
        grid[27][15] = BR_DARK; grid[27][17] = BR_DARK

    elif tree_index == 4:
        # Árbol 5: Árbol Retorcido / Sauce Pardo Místico
        draw_ground_shadow(16, 8)
        # Tronco sinuoso curvado
        for y in range(15, 30):
            bend = int((25 - y) * 0.4)
            for dx in range(-2, 3):
                px = 16 + bend + dx
                if 0 <= px < 32:
                    grid[y][px] = BR_TRUNK if dx <= 0 else BR_DARK
        # Follaje colgante
        for cx, cy in [(11, 10), (17, 8), (22, 11), (9, 15), (24, 16)]:
            for y in range(cy - 4, cy + 5):
                for x in range(cx - 4, cx + 5):
                    if 0 <= x < 32 and 0 <= y < 32:
                        if (x - cx)**2 + (y - cy)**2 <= 14:
                            grid[y][x] = F_WARM if x < cx else F_MID
                            if y > cy + 2: grid[y][x] = F_DARK
                            if x == cx and y == cy - 3: grid[y][x] = F_GOLD

    elif tree_index == 5:
        # Árbol 6: Árbol Alto Estilizado (Tipo Álamo / Abedul Pardo)
        draw_ground_shadow(16, 5)
        # Tronco alto
        for y in range(18, 30):
            grid[y][15] = BR_LIGHT; grid[y][16] = BR_TRUNK; grid[y][17] = BR_DARK
        # Copa elíptica estilizada alta
        for y in range(3, 20):
            for x in range(10, 23):
                dist = ((x - 16)**2 / 24.0) + ((y - 11)**2 / 56.0)
                if dist <= 1.0:
                    if dist > 0.8: grid[y][x] = F_DARK
                    elif y < 9 and x < 16: grid[y][x] = F_GOLD
                    elif x < 17: grid[y][x] = F_WARM
                    else: grid[y][x] = F_MID

    elif tree_index == 6:
        # Árbol 7: Árbol de Bellotas / Vainas Silvestres
        draw_ground_shadow(16, 8)
        for y in range(20, 30):
            for x in range(14, 18): grid[y][x] = BR_TRUNK
        for y in range(6, 22):
            for x in range(7, 25):
                if ((x - 16)**2 / 72.0) + ((y - 14)**2 / 45.0) <= 1.0:
                    grid[y][x] = F_WARM if x < 16 else F_MID
                    if y > 17: grid[y][x] = F_DARK
        # Frutos / bayas ámbar colgantes
        for bx, by in [(11, 19), (14, 21), (19, 20), (22, 17)]:
            grid[by][bx] = F_GOLD
            grid[by+1][bx] = BR_DEEP

    elif tree_index == 7:
        # Árbol 8: Árbol Gemelo (Doble Tronco y Dos Copas)
        draw_ground_shadow(16, 9)
        # Tronco izquierdo y derecho
        for y in range(19, 30):
            grid[y][12] = BR_LIGHT; grid[y][13] = BR_TRUNK
            grid[y][18] = BR_TRUNK; grid[y][19] = BR_DARK
        # Copa izquierda
        for y in range(8, 20):
            for x in range(6, 17):
                if (x - 11)**2 + (y - 14)**2 <= 20:
                    grid[y][x] = F_WARM if x < 11 else F_MID
                    if y < 11 and x <= 11: grid[y][x] = F_GOLD
        # Copa derecha
        for y in range(6, 19):
            for x in range(14, 26):
                if (x - 20)**2 + (y - 12)**2 <= 24:
                    grid[y][x] = F_WARM if x < 20 else F_MID
                    if y < 9 and x <= 20: grid[y][x] = F_GOLD

    rgba = bytearray()
    for y in range(32):
        for x in range(32):
            rgba.extend(grid[y][x])
    return rgba

# =====================================================================
# EJECUCIÓN Y GUARDADO EN UNITY ASSETS Y RESOURCES
# =====================================================================
def main():
    dirs = [
        os.path.join("Assets", "Sprites", "Creatures"),
        os.path.join("Assets", "Resources", "Creatures"),
        os.path.join("Assets", "Sprites", "Trees"),
        os.path.join("Assets", "Resources", "Trees")
    ]
    for d in dirs: os.makedirs(d, exist_ok=True)
    
    # 1. Guardar Criaturas Alien (16x16)
    frames = ["idle1", "idle2", "walk1", "walk2"]
    for f in frames:
        rgba = create_alien_frame(f)
        for sub in ["Sprites", "Resources"]:
            path = os.path.join("Assets", sub, "Creatures", f"alien_{f}.png")
            write_png(path, 16, 16, rgba)
            print(f"-> Guardado {path}")
            
    # 2. Guardar 8 Árboles (32x32)
    tree_names = [
        "tree_01_autumn_oak",
        "tree_02_brown_pine",
        "tree_03_ancient_stump",
        "tree_04_copper_bush",
        "tree_05_gnarled_willow",
        "tree_06_tall_birch",
        "tree_07_amber_fruits",
        "tree_08_twin_trunk"
    ]
    for idx, tname in enumerate(tree_names):
        rgba = create_tree_sprite(idx)
        for sub in ["Sprites", "Resources"]:
            path = os.path.join("Assets", sub, "Trees", f"{tname}.png")
            write_png(path, 32, 32, rgba)
            print(f"-> Guardado {path}")

    # 3. Crear metadatos .meta pixel-perfect para los nuevos sprites
    # 16 PPU para las criaturas (para que midan 1 unidad en el mundo como 1 tile)
    # 32 PPU para los árboles (para que midan 1 tile exacto en el mundo)
    print("Generando metadatos .meta pixel-perfect...")
    
    template = """fileFormatVersion: 2
guid: REPLACE_GUID
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: REPLACE_PPU
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
"""
    import uuid
    for sub in ["Sprites", "Resources"]:
        for f in frames:
            p = os.path.join("Assets", sub, "Creatures", f"alien_{f}.png.meta")
            meta_str = template.replace("REPLACE_GUID", uuid.uuid4().hex).replace("REPLACE_PPU", "16")
            with open(p, "w", encoding="utf-8") as fp: fp.write(meta_str)
        for tname in tree_names:
            p = os.path.join("Assets", sub, "Trees", f"{tname}.png.meta")
            meta_str = template.replace("REPLACE_GUID", uuid.uuid4().hex).replace("REPLACE_PPU", "32")
            with open(p, "w", encoding="utf-8") as fp: fp.write(meta_str)
            
    print("¡Todos los sprites de criaturas y árboles generados con éxito!")

if __name__ == "__main__":
    main()
