import zlib
import struct
import os
import uuid

def write_png(filename, width, height, rgba_data):
    """Guarda un buffer RGBA en archivo PNG usando compresión zlib pura."""
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

def create_meta_file(filepath, ppu=32):
    meta_path = filepath + ".meta"
    # Generar GUID determinista o único
    file_id = os.path.basename(filepath)
    guid = uuid.uuid5(uuid.NAMESPACE_DNS, f"lifesim_{file_id}_{ppu}").hex
    meta_content = f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
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
  spritePixelsToUnits: {ppu}
  textureType: 8
  textureShape: 1
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    textureFormat: -1
    textureCompression: 0
"""
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(meta_content)

T = (0, 0, 0, 0)

# =====================================================================
# 1. GENERACIÓN DE ROCAS (8 VARIANTES 32x32 EN TONOS GRISES)
# =====================================================================
# Variedad solicitada por el usuario:
# 1 roca grande, 2 pequeñas superpuestas, un grupito de roquitas, etc.

ROCK_OUTLINE = (28, 34, 42, 255)    # Contorno y grietas profundas
ROCK_DARK    = (58, 66, 78, 255)    # Sombra intensa inferior
ROCK_SHADOW  = (88, 98, 112, 255)   # Sombra media
ROCK_BASE    = (125, 138, 154, 255) # Gris medio roca base
ROCK_LIGHT   = (170, 182, 198, 255) # Gris claro iluminación superior
ROCK_HI      = (215, 225, 238, 255) # Brillo especular y aristas
ROCK_MOSS    = (75, 110, 65, 255)   # Detalle sutil de musgo en la base
MOSS_LIGHT   = (105, 145, 85, 255)

def draw_oval(grid, cx, cy, rx, ry, color):
    for y in range(32):
        for x in range(32):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            if dx*dx + dy*dy <= 1.0:
                grid[y][x] = color

def create_rock_large_boulder():
    """Roca 1: Una roca grande imponente con volumen, relieve y aristas."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    # Base en el suelo (y=8..10), cima arriba (y=20..22)
    draw_oval(grid, 16, 9, 13, 7.5, ROCK_OUTLINE)
    draw_oval(grid, 16, 10, 12, 7, ROCK_DARK)
    draw_oval(grid, 16, 12, 11.5, 6.8, ROCK_SHADOW)
    draw_oval(grid, 15.5, 14, 11, 6.5, ROCK_BASE)
    draw_oval(grid, 15, 17, 9.5, 5.5, ROCK_LIGHT)
    draw_oval(grid, 14, 19, 7, 4.0, ROCK_HI)
    
    # Grietas y facetas angulares
    for x in range(12, 21):
        if x in (14, 15, 16):
            grid[14][x] = ROCK_OUTLINE
            grid[13][x+1] = ROCK_DARK
    # Musgo base en el suelo (y=4..7)
    for x in [8, 9, 10, 21, 22, 23]:
        grid[6][x] = ROCK_MOSS
        grid[7][x] = MOSS_LIGHT
    return grid

