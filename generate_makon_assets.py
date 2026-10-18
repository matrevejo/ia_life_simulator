import os
import uuid
import numpy as np
from PIL import Image
from collections import deque
from scipy.ndimage import binary_erosion

SRC_IMG = r"C:\Users\oscar\.gemini\antigravity-ide\brain\95633b71-868f-40bc-ba64-6383814f9ec2\.user_uploaded\media_1792311636653.jpg"

im = Image.open(SRC_IMG).convert("RGB")
arr = np.array(im)
H, W, _ = arr.shape

threshold = 135

def extract_cell(r, c):
    y0, y1 = r * (H // 2), (r + 1) * (H // 2)
    x0, x1 = c * (W // 4), (c + 1) * (W // 4)
    cell = arr[y0:y1, x0:x1]
    cH, cW, _ = cell.shape
    
    is_outline = (cell[:, :, 0] < threshold) & (cell[:, :, 1] < threshold) & (cell[:, :, 2] < threshold)
    visited = np.zeros((cH, cW), dtype=bool)
    q = deque()
    for x in range(cW):
        if not is_outline[0, x]: q.append((0, x)); visited[0, x] = True
        if not is_outline[cH-1, x]: q.append((cH-1, x)); visited[cH-1, x] = True
    for y in range(cH):
        if not is_outline[y, 0]: q.append((y, 0)); visited[y, 0] = True
        if not is_outline[y, cW-1]: q.append((y, cW-1)); visited[y, cW-1] = True
        
    while q:
        cy, cx = q.popleft()
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < cH and 0 <= nx < cW and not visited[ny, nx]:
                if not is_outline[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))
                    
    creature = ~visited
    rgba = np.zeros((cH, cW, 4), dtype=np.uint8)
    rgba[creature, :3] = cell[creature]
    rgba[creature, 3] = 255
    
    edge = creature & ~binary_erosion(creature)
    fringe = edge & (rgba[:, :, 0] > 130)
    rgba[fringe, 3] = 0
    
    ys, xs = np.where(rgba[:, :, 3] > 0)
    cropped = rgba[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return cropped

raw_poses = {
    "front": extract_cell(0, 0),
    "back": extract_cell(0, 1),
    "side_right": extract_cell(0, 2),
    "side_left": extract_cell(0, 3),
    "diag_front_right": extract_cell(1, 0),
    "diag_front_left": extract_cell(1, 1),
    "diag_back_right": extract_cell(1, 2),
    "diag_back_left": extract_cell(1, 3)
}

CANVAS_W = 256
CANVAS_H = 360
GROUND_Y = 350

def place_on_canvas(cropped_rgba, offset_x=0, offset_y=0):
    cH, cW, _ = cropped_rgba.shape
    canvas = np.zeros((CANVAS_H, CANVAS_W, 4), dtype=np.uint8)
    start_x = (CANVAS_W - cW) // 2 + offset_x
    start_y = (GROUND_Y - cH) + offset_y
    canvas[start_y:start_y+cH, start_x:start_x+cW] = cropped_rgba
    return canvas

# Base idle poses
idle_front = place_on_canvas(raw_poses["front"])
idle_back = place_on_canvas(raw_poses["back"])
idle_side = place_on_canvas(raw_poses["side_right"]) # Facing right
idle_diag_front = place_on_canvas(raw_poses["diag_front_right"])
idle_diag_back = place_on_canvas(raw_poses["diag_back_right"])

# Walking frame generators with foot motion
def make_walk_front_back(canvas_base, lift_left, leg_split_x=128, y_leg_start=280, lift_amount=16, shift_x=3):
    res = canvas_base.copy()
    leg_mask = np.zeros((CANVAS_H, CANVAS_W), dtype=bool)
    if lift_left:
        leg_mask[y_leg_start:, :leg_split_x] = (res[y_leg_start:, :leg_split_x, 3] > 0)
    else:
        leg_mask[y_leg_start:, leg_split_x:] = (res[y_leg_start:, leg_split_x:, 3] > 0)
        
    leg_pixels = np.zeros_like(res)
    leg_pixels[leg_mask] = res[leg_mask]
    
    fur_fringe = res[y_leg_start-5:y_leg_start+15, :].copy()
    res[leg_mask] = 0
    
    sx = shift_x if lift_left else -shift_x
    ys, xs = np.where(leg_mask)
    for y, x in zip(ys, xs):
        ny = y - lift_amount
        nx = x + sx
        if 0 <= ny < CANVAS_H and 0 <= nx < CANVAS_W:
            res[ny, nx] = leg_pixels[y, x]
            
    for dy in range(fur_fringe.shape[0]):
        for dx in range(fur_fringe.shape[1]):
            if fur_fringe[dy, dx, 3] > 0:
                res[y_leg_start - 5 + dy, dx] = fur_fringe[dy, dx]
                
    return res

def make_walk_side(canvas_base, step_front, x_split=124, y_leg_start=280, lift_amount=15):
    res = canvas_base.copy()
    front_mask = np.zeros((CANVAS_H, CANVAS_W), dtype=bool)
    back_mask = np.zeros((CANVAS_H, CANVAS_W), dtype=bool)
    
    front_mask[y_leg_start:, x_split:] = (res[y_leg_start:, x_split:, 3] > 0)
    back_mask[y_leg_start:, :x_split] = (res[y_leg_start:, :x_split, 3] > 0)
    
    fur_fringe = res[y_leg_start-5:y_leg_start+15, :].copy()
    res[front_mask] = 0
    res[back_mask] = 0
    
    if step_front:
        ys_b, xs_b = np.where(back_mask)
        res[ys_b, xs_b] = canvas_base[ys_b, xs_b]
        
        ys_f, xs_f = np.where(front_mask)
        for y, x in zip(ys_f, xs_f):
            ny = y - lift_amount
            nx = x + 10
            if 0 <= ny < CANVAS_H and 0 <= nx < CANVAS_W:
                res[ny, nx] = canvas_base[y, x]
    else:
        ys_f, xs_f = np.where(front_mask)
        res[ys_f, xs_f] = canvas_base[ys_f, xs_f]
        
        ys_b, xs_b = np.where(back_mask)
        for y, x in zip(ys_b, xs_b):
            ny = y - lift_amount
            nx = x + 12
            if 0 <= ny < CANVAS_H and 0 <= nx < CANVAS_W:
                res[ny, nx] = canvas_base[y, x]
                
    for dy in range(fur_fringe.shape[0]):
        for dx in range(fur_fringe.shape[1]):
            if fur_fringe[dy, dx, 3] > 0:
                res[y_leg_start - 5 + dy, dx] = fur_fringe[dy, dx]
                
    return res

front_w1 = make_walk_front_back(idle_front, lift_left=True, leg_split_x=128, y_leg_start=280, lift_amount=16)
front_w2 = make_walk_front_back(idle_front, lift_left=False, leg_split_x=128, y_leg_start=280, lift_amount=16)

back_w1 = make_walk_front_back(idle_back, lift_left=True, leg_split_x=128, y_leg_start=280, lift_amount=16)
back_w2 = make_walk_front_back(idle_back, lift_left=False, leg_split_x=128, y_leg_start=280, lift_amount=16)

side_w1 = make_walk_side(idle_side, step_front=True, x_split=124, y_leg_start=280, lift_amount=15)
side_w2 = make_walk_side(idle_side, step_front=False, x_split=124, y_leg_start=280, lift_amount=15)

diag_front_w1 = make_walk_front_back(idle_diag_front, lift_left=True, leg_split_x=124, y_leg_start=280, lift_amount=16)
diag_front_w2 = make_walk_front_back(idle_diag_front, lift_left=False, leg_split_x=124, y_leg_start=280, lift_amount=16)

diag_back_w1 = make_walk_front_back(idle_diag_back, lift_left=True, leg_split_x=128, y_leg_start=280, lift_amount=16)
diag_back_w2 = make_walk_front_back(idle_diag_back, lift_left=False, leg_split_x=128, y_leg_start=280, lift_amount=16)

# Poses dictionary (14 standard + 6 diagonal = 20 poses)
sprites_to_save = {
    # Front
    "makon_front_idle": idle_front,
    "makon_front_walk1": front_w1,
    "makon_front_walk2": front_w2,
    "makon_front_attack": idle_front, # No weapon: stays curious/peaceful
    
    # Back
    "makon_back_idle": idle_back,
    "makon_back_walk1": back_w1,
    "makon_back_walk2": back_w2,
    
    # Side (facing right; engine flips for left)
    "makon_side_idle": idle_side,
    "makon_side_walk1": side_w1,
    "makon_side_walk2": side_w2,
    
    # Club poses redirected to peaceful bare sprites
    "makon_side_club_idle": idle_side,
    "makon_side_club_walk1": side_w1,
    "makon_side_club_walk2": side_w2,
    "makon_side_club_attack": idle_side,
    
    # Diagonal poses (Front-Right & Back-Right; engine flips for left)
    "makon_diag_front_idle": idle_diag_front,
    "makon_diag_front_walk1": diag_front_w1,
    "makon_diag_front_walk2": diag_front_w2,
    
    "makon_diag_back_idle": idle_diag_back,
    "makon_diag_back_walk1": diag_back_w1,
    "makon_diag_back_walk2": diag_back_w2
}

def create_meta_file(filepath, ppu=200):
    meta_path = filepath + ".meta"
    # Keep existing guid if meta file already exists
    guid = None
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("guid:"):
                    guid = line.split(":", 1)[1].strip()
                    break
    if not guid:
        file_id = os.path.basename(filepath)
        guid = uuid.uuid5(uuid.NAMESPACE_DNS, f"lifesim_makon_{file_id}_{ppu}").hex
        
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
    filterMode: 1
    aniso: 1
  spriteMode: 1
  spritePixelsToUnits: {ppu}
  alignment: 9
  spritePivot: {{x: 0.5, y: 0.05}}
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

# Target directories
dirs = [
    os.path.join("Assets", "Resources", "Creatures"),
    os.path.join("Assets", "Sprites", "Creatures")
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    for name, img_arr in sprites_to_save.items():
        png_path = os.path.join(d, f"{name}.png")
        Image.fromarray(img_arr).save(png_path)
        create_meta_file(png_path, ppu=200)

print(f"Successfully generated and wrote {len(sprites_to_save)} Makon sprites to:")
for d in dirs:
    print(f"  - {d}")
