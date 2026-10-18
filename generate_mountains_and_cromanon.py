import zlib
import struct
import os
import uuid

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

T = (0, 0, 0, 0) # Transparente

# =====================================================================
# 1. ESPECIE CROMAÑÓN ALIENÍGENA (16x16 PIXEL ART BASADO EN EL BOCETO)
# =====================================================================
# Estructura: Cuerpo peludo rectangular con trazos verticales, gran nariz protuberante,
# ojo expresivo minimalista y dos patitas delgadas con andar gracioso (sin saltos).
# En tonos de grises graduados para teñirse a cualquier color fácilmente.

FUR_DARK  = (70, 75, 85, 255)   # Sombra de pelaje profundo
FUR_MID   = (130, 138, 150, 255)# Pelaje base medio
FUR_LIGHT = (195, 202, 215, 255)# Realce de pelos individuales
FUR_TIP   = (240, 245, 255, 255)# Puntas brillantes de pelos
NOSE_DARK = (150, 155, 165, 255)# Sombra inferior de la gran nariz
NOSE_MID  = (210, 215, 225, 255)# Cuerpo de la gran nariz
NOSE_HI   = (250, 252, 255, 255)# Brillo superior de la nariz
EYE_WHITE = (255, 255, 255, 255)# Esclera del ojo
EYE_PUPIL = (25, 30, 40, 255)   # Pupila cómica
LEG_COLOR = (55, 60, 70, 255)   # Patas delgadas

