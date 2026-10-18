import zlib
import struct
import random
import os
import math
import shutil

# -------------------------------------------------------------
# PALETA DE 8 TONALIDADES DE VERDE (ESTILO RETRO 16-BIT / GBA)
# Calibrada para evitar patrones repetitivos y lograr máxima continuidad
# -------------------------------------------------------------
PALETTE_8_GREENS = [
    (24, 46, 24, 255),    # 0: Verde sombra profundo (raíz/sombra oscura)
    (36, 66, 32, 255),    # 1: Verde sombra de brizna
    (52, 92, 42, 255),    # 2: Verde bajo medio (sombreado de hojas)
    (68, 120, 54, 255),   # 3: Verde prado dominante (color neutro base de continuidad)
    (88, 148, 68, 255),   # 4: Verde medio alto (cuerpo de briznas)
    (116, 178, 86, 255),  # 5: Verde iluminado (luz solar en hierba)
    (152, 210, 108, 255), # 6: Verde claro reflejo
    (194, 236, 138, 255)  # 7: Verde lima resplandor / punta de brizna
]

# Acentos complementarios para elementos naturales
COL_WHITE = (252, 250, 242, 255)
COL_YELLOW = (255, 212, 48, 255)
COL_FLOWER_EYE = (210, 140, 20, 255)
COL_STONE_L = (168, 172, 160, 255)
COL_STONE_M = (112, 116, 108, 255)
COL_STONE_D = (54, 58, 52, 255)
COL_DEW_CORE = (235, 250, 255, 255)
COL_DEW_GLOW = (175, 225, 245, 255)

def write_png(filename, width, height, rgba_data):
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

def create_seamless_base(seed=1337):
    """
    Crea una base homogénea y texturizada en 32x32 sin manchas circulares.
    El color base 3 es dominante, con toques sutiles de tonos 2 y 4 para textura de hierba.
    Los bordes tienen la misma distribución para garantizar 'seamless tiling' perfecto.
    """
    grid = [[3 for _ in range(32)] for _ in range(32)]
    rng = random.Random(seed)

    # Dispersar micro-textura de 1 a 2 píxeles simulando briznas suaves en el césped
    for y in range(32):
        for x in range(32):
            val = rng.random()
            if val < 0.16:
                grid[y][x] = 2  # Toque de sombra baja
            elif val > 0.84:
                grid[y][x] = 4  # Toque de luz suave

    return grid

def draw_tuft(grid, x, y, blades=[(-1, 3, 5), (0, 4, 6), (1, 3, 5)]):
    """Dibuja un mechón natural de hierba con varias briznas contiguas."""
    for dx, h, max_c in blades:
        bx = (x + dx) % 32
        for dy in range(h):
            by = (y - dy) % 32
            if dy == h - 1:
                grid[by][bx] = max_c
            elif dy == 0:
                grid[by][bx] = 2
            else:
                grid[by][bx] = max_c - 1
            # Sombra a la derecha
            sx = (bx + 1) % 32
            if grid[by][sx] < 3:
                grid[by][sx] = 1

def draw_wildflower(grid, cx, cy):
    """Dibuja una margarita silvestre blanca con centro amarillo."""
    # Sombra del tallo
    grid[(cy + 2) % 32][cx % 32] = 0
    grid[(cy + 1) % 32][cx % 32] = 1
    
    # 4 pétalos
    petals = [(0, -1), (-1, 0), (1, 0), (0, 1)]
    for dx, dy in petals:
        px = (cx + dx) % 32
        py = (cy + dy) % 32
        grid[py][px] = 'FLOWER_WHITE'
        
    grid[cy % 32][cx % 32] = 'FLOWER_YELLOW'

def draw_clover(grid, cx, cy):
    """Dibuja un trébol de 3 hojas con silueta limpia."""
    grid[(cy + 2) % 32][cx % 32] = 0 # Tallo sombra
    grid[(cy + 1) % 32][cx % 32] = 1 # Tallo
    grid[cy % 32][cx % 32] = 1       # Centro
    
    # Hojas en 3 direcciones
    grid[(cy - 1) % 32][(cx - 1) % 32] = 6
    grid[(cy - 1) % 32][cx % 32] = 7
    grid[(cy - 1) % 32][(cx + 1) % 32] = 5
    
    grid[cy % 32][(cx - 2) % 32] = 5
    grid[cy % 32][(cx - 1) % 32] = 6
    grid[cy % 32][(cx + 1) % 32] = 6
    grid[cy % 32][(cx + 2) % 32] = 4