def create_rock_twin_overlapping():
    """Roca 2: Dos rocas medianas superpuestas (una detrás, otra delante)."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    # Roca trasera (izquierda)
    draw_oval(grid, 11, 14, 8, 5.5, ROCK_OUTLINE)
    draw_oval(grid, 11, 15, 7.2, 4.8, ROCK_DARK)
    draw_oval(grid, 10.5, 16.5, 6.5, 4.2, ROCK_BASE)
    draw_oval(grid, 10, 18, 5, 3.2, ROCK_LIGHT)
    draw_oval(grid, 9.5, 19.5, 3, 2, ROCK_HI)
    
    # Roca delantera (derecha, solapa sobre la trasera)
    draw_oval(grid, 20, 9, 8.5, 6, ROCK_OUTLINE)
    draw_oval(grid, 20, 10, 7.8, 5.2, ROCK_DARK)
    draw_oval(grid, 19.5, 11.5, 7, 4.8, ROCK_SHADOW)
    draw_oval(grid, 19, 13.5, 6.5, 4.2, ROCK_BASE)
    draw_oval(grid, 18.5, 15.5, 5, 3.2, ROCK_LIGHT)
    draw_oval(grid, 18, 17, 3.5, 2, ROCK_HI)
    
    # Sombra proyectada entre ambas
    for y in range(10, 15):
        grid[y][14] = ROCK_OUTLINE
    # Musgo en el suelo
    grid[6][11] = ROCK_MOSS
    grid[5][20] = ROCK_MOSS
    return grid

def create_rock_cluster_small():
    """Roca 3: Un grupito de 4-5 roquitas y piedras dispersas sobre la hierba."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    # Piedra central izquierda
    draw_oval(grid, 10, 12, 5.5, 4, ROCK_OUTLINE)
    draw_oval(grid, 10, 13, 4.8, 3.4, ROCK_SHADOW)
    draw_oval(grid, 9.5, 14, 4.0, 2.8, ROCK_BASE)
    draw_oval(grid, 9.5, 15.5, 3, 2, ROCK_LIGHT)
    draw_oval(grid, 9, 16.5, 1.8, 1.2, ROCK_HI)

    # Piedra central derecha
    draw_oval(grid, 19, 13, 6, 4.5, ROCK_OUTLINE)
    draw_oval(grid, 19, 14, 5.2, 3.8, ROCK_SHADOW)
    draw_oval(grid, 18.5, 15, 4.5, 3.0, ROCK_BASE)
    draw_oval(grid, 18.5, 16.5, 3.5, 2.2, ROCK_LIGHT)
    draw_oval(grid, 18, 17.5, 2, 1.3, ROCK_HI)

    # Piedrecita delantera (más cerca del suelo)
    draw_oval(grid, 15, 8, 4, 2.8, ROCK_OUTLINE)
    draw_oval(grid, 15, 8.5, 3.4, 2.2, ROCK_SHADOW)
    draw_oval(grid, 14.5, 10, 2.5, 1.6, ROCK_BASE)
    draw_oval(grid, 14.5, 11, 1.8, 1.0, ROCK_LIGHT)

    # Piedrecita trasera
    draw_oval(grid, 14, 17, 3.5, 2.5, ROCK_OUTLINE)
    draw_oval(grid, 14, 17.5, 2.8, 1.8, ROCK_BASE)
    draw_oval(grid, 13.5, 19, 1.8, 1.2, ROCK_LIGHT)
    draw_oval(grid, 13.5, 20, 1.2, 0.8, ROCK_HI)

    # Guijarrito suelto
    draw_oval(grid, 25, 9, 2.2, 1.6, ROCK_OUTLINE)
    draw_oval(grid, 25, 9.5, 1.6, 1.1, ROCK_LIGHT)
    return grid

def create_rock_crag_angular():
    """Roca 4: Roca angular y puntiaguda con facetas afiladas."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    draw_oval(grid, 16, 10, 11, 6.5, ROCK_OUTLINE)
    draw_oval(grid, 16, 11, 10, 5.5, ROCK_DARK)
    
    # Faceta izquierda iluminada
    for y in range(10, 22):
        for x in range(8, 16):
            if (16 - x) + (22 - y)*0.8 < 9:
                grid[y][x] = ROCK_LIGHT
                if x < 12 and y > 17:
                    grid[y][x] = ROCK_HI
    # Arista central divisoria
    for y in range(10, 22):
        grid[y][15] = ROCK_OUTLINE
    # Faceta derecha en sombra
    for y in range(9, 20):
        for x in range(16, 24):
            if (x - 16) + (20 - y)*0.8 < 8:
                grid[y][x] = ROCK_SHADOW
    return grid

def create_rock_mossy_slate():
    """Roca 5: Roca estratificada con losas horizontales y líquenes."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    draw_oval(grid, 16, 10, 13, 6, ROCK_OUTLINE)
    draw_oval(grid, 16, 11, 12, 5, ROCK_DARK)
    draw_oval(grid, 15.5, 13, 11.5, 4.5, ROCK_BASE)
    draw_oval(grid, 15, 15, 10, 3.8, ROCK_LIGHT)
    draw_oval(grid, 14.5, 17, 8, 2.8, ROCK_HI)
    
    for x in range(7, 24):
        grid[13][x] = ROCK_OUTLINE
        grid[11][x] = ROCK_SHADOW
    for x in (8, 9, 10, 18, 19, 22):
        grid[8][x] = ROCK_MOSS
        grid[9][x] = MOSS_LIGHT
    return grid