def create_cromanon_frame(frame_name="idle1"):
    grid = [[T for _ in range(16)] for _ in range(16)]
    
    # 1. Pelaje del cuerpo rectangular (x=1..7, y=1..12) con pelos puntiagudos arriba y abajo
    def draw_shaggy_body(offset_y=0, sway=0):
        # Picos de pelo arriba (y=0..1)
        for x, tip_y in [(1, 1), (2, 0), (3, 1), (4, 0), (5, 1), (6, 0), (7, 1)]:
            py = tip_y + offset_y
            if 0 <= py < 16: grid[py][x + sway] = FUR_TIP
            
        # Cuerpo principal con líneas verticales simulando el boceto a mano
        for y in range(2 + offset_y, 12 + offset_y):
            for x in range(1, 8):
                px = x + sway
                if 0 <= px < 16 and 0 <= y < 16:
                    # Trazos verticales alternos para dar textura peluda
                    if (px + y * 3) % 4 == 0:
                        grid[y][px] = FUR_LIGHT
                    elif (px + y) % 3 == 0:
                        grid[y][px] = FUR_DARK
                    else:
                        grid[y][px] = FUR_MID
                        
        # Mechones de pelo abajo (y=12)
        for x in range(1, 8):
            py = 12 + offset_y
            px = x + sway
            if 0 <= py < 16 and 0 <= px < 16:
                grid[py][px] = FUR_DARK if x % 2 == 0 else FUR_MID

    # 2. Gran nariz y ojo mirando hacia la derecha (perfil)
    def draw_face(offset_y=0, sway=0, nose_bob=0, blink=False):
        # Ojo minimalista (y=4..6, x=7..10)
        ey = 4 + offset_y
        ex = 7 + sway
        if blink:
            # Ojo cerrado (línea cómica)
            for dx in range(1, 4):
                if 0 <= ey + 1 < 16 and 0 <= ex + dx < 16:
                    grid[ey + 1][ex + dx] = EYE_PUPIL
        else:
            # Ojo abierto
            for dy in range(3):
                for dx in range(3):
                    py = ey + dy
                    px = ex + dx + 1
                    if 0 <= py < 16 and 0 <= px < 16:
                        grid[py][px] = EYE_WHITE
            # Pupila grande mirando hacia el frente/abajo
            if 0 <= ey + 1 < 16 and 0 <= ex + 3 < 16: grid[ey + 1][ex + 3] = EYE_PUPIL
            if 0 <= ey + 2 < 16 and 0 <= ex + 3 < 16: grid[ey + 2][ex + 3] = EYE_PUPIL

        # Gran nariz bulbosa (y=6..10, x=7..14)
        ny = 6 + offset_y + nose_bob
        for y in range(ny, ny + 4):
            # Longitud de la nariz horizontal
            length = 6 if (y == ny + 1 or y == ny + 2) else 5
            for dx in range(length):
                px = 7 + sway + dx
                if 0 <= y < 16 and 0 <= px < 16:
                    if y == ny:
                        grid[y][px] = NOSE_HI if dx > 2 else NOSE_MID
                    elif y == ny + 3 or dx == length - 1:
                        grid[y][px] = NOSE_DARK
                    else:
                        grid[y][px] = NOSE_MID

    # Variaciones de poses
    if frame_name == "idle1":
        draw_shaggy_body(offset_y=0, sway=0)
        draw_face(offset_y=0, sway=0, nose_bob=0, blink=False)
        # Patas en reposo: rectas con pie plano
        grid[13][3] = LEG_COLOR; grid[14][3] = LEG_COLOR; grid[15][2] = LEG_COLOR; grid[15][3] = LEG_COLOR; grid[15][4] = LEG_COLOR
        grid[13][6] = LEG_COLOR; grid[14][6] = LEG_COLOR; grid[15][6] = LEG_COLOR; grid[15][7] = LEG_COLOR; grid[15][8] = LEG_COLOR

    elif frame_name == "idle2":
        # Parpadeo y leve temblor cómico del pelo
        draw_shaggy_body(offset_y=0, sway=0)
        draw_face(offset_y=0, sway=0, nose_bob=1, blink=True)
        grid[13][3] = LEG_COLOR; grid[14][3] = LEG_COLOR; grid[15][2] = LEG_COLOR; grid[15][3] = LEG_COLOR; grid[15][4] = LEG_COLOR
        grid[13][6] = LEG_COLOR; grid[14][6] = LEG_COLOR; grid[15][6] = LEG_COLOR; grid[15][7] = LEG_COLOR; grid[15][8] = LEG_COLOR

    elif frame_name == "walk1":
        # Paso 1: pata izquierda adelante, pata derecha atrás (andar de zancada cómica)
        draw_shaggy_body(offset_y=0, sway=0)
        draw_face(offset_y=0, sway=0, nose_bob=0, blink=False)
        # Pata delantera (hacia la derecha/adelante)
        grid[13][6] = LEG_COLOR; grid[14][7] = LEG_COLOR; grid[15][7] = LEG_COLOR; grid[15][8] = LEG_COLOR; grid[15][9] = LEG_COLOR
        # Pata trasera (hacia la izquierda/atrás)
        grid[13][3] = LEG_COLOR; grid[14][2] = LEG_COLOR; grid[15][1] = LEG_COLOR; grid[15][2] = LEG_COLOR

    elif frame_name == "walk2":
        # Paso 2: pata derecha adelante, pata izquierda atrás, nariz se balancea
        draw_shaggy_body(offset_y=0, sway=1)
        draw_face(offset_y=0, sway=1, nose_bob=1, blink=False)
        # Pata delantera
        grid[13][4] = LEG_COLOR; grid[14][5] = LEG_COLOR; grid[15][5] = LEG_COLOR; grid[15][6] = LEG_COLOR; grid[15][7] = LEG_COLOR
        # Pata trasera extendida
        grid[13][7] = LEG_COLOR; grid[14][8] = LEG_COLOR; grid[15][8] = LEG_COLOR; grid[15][9] = LEG_COLOR

    rgba = bytearray()
    for y in range(16):
        for x in range(16):
            rgba.extend(grid[y][x])
    return rgba