def draw_pebble(grid, cx, cy):
    """Dibuja un guijarro redondeado con luz superior y sombra inferior."""
    # Sombra en césped
    grid[(cy + 2) % 32][(cx - 1) % 32] = 0
    grid[(cy + 2) % 32][cx % 32] = 0
    grid[(cy + 2) % 32][(cx + 1) % 32] = 0
    
    # Piedra
    grid[(cy) % 32][(cx - 1) % 32] = 'STONE_L'
    grid[(cy) % 32][cx % 32] = 'STONE_L'
    grid[(cy) % 32][(cx + 1) % 32] = 'STONE_M'
    
    grid[(cy + 1) % 32][(cx - 1) % 32] = 'STONE_M'
    grid[(cy + 1) % 32][cx % 32] = 'STONE_D'
    grid[(cy + 1) % 32][(cx + 1) % 32] = 'STONE_D'

def draw_dewdrop(grid, cx, cy):
    """Gota de rocío resplandeciente."""
    grid[cy % 32][cx % 32] = 'DEW_CORE'
    grid[(cy + 1) % 32][cx % 32] = 'DEW_GLOW'
    grid[(cy + 2) % 32][cx % 32] = 7

# -------------------------------------------------------------
# DEFINICIÓN DE LOS 8 SPRITES (32x32)
# -------------------------------------------------------------
def generate_8_sprites():
    sprites = []

    # 1. grass_01_plain: Prado base tranquilo y homogéneo
    s1 = create_seamless_base(101)
    draw_tuft(s1, 8, 12, [(-1, 2, 5), (0, 3, 5)])
    draw_tuft(s1, 24, 22, [(0, 3, 5), (1, 2, 4)])
    sprites.append(("grass_01_plain", "Prado Base Clásico", s1))

    # 2. grass_02_tufts: Mechones dobles de briznas vivas
    s2 = create_seamless_base(202)
    draw_tuft(s2, 10, 14, [(-1, 3, 5), (0, 5, 6), (1, 3, 5)])
    draw_tuft(s2, 22, 24, [(-1, 2, 5), (0, 4, 6), (1, 3, 5)])
    sprites.append(("grass_02_tufts", "Briznas Agrupadas", s2))

    # 3. grass_03_dense: Césped más denso y profundo
    s3 = create_seamless_base(303)
    draw_tuft(s3, 7, 10, [(-1, 4, 5), (0, 5, 5), (1, 4, 5)])
    draw_tuft(s3, 16, 20, [(-1, 3, 5), (0, 5, 6), (1, 4, 5)])
    draw_tuft(s3, 25, 9, [(0, 4, 5), (1, 3, 5)])
    sprites.append(("grass_03_dense", "Hierba Densa y Profunda", s3))

    # 4. grass_04_flowers: Flores silvestres (margaritas blancas y amarillas)
    s4 = create_seamless_base(404)
    draw_wildflower(s4, 9, 12)
    draw_wildflower(s4, 22, 20)
    draw_tuft(s4, 15, 14, [(0, 3, 5), (1, 2, 4)])
    sprites.append(("grass_04_flowers", "Flores Silvestres", s4))

    # 5. grass_05_clover: Tréboles silvestres de 3 hojas
    s5 = create_seamless_base(505)
    draw_clover(s5, 12, 14)
    draw_clover(s5, 21, 18)
    draw_tuft(s5, 6, 24, [(0, 3, 5), (1, 2, 5)])
    sprites.append(("grass_05_clover", "Tréboles Silvestres", s5))

    # 6. grass_06_wild_stalks: Briznas altas curvadas por la brisa
    s6 = create_seamless_base(606)
    draw_tuft(s6, 9, 16, [(-1, 4, 6), (0, 6, 7), (1, 5, 6)])
    draw_tuft(s6, 21, 22, [(-1, 4, 5), (0, 6, 7), (1, 4, 6)])
    sprites.append(("grass_06_wild_stalks", "Briznas Altas Soleadas", s6))

    # 7. grass_07_pebbles: Guijarros y tierra fértil
    s7 = create_seamless_base(707)
    draw_pebble(s7, 14, 15)
    draw_pebble(s7, 23, 23)
    draw_tuft(s7, 8, 22, [(0, 3, 5), (1, 2, 4)])
    sprites.append(("grass_07_pebbles", "Guijarros y Musgo", s7))

    # 8. grass_08_morning_dew: Rocío matutino brillante
    s8 = create_seamless_base(808)
    draw_tuft(s8, 8, 14, [(-1, 3, 5), (0, 5, 6), (1, 3, 5)])
    draw_dewdrop(s8, 8, 9)
    draw_tuft(s8, 20, 22, [(-1, 3, 5), (0, 6, 7), (1, 4, 6)])
    draw_dewdrop(s8, 20, 16)
    sprites.append(("grass_08_morning_dew", "Rocío Matutino", s8))

    return sprites