def create_rock_stacked_stones():
    """Roca 6: Rocas apiladas (cairn) en equilibrio."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    # Roca inferior grande en el suelo (y=8..12)
    draw_oval(grid, 16, 8, 11, 4.5, ROCK_OUTLINE)
    draw_oval(grid, 16, 9, 10, 3.8, ROCK_SHADOW)
    draw_oval(grid, 15.5, 10, 9, 3.2, ROCK_BASE)
    draw_oval(grid, 15, 11, 7, 2.2, ROCK_LIGHT)
    
    # Roca intermedia (y=13..17)
    draw_oval(grid, 16, 15, 7.5, 3.8, ROCK_OUTLINE)
    draw_oval(grid, 16, 15.5, 6.8, 3.2, ROCK_SHADOW)
    draw_oval(grid, 15.5, 16.5, 6, 2.6, ROCK_BASE)
    draw_oval(grid, 15, 17.5, 4.5, 1.8, ROCK_LIGHT)
    draw_oval(grid, 14.5, 18.5, 2.5, 1.0, ROCK_HI)

    # Roca superior pequeña (y=19..23)
    draw_oval(grid, 16, 21, 4.5, 2.5, ROCK_OUTLINE)
    draw_oval(grid, 16, 21.5, 3.8, 2.0, ROCK_BASE)
    draw_oval(grid, 15.5, 22.5, 2.5, 1.3, ROCK_LIGHT)
    draw_oval(grid, 15, 23.2, 1.5, 0.8, ROCK_HI)
    return grid

def create_rock_flat_slab():
    """Roca 7: Losa de piedra baja y ancha sobre el césped."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    draw_oval(grid, 16, 9, 14, 5.0, ROCK_OUTLINE)
    draw_oval(grid, 16, 10, 13, 4.2, ROCK_DARK)
    draw_oval(grid, 15.5, 11.5, 12, 3.6, ROCK_BASE)
    draw_oval(grid, 15, 13, 10.5, 2.8, ROCK_LIGHT)
    draw_oval(grid, 14, 14.5, 8, 2.0, ROCK_HI)
    
    grid[12][12] = ROCK_OUTLINE
    grid[11][13] = ROCK_DARK
    grid[13][20] = ROCK_OUTLINE
    return grid

def create_rock_monolith_pillar():
    """Roca 8: Pilar / monolito vertical alto."""
    grid = [[T for _ in range(32)] for _ in range(32)]
    # Base ancha en el suelo (y=8..10)
    draw_oval(grid, 16, 8, 10, 4.5, ROCK_OUTLINE)
    draw_oval(grid, 16, 9, 9, 3.8, ROCK_DARK)
    
    # Columna vertical (y=9..23)
    for y in range(9, 24):
        for x in range(11, 21):
            grid[y][x] = ROCK_OUTLINE
    for y in range(10, 23):
        for x in range(12, 20):
            if x <= 15:
                grid[y][x] = ROCK_LIGHT
                if x == 12 or y == 22:
                    grid[y][x] = ROCK_HI
            else:
                grid[y][x] = ROCK_SHADOW
                if x == 19:
                    grid[y][x] = ROCK_DARK
    # Cima redondeada (y=24)
    grid[24][14] = ROCK_HI
    grid[24][15] = ROCK_HI
    grid[25][14] = ROCK_OUTLINE
    grid[25][15] = ROCK_OUTLINE
    return grid

# =====================================================================
# 2. ESPECIE MAKÓN (24x24 PIXEL ART BASADO EN EL NUEVO BOCETO)
# =====================================================================
# Poses requeridas:
# - Mirando hacia los lados (con y sin garrote, andando y golpeando)
# - Mirando hacia adelante (dos ojos, nariz separada abajo, brazos a los lados)
# - Mirando hacia atrás (espalda peluda pura)
# - Nariz separada de los ojos, ojos un poco más arriba, nariz un poco más pequeña
# - Garrote visible o escondido en el pelo

FUR_DEEP   = (45, 48, 56, 255)   # Sombra negra/carbón de pelo
FUR_DARK   = (80, 85, 96, 255)   # Pelo oscuro base
FUR_MID    = (140, 148, 162, 255)# Pelo gris medio
FUR_LIGHT  = (205, 212, 224, 255)# Pelo claro mechones
FUR_TIP    = (248, 250, 255, 255)# Mechones iluminados blancos