# =====================================================================
# 2. SPRITES DE MONTAÑAS MOSAICO (32x32) PARA FORMAR CORDILLERAS
# =====================================================================
# Paleta de roca y granito con sombras profundas y aristas afiladas:
M_SHADOW  = (22, 26, 34, 255)   # Sombra de fisura rocosa profunda
M_DARK    = (45, 52, 65, 255)   # Roca oscura base
M_MID     = (75, 85, 105, 255)  # Granito gris pizarra
M_LIGHT   = (115, 128, 150, 255)# Realce de cara iluminada
M_PEAK    = (175, 190, 210, 255)# Cima clara / arista de nieve/roca
M_SNOW    = (230, 240, 250, 255)# Nieve de la cumbre
M_MOSS    = (55, 80, 45, 255)   # Musgo en las repisas rocosas

def create_mountain_sprite(tile_idx):
    grid = [[T for _ in range(32)] for _ in range(32)]

    if tile_idx == 0:
        # 1. mountain_01_peak: Pico rocoso superior con nieve y arista afilada
        # Cima en (16, 4)
        for y in range(4, 32):
            w = int((y - 4) * 0.55)
            for dx in range(-w, w + 1):
                x = 16 + dx
                if 0 <= x < 32:
                    if y < 10:
                        grid[y][x] = M_SNOW if dx <= 0 else M_PEAK
                    elif dx < 0:
                        grid[y][x] = M_LIGHT if (x + y) % 3 != 0 else M_MID
                    elif dx == 0:
                        grid[y][x] = M_PEAK
                    else:
                        grid[y][x] = M_DARK if (x + y) % 2 == 0 else M_SHADOW

    elif tile_idx == 1:
        # 2. mountain_02_slope_left: Ladera izquierda de montaña (desciende hacia la izquierda)
        for y in range(0, 32):
            startX = max(0, 28 - int(y * 0.9))
            for x in range(startX, 32):
                if x == startX:
                    grid[y][x] = M_PEAK
                elif x < startX + 6:
                    grid[y][x] = M_LIGHT
                else:
                    grid[y][x] = M_MID if y % 2 == 0 else M_LIGHT
                    
    elif tile_idx == 2:
        # 3. mountain_03_slope_right: Ladera derecha de montaña (sombreada)
        for y in range(0, 32):
            endX = min(31, 3 + int(y * 0.9))
            for x in range(0, endX + 1):
                if x == endX:
                    grid[y][x] = M_SHADOW
                elif x > endX - 5:
                    grid[y][x] = M_DARK
                else:
                    grid[y][x] = M_MID if (x + y) % 2 == 0 else M_DARK

    elif tile_idx == 3:
        # 4. mountain_04_cliff_center: Acantilado central (pared de roca maciza sin huecos)
        for y in range(0, 32):
            for x in range(0, 32):
                # Estratos y fracturas verticales
                if x in [8, 18, 26] and (y % 6 != 0):
                    grid[y][x] = M_SHADOW
                elif x < 15:
                    grid[y][x] = M_LIGHT if (x + y) % 4 == 0 else M_MID
                else:
                    grid[y][x] = M_DARK if (x + y) % 3 == 0 else M_MID
                if (x + y * 2) % 17 == 0 and y > 10:
                    grid[y][x] = M_MOSS # Repisa con musgo

    elif tile_idx == 4:
        # 5. mountain_05_base_left: Base izquierda con pedregal y unión al césped
        for y in range(0, 32):
            for x in range(0, 32):
                if y > 24 and x < 16:
                    if (x + y) % 2 == 0: grid[y][x] = M_MOSS
                    elif y == 31: pass # Conexión al césped
                    else: grid[y][x] = M_DARK
                else:
                    grid[y][x] = M_MID if x > 12 else M_DARK

    elif tile_idx == 5:
        # 6. mountain_06_base_center: Base central rocosa maciza
        for y in range(0, 32):
            for x in range(0, 32):
                if y > 26:
                    grid[y][x] = M_MOSS if (x + y) % 3 == 0 else M_DARK
                else:
                    grid[y][x] = M_MID if (x + y) % 2 == 0 else M_DARK
                if y > 20 and x % 5 == 0:
                    grid[y][x] = M_SHADOW

    elif tile_idx == 6:
        # 7. mountain_07_base_right: Base derecha con talud de grava
        for y in range(0, 32):
            for x in range(0, 32):
                if y > 24 and x > 16:
                    grid[y][x] = M_MOSS if (x + y) % 2 == 0 else M_SHADOW
                else:
                    grid[y][x] = M_DARK if x > 10 else M_MID

    elif tile_idx == 7:
        # 8. mountain_08_monolith: Risco / peñasco solitario imponente
        for y in range(6, 30):
            w = 8 if y < 14 else 12
            for dx in range(-w, w + 1):
                x = 16 + dx
                if 0 <= x < 32:
                    if dx < -w + 2 or dx > w - 2:
                        grid[y][x] = M_SHADOW if dx > 0 else M_PEAK
                    elif dx < 0:
                        grid[y][x] = M_LIGHT if y < 15 else M_MID
                    else:
                        grid[y][x] = M_DARK
        # Musgo en la cumbre
        for dx in range(-5, 6): grid[6][16 + dx] = M_MOSS

    rgba = bytearray()
    for y in range(32):
        for x in range(32):
            rgba.extend(grid[y][x])
    return rgba