def grid_to_rgba(grid):
    rgba = bytearray()
    for y in range(32):
        for x in range(32):
            val = grid[y][x]
            if isinstance(val, int):
                color = PALETTE_8_GREENS[val]
            elif val == 'FLOWER_WHITE':
                color = COL_WHITE
            elif val == 'FLOWER_YELLOW':
                color = COL_YELLOW
            elif val == 'STONE_L':
                color = COL_STONE_L
            elif val == 'STONE_M':
                color = COL_STONE_M
            elif val == 'STONE_D':
                color = COL_STONE_D
            elif val == 'DEW_CORE':
                color = COL_DEW_CORE
            elif val == 'DEW_GLOW':
                color = COL_DEW_GLOW
            else:
                color = PALETTE_8_GREENS[3]
            rgba.extend(color)
    return rgba

def upscale_image(src_rgba, src_w, src_h, factor):
    dst_w = src_w * factor
    dst_h = src_h * factor
    dst_rgba = bytearray(dst_w * dst_h * 4)
    
    for y in range(dst_h):
        sy = y // factor
        for x in range(dst_w):
            sx = x // factor
            src_idx = (sy * src_w + sx) * 4
            dst_idx = (y * dst_w + x) * 4
            dst_rgba[dst_idx:dst_idx+4] = src_rgba[src_idx:src_idx+4]
            
    return dst_w, dst_h, dst_rgba