EYE_WHITE  = (255, 255, 255, 255)# Blanco de ojos
EYE_PUPIL  = (20, 24, 30, 255)   # Pupila atenta
NOSE_DARK  = (135, 140, 150, 255)# Sombra inferior de la nariz redondeada
NOSE_LIGHT = (230, 235, 245, 255)# Brillo de la nariz
LEG_COLOR  = (50, 54, 62, 255)   # Piernas delgadas tipo palo
CLUB_WOOD  = (138, 92, 54, 255)  # Garrote de madera parda
CLUB_DARK  = (92, 58, 32, 255)   # Veta oscura del garrote
CLUB_LIGHT = (185, 135, 85, 255) # Iluminación de la madera del garrote

def create_makon_sprite(view="side", weapon=False, anim="idle", leg_frame=0):
    """
    view: 'side', 'front', 'back'
    weapon: True, False
    anim: 'idle', 'walk', 'attack'
    leg_frame: 0, 1, 2
    Canvas: 24x24 pixels.
    """
    grid = [[T for _ in range(24)] for _ in range(24)]
    
    # -------------------------------------------------------------
    # VISTA LATERAL (SIDE VIEW)
    # -------------------------------------------------------------
    if view == "side":
        body_x_min = 6
        body_x_max = 14
        body_y_min = 4
        body_y_max = 18
        
        # 1. Arma: Garrote (si está activo)
        if weapon:
            if anim == "attack":
                # Golpeando con el garrote hacia adelante (swing)
                # Garrote proyectado hacia el frente en diagonal
                for i in range(7):
                    gx = 14 + i
                    gy = 10 + int(i * 0.4)
                    thickness = 1 + int(i * 0.35)
                    for ty in range(gy - thickness, gy + thickness + 1):
                        if 0 <= gx < 24 and 0 <= ty < 24:
                            grid[ty][gx] = CLUB_WOOD if ty == gy else CLUB_DARK
                # Cabeza gorda del garrote
                for dx in range(3):
                    for dy in range(4):
                        gx = 19 + dx
                        gy = 11 + dy
                        if 0 <= gx < 24 and 0 <= gy < 24:
                            grid[gy][gx] = CLUB_LIGHT if dx == 0 else CLUB_WOOD
                # Brazo sujetando
                for bx in range(12, 16):
                    grid[12][bx] = LEG_COLOR
            else:
                # Garrote sostenido en la espalda apuntando hacia arriba/atrás (como en el boceto)
                for i in range(8):
                    gx = 7 - i
                    gy = 10 + int(i * 0.8)
                    thick = 1 + int(i * 0.35)
                    for tx in range(gx - thick, gx + thick + 1):
                        if 0 <= tx < 24 and 0 <= gy < 24:
                            grid[gy][tx] = CLUB_LIGHT if tx == gx else CLUB_WOOD
                # Brazo hacia atrás
                grid[12][6] = LEG_COLOR
                grid[11][5] = LEG_COLOR

        # 2. Piernas y piececitos delgados
        # leg_frame: 0 = idle, 1 = paso 1 (izq adelante, der atrás), 2 = paso 2 (al revés)
        if leg_frame == 0:
            # Pierna 1
            for y in range(0, 4): grid[y][8] = LEG_COLOR
            grid[0][9] = LEG_COLOR; grid[0][10] = LEG_COLOR # Pie plano
            # Pierna 2
            for y in range(0, 4): grid[y][12] = LEG_COLOR
            grid[0][13] = LEG_COLOR; grid[0][14] = LEG_COLOR
        elif leg_frame == 1:
            # Zancada abierta
            for y in range(0, 4): grid[y][7 - y//2] = LEG_COLOR
            grid[0][5] = LEG_COLOR; grid[0][6] = LEG_COLOR
            for y in range(0, 4): grid[y][13 + y//2] = LEG_COLOR
            grid[0][15] = LEG_COLOR; grid[0][16] = LEG_COLOR
        else:
            # Zancada opuesta
            for y in range(0, 4): grid[y][9 + y//2] = LEG_COLOR
            grid[0][11] = LEG_COLOR; grid[0][12] = LEG_COLOR
            for y in range(0, 4): grid[y][11 - y//2] = LEG_COLOR
            grid[0][7] = LEG_COLOR; grid[0][8] = LEG_COLOR

        # 3. Mechones inferiores irregulares (y=3..5)
        for x in range(body_x_min, body_x_max + 1):
            if x % 2 == 0: grid[3][x] = FUR_DARK
            else: grid[4][x] = FUR_MID

        # 4. Cuerpo peludo con trazos verticales densos (y=4..18)
        for y in range(body_y_min, body_y_max + 1):
            for x in range(body_x_min, body_x_max + 1):
                # Trazos verticales alternando claros y oscuros
                pattern = (x + y * 2) % 3
                if pattern == 0: grid[y][x] = FUR_LIGHT
                elif pattern == 1: grid[y][x] = FUR_MID
                else: grid[y][x] = FUR_DARK
                # Borde posterior más oscuro
                if x == body_x_min: grid[y][x] = FUR_DEEP

        # 5. Mechones de pelo puntiagudos en la cabeza (y=19..22)
        for x, ty in [(6, 19), (7, 21), (8, 20), (9, 22), (10, 20), (11, 22), (12, 21), (13, 20), (14, 19)]:
            grid[ty][x] = FUR_TIP
            grid[ty-1][x] = FUR_LIGHT

        # 6. Ojo minimalista (ARRIBA, separado de la nariz)
        # Ojo situado en y=15..17, x=13..15
        grid[15][13] = EYE_WHITE; grid[15][14] = EYE_WHITE; grid[15][15] = EYE_WHITE
        grid[16][13] = EYE_WHITE; grid[16][14] = EYE_WHITE; grid[16][15] = EYE_WHITE
        grid[17][13] = EYE_WHITE; grid[17][14] = EYE_WHITE
        grid[16][15] = EYE_PUPIL; grid[15][15] = EYE_PUPIL # Pupila mirando al frente

        # 7. Nariz redondeada (MÁS PEQUEÑA, SEPARADA abajo del ojo)
        # Situada en y=10..12, sobresale hacia la derecha (x=14..18)
        # Nótese el espacio libre entre y=13 y el ojo y=15
        grid[13][13] = FUR_DARK # Separación entre ojo y nariz
        grid[13][14] = FUR_DARK

        # Snout / Nariz bulbosa compacta
        for ny in range(10, 13):
            for nx in range(14, 18):
                grid[ny][nx] = NOSE_LIGHT
        grid[11][18] = NOSE_LIGHT # Punta redonda
        grid[10][15] = NOSE_DARK  # Sombra inferior
        grid[10][16] = NOSE_DARK
        grid[10][17] = NOSE_DARK

    # -------------------------------------------------------------
    # VISTA FRONTAL (FRONT VIEW)
    # -------------------------------------------------------------
    elif view == "front":
        body_x_min = 7
        body_x_max = 16
        body_y_min = 4
        body_y_max = 18

        # 1. Piernas
        if leg_frame == 0:
            for y in range(0, 4): grid[y][9] = LEG_COLOR; grid[y][14] = LEG_COLOR
            grid[0][8] = LEG_COLOR; grid[0][9] = LEG_COLOR
            grid[0][14] = LEG_COLOR; grid[0][15] = LEG_COLOR
        elif leg_frame == 1:
            for y in range(0, 4): grid[y][8] = LEG_COLOR; grid[y][15] = LEG_COLOR
            grid[0][7] = LEG_COLOR; grid[0][8] = LEG_COLOR
            grid[0][15] = LEG_COLOR; grid[0][16] = LEG_COLOR
        else:
            for y in range(0, 4): grid[y][10] = LEG_COLOR; grid[y][13] = LEG_COLOR
            grid[0][10] = LEG_COLOR; grid[0][11] = LEG_COLOR
            grid[0][12] = LEG_COLOR; grid[0][13] = LEG_COLOR

        # 2. Brazos a los lados
        # Brazo izquierdo
        grid[11][5] = LEG_COLOR; grid[10][5] = LEG_COLOR; grid[9][6] = LEG_COLOR
        grid[8][5] = LEG_COLOR # Dedos
        # Brazo derecho
        grid[11][18] = LEG_COLOR; grid[10][18] = LEG_COLOR; grid[9][17] = LEG_COLOR
        grid[8][18] = LEG_COLOR

        # Si tiene garrote frontal
        if weapon and anim == "attack":
            for i in range(6):
                gx = 18 + i
                gy = 12 - i
                if 0 <= gx < 24 and 0 <= gy < 24:
                    grid[gy][gx] = CLUB_WOOD

        # 3. Pelo del cuerpo (trazos verticales)
        for y in range(body_y_min, body_y_max + 1):
            for x in range(body_x_min, body_x_max + 1):
                pattern = (x * 2 + y) % 3
                if pattern == 0: grid[y][x] = FUR_LIGHT
                elif pattern == 1: grid[y][x] = FUR_MID
                else: grid[y][x] = FUR_DARK

        # 4. Mechones cabeza
        for x, ty in [(7, 20), (8, 22), (9, 21), (10, 23), (11, 21), (12, 23), (13, 21), (14, 22), (15, 20), (16, 21)]:
            grid[ty][x] = FUR_TIP
            grid[ty-1][x] = FUR_LIGHT

        # 5. DOS OJOS FRONTALES (Arriba, bien separados de la nariz)
        # Ojo izquierdo (x=8..10, y=14..16)
        for oy in (14, 15, 16):
            for ox in (8, 9, 10): grid[oy][ox] = EYE_WHITE
        grid[15][9] = EYE_PUPIL

        # Ojo derecho (x=13..15, y=14..16)
        for oy in (14, 15, 16):
            for ox in (13, 14, 15): grid[oy][ox] = EYE_WHITE
        grid[15][14] = EYE_PUPIL

        # 6. Gran Nariz / Hocico frontal redondeado (y=9..12, x=10..13)
        # Claramente separada de los ojos por la línea y=13
        for ny in range(9, 13):
            for nx in range(10, 14):
                grid[ny][nx] = NOSE_LIGHT
        grid[9][11] = NOSE_DARK
        grid[9][12] = NOSE_DARK

    # -------------------------------------------------------------
    # VISTA TRASERA (BACK VIEW)
    # -------------------------------------------------------------
    elif view == "back":
        body_x_min = 7
        body_x_max = 16
        body_y_min = 4
        body_y_max = 18

        # 1. Piernas traseras
        for y in range(0, 4): grid[y][9] = LEG_COLOR; grid[y][14] = LEG_COLOR
        grid[0][9] = LEG_COLOR; grid[0][14] = LEG_COLOR

        # 2. Brazos a los lados
        grid[11][5] = LEG_COLOR; grid[10][5] = LEG_COLOR; grid[9][6] = LEG_COLOR
        grid[11][18] = LEG_COLOR; grid[10][18] = LEG_COLOR; grid[9][17] = LEG_COLOR

        # 3. Pelo de espalda puro y denso (sin cara)
        for y in range(body_y_min, body_y_max + 1):
            for x in range(body_x_min, body_x_max + 1):
                pattern = (x + y * 3) % 4
                if pattern == 0: grid[y][x] = FUR_LIGHT
                elif pattern == 1: grid[y][x] = FUR_MID
                elif pattern == 2: grid[y][x] = FUR_DARK
                else: grid[y][x] = FUR_DEEP

        # 4. Mechones cabeza
        for x, ty in [(7, 21), (8, 22), (9, 20), (10, 23), (11, 21), (12, 23), (13, 20), (14, 22), (15, 21), (16, 20)]:
            grid[ty][x] = FUR_TIP
            grid[ty-1][x] = FUR_LIGHT

        # 5. Si lleva el garrote a la espalda
        if weapon:
            for i in range(8):
                gx = 8 + i
                gy = 8 + i
                if 0 <= gx < 24 and 0 <= gy < 24:
                    grid[gy][gx] = CLUB_WOOD
                    grid[gy][gx+1] = CLUB_DARK

    return grid

def flatten_grid(grid, w, h):
    raw = bytearray()
    for y in range(h - 1, -1, -1): # Invertir para PNG (y=0 arriba)
        for x in range(w):
            r, g, b, a = grid[y][x]
            raw.extend([r, g, b, a])
    return bytes(raw)

# =====================================================================
# EJECUCIÓN PRINCIPAL: GUARDAR SPRITES Y METAS
# =====================================================================

def main():
    # Directorios destino
    dirs = [
        os.path.join("Assets", "Sprites", "Rocks"),
        os.path.join("Assets", "Resources", "Rocks"),
        os.path.join("Assets", "Sprites", "Creatures"),
        os.path.join("Assets", "Resources", "Creatures")
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    print("--- 1. GENERANDO 8 SPRITES DE ROCAS (32x32) ---")
    rock_creators = [
        ("rock_01_large_boulder", create_rock_large_boulder),
        ("rock_02_twin_overlapping", create_rock_twin_overlapping),
        ("rock_03_cluster_small", create_rock_cluster_small),
        ("rock_04_crag_angular", create_rock_crag_angular),
        ("rock_05_mossy_slate", create_rock_mossy_slate),
        ("rock_06_stacked_stones", create_rock_stacked_stones),
        ("rock_07_flat_slab", create_rock_flat_slab),
        ("rock_08_monolith_pillar", create_rock_monolith_pillar),
    ]

    for name, creator in rock_creators:
        grid = creator()
        rgba = flatten_grid(grid, 32, 32)
        for folder in ["Assets/Sprites/Rocks", "Assets/Resources/Rocks"]:
            fp = os.path.join(folder, f"{name}.png")
            write_png(fp, 32, 32, rgba)
            create_meta_file(fp, ppu=32)
        print(f"  [OK] Roca: {name}.png (32x32)")

    print("\n--- 2. GENERANDO 14 SPRITES DE MAKÓN (24x24) ---")
    makon_configs = [
        # Vista lateral desarmado
        ("makon_side_idle", "side", False, "idle", 0),
        ("makon_side_walk1", "side", False, "walk", 1),
        ("makon_side_walk2", "side", False, "walk", 2),
        # Vista lateral con garrote (arma visible)
        ("makon_side_club_idle", "side", True, "idle", 0),
        ("makon_side_club_walk1", "side", True, "walk", 1),
        ("makon_side_club_walk2", "side", True, "walk", 2),
        ("makon_side_club_attack", "side", True, "attack", 1),
        # Vista frontal (mirando hacia adelante)
        ("makon_front_idle", "front", False, "idle", 0),
        ("makon_front_walk1", "front", False, "walk", 1),
        ("makon_front_walk2", "front", False, "walk", 2),
        ("makon_front_attack", "front", True, "attack", 0),
        # Vista trasera (mirando hacia atrás)
        ("makon_back_idle", "back", False, "idle", 0),
        ("makon_back_walk1", "back", False, "walk", 1),
        ("makon_back_walk2", "back", False, "walk", 2),
    ]

    for name, view, weapon, anim, leg_frame in makon_configs:
        grid = create_makon_sprite(view=view, weapon=weapon, anim=anim, leg_frame=leg_frame)
        rgba = flatten_grid(grid, 24, 24)
        for folder in ["Assets/Sprites/Creatures", "Assets/Resources/Creatures"]:
            fp = os.path.join(folder, f"{name}.png")
            write_png(fp, 24, 24, rgba)
            create_meta_file(fp, ppu=16) # 16 PPU = 1.5 unidades Unity
        print(f"  [OK] Makón: {name}.png (24x24, 16 PPU)")

    # 3. Generar hojas de contacto / showcase en artifacts
    artifact_dir = r"C:\Users\oscar\.gemini\antigravity-ide\brain\88fc08f9-9a13-4d42-9f37-aad5763dc29d"
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Showcase Rocas (8 rocas en fila)
    showcase_w = 32 * 8
    showcase_h = 32
    showcase_grid = [[T for _ in range(showcase_w)] for _ in range(showcase_h)]
    for idx, (_, creator) in enumerate(rock_creators):
        r_grid = creator()
        for y in range(32):
            for x in range(32):
                showcase_grid[y][idx * 32 + x] = r_grid[y][x]
    write_png(os.path.join(artifact_dir, "rocks_showcase.png"), showcase_w, showcase_h, flatten_grid(showcase_grid, showcase_w, showcase_h))

    # Showcase Makones (14 poses en fila)
    m_showcase_w = 24 * 14
    m_showcase_h = 24
    m_showcase_grid = [[T for _ in range(m_showcase_w)] for _ in range(m_showcase_h)]
    for idx, (name, view, weapon, anim, leg_frame) in enumerate(makon_configs):
        m_grid = create_makon_sprite(view=view, weapon=weapon, anim=anim, leg_frame=leg_frame)
        for y in range(24):
            for x in range(24):
                m_showcase_grid[y][idx * 24 + x] = m_grid[y][x]
    write_png(os.path.join(artifact_dir, "makon_showcase.png"), m_showcase_w, m_showcase_h, flatten_grid(m_showcase_grid, m_showcase_w, m_showcase_h))

    print("\n¡Generación completada con éxito!")

if __name__ == "__main__":
    main()