# =====================================================================
# EJECUCIÓN PRINCIPAL: GUARDAR SPRITES Y GENERAR .META
# =====================================================================
def main():
    dirs = [
        os.path.join("Assets", "Sprites", "Creatures"),
        os.path.join("Assets", "Resources", "Creatures"),
        os.path.join("Assets", "Sprites", "Mountains"),
        os.path.join("Assets", "Resources", "Mountains")
    ]
    for d in dirs: os.makedirs(d, exist_ok=True)

    # 1. Guardar frames de Cromañón
    croma_frames = ["idle1", "idle2", "walk1", "walk2"]
    for f in croma_frames:
        rgba = create_cromanon_frame(f)
        for sub in ["Sprites", "Resources"]:
            path = os.path.join("Assets", sub, "Creatures", f"cromanon_{f}.png")
            write_png(path, 16, 16, rgba)
            print(f"-> Guardado {path}")

    # 2. Guardar 8 sprites de montaña
    mountain_names = [
        "mountain_01_peak",
        "mountain_02_slope_left",
        "mountain_03_slope_right",
        "mountain_04_cliff_center",
        "mountain_05_base_left",
        "mountain_06_base_center",
        "mountain_07_base_right",
        "mountain_08_monolith"
    ]
    for idx, mname in enumerate(mountain_names):
        rgba = create_mountain_sprite(idx)
        for sub in ["Sprites", "Resources"]:
            path = os.path.join("Assets", sub, "Mountains", f"{mname}.png")
            write_png(path, 32, 32, rgba)
            print(f"-> Guardado {path}")

    # 3. Metadatos .meta
    meta_template = """fileFormatVersion: 2
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
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
  spriteMode: 1
  spritePixelsToUnits: REPLACE_PPU
  textureType: 8
  textureShape: 1
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    textureFormat: -1
    textureCompression: 0
"""
    for sub in ["Sprites", "Resources"]:
        for f in croma_frames:
            p = os.path.join("Assets", sub, "Creatures", f"cromanon_{f}.png.meta")
            m = meta_template.replace("REPLACE_GUID", uuid.uuid4().hex).replace("REPLACE_PPU", "16")
            with open(p, "w", encoding="utf-8") as fp: fp.write(m)
        for mname in mountain_names:
            p = os.path.join("Assets", sub, "Mountains", f"{mname}.png.meta")
            m = meta_template.replace("REPLACE_GUID", uuid.uuid4().hex).replace("REPLACE_PPU", "32")
            with open(p, "w", encoding="utf-8") as fp: fp.write(m)

    print("¡Sprites de Cromañón y Montañas generados con éxito!")

if __name__ == "__main__":
    main()