# -------------------------------------------------------------
# GENERACIÓN DE MOSAICO CONTINUO Y ORGÁNICO
# -------------------------------------------------------------
def generate_mosaic(sprites_rgba_list, tiles_x=24, tiles_y=16, seed=777):
    rng = random.Random(seed)
    tile_map = [[0 for _ in range(tiles_x)] for _ in range(tiles_y)]
    
    # Crear núcleos orgánicos para cúmulos de flores (3) y tréboles (4)
    num_patches = max(4, (tiles_x * tiles_y) // 50)
    patches = []
    for _ in range(num_patches):
        patches.append({
            'x': rng.randint(2, tiles_x - 3),
            'y': rng.randint(2, tiles_y - 3),
            'type': rng.choice([3, 4]),
            'rad': rng.uniform(1.8, 3.2)
        })

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            chosen = None
            
            # Comprobar pertenencia a parche floral
            for p in patches:
                dist = math.hypot(tx - p['x'], ty - p['y'])
                if dist < p['rad'] and rng.random() < 0.65:
                    chosen = p['type']
                    break
            
            if chosen is None:
                r = rng.random()
                if r < 0.44:
                    chosen = 0  # Prado base
                elif r < 0.72:
                    chosen = 1  # Briznas agrupadas
                elif r < 0.84:
                    chosen = 2  # Hierba densa
                elif r < 0.92:
                    chosen = 5  # Briznas altas soleadas
                elif r < 0.96:
                    chosen = 7  # Rocío matutino
                else:
                    chosen = 6  # Guijarros
                    
            tile_map[ty][tx] = chosen

    mosaic_w = tiles_x * 32
    mosaic_h = tiles_y * 32
    mosaic_rgba = bytearray(mosaic_w * mosaic_h * 4)
    
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tile_idx = tile_map[ty][tx]
            tile_data = sprites_rgba_list[tile_idx]
            
            for py in range(32):
                dst_y = ty * 32 + py
                src_start = py * 32 * 4
                src_end = src_start + 32 * 4
                dst_start = (dst_y * mosaic_w + tx * 32) * 4
                dst_end = dst_start + 32 * 4
                mosaic_rgba[dst_start:dst_end] = tile_data[src_start:src_end]
                
    return mosaic_w, mosaic_h, mosaic_rgba, tile_map

def main():
    target_dir = os.path.join("Assets", "Sprites", "GrassTiles")
    preview_dir = os.path.join("Assets", "Sprites", "Previews")
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)
    
    artifacts_dir = r"C:\Users\oscar\.gemini\antigravity-ide\brain\88fc08f9-9a13-4d42-9f37-aad5763dc29d"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("1. Generando 8 sprites refinados (seamless 16-bit pixel art)...")
    sprite_defs = generate_8_sprites()
    sprites_rgba = []
    
    tileset_w = 32 * 8
    tileset_h = 32
    tileset_rgba = bytearray(tileset_w * tileset_h * 4)
    
    for i, (name, title, grid) in enumerate(sprite_defs):
        rgba = grid_to_rgba(grid)
        sprites_rgba.append(rgba)
        
        single_path = os.path.join(target_dir, f"{name}.png")
        write_png(single_path, 32, 32, rgba)
        
        for y in range(32):
            src_s = y * 32 * 4
            src_e = src_s + 32 * 4
            dst_s = (y * tileset_w + i * 32) * 4
            dst_e = dst_s + 32 * 4
            tileset_rgba[dst_s:dst_e] = rgba[src_s:src_e]

    tileset_path = os.path.join(target_dir, "grass_tileset_8x32.png")
    write_png(tileset_path, tileset_w, tileset_h, tileset_rgba)
    
    print("2. Generando mosaico de prado continuo...")
    mw, mh, mosaic_rgba, tile_map = generate_mosaic(sprites_rgba, tiles_x=24, tiles_y=16, seed=888)
    
    up_w, up_h, up_mosaic_rgba = upscale_image(mosaic_rgba, mw, mh, 2)
    mosaic_path_2x = os.path.join(preview_dir, "meadow_mosaic_preview.png")
    write_png(mosaic_path_2x, up_w, up_h, up_mosaic_rgba)
    
    art_mosaic = os.path.join(artifacts_dir, "meadow_mosaic_preview.png")
    write_png(art_mosaic, up_w, up_h, up_mosaic_rgba)

    print("3. Generando showcase card...")
    card_w = 32 * 8 * 4 + 40
    card_h = 32 * 4 + 140
    card_rgba = bytearray([20, 24, 30, 255] * (card_w * card_h))
    
    for i, rgba in enumerate(sprites_rgba):
        _, _, up_tile = upscale_image(rgba, 32, 32, 4)
        tile_start_x = 20 + i * (128 + 4)
        tile_start_y = 20
        
        for ty in range(128):
            for tx in range(128):
                dx = tile_start_x + tx
                dy = tile_start_y + ty
                s_idx = (ty * 128 + tx) * 4
                d_idx = (dy * card_w + dx) * 4
                card_rgba[d_idx:d_idx+4] = up_tile[s_idx:s_idx+4]

    swatch_size = 28
    swatch_y = card_h - 55
    for i, col in enumerate(PALETTE_8_GREENS):
        sx = 20 + i * (swatch_size * 2 + 14)
        for sy in range(swatch_size):
            for px in range(swatch_size * 2):
                dx = sx + px
                dy = swatch_y + sy
                if dx < card_w and dy < card_h:
                    d_idx = (dy * card_w + dx) * 4
                    card_rgba[d_idx:d_idx+4] = col
                    
    showcase_path = os.path.join(preview_dir, "tiles_showcase.png")
    write_png(showcase_path, card_w, card_h, card_rgba)
    art_showcase = os.path.join(artifacts_dir, "tiles_showcase.png")
    write_png(art_showcase, card_w, card_h, card_rgba)
    
    # Actualizar también preview/tiles_data.js
    import base64, json
    tiles_json = {}
    for i, (name, title, _) in enumerate(sprite_defs):
        with open(os.path.join(target_dir, f"{name}.png"), 'rb') as fp:
            b64 = base64.b64encode(fp.read()).decode('ascii')
            tiles_json[i] = {
                'id': i,
                'name': name,
                'title': title,
                'data': f'data:image/png;base64,{b64}'
            }
    with open('preview/tiles_data.js', 'w', encoding='utf-8') as out:
        out.write('window.TILE_PALETTE_DATA = ' + json.dumps(tiles_json, indent=2, ensure_ascii=False) + ';\n')
        
    print("¡Sprites, mosaico, showcase y tiles_data actualizados con éxito!")

if __name__ == "__main__":
    main()
