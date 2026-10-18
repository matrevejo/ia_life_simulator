import os
import base64
import json

def get_b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

data = {
    "grass": {},
    "trees": {},
    "rocks": {},
    "creatures": {}
}

# Grass (8)
for name in [
    "grass_01_plain", "grass_02_tufts", "grass_03_dense", "grass_04_flowers",
    "grass_05_clover", "grass_06_wild_stalks", "grass_07_pebbles", "grass_08_morning_dew"
]:
    p = os.path.join("Assets", "Resources", "GrassTiles", f"{name}.png")
    if os.path.exists(p):
        data["grass"][name] = get_b64(p)

# Trees (8)
for name in [
    "tree_01_autumn_oak", "tree_02_brown_pine", "tree_03_ancient_stump", "tree_04_copper_bush",
    "tree_05_gnarled_willow", "tree_06_tall_birch", "tree_07_amber_fruits", "tree_08_twin_trunk"
]:
    p = os.path.join("Assets", "Resources", "Trees", f"{name}.png")
    if os.path.exists(p):
        data["trees"][name] = get_b64(p)

# Rocks (8)
for name in [
    "rock_01_large_boulder", "rock_02_twin_overlapping", "rock_03_cluster_small", "rock_04_crag_angular",
    "rock_05_mossy_slate", "rock_06_stacked_stones", "rock_07_flat_slab", "rock_08_monolith_pillar"
]:
    p = os.path.join("Assets", "Resources", "Rocks", f"{name}.png")
    if os.path.exists(p):
        data["rocks"][name] = get_b64(p)

# Creatures (Gelatinous + Makón 14 poses)
for name in [
    "alien_idle1", "alien_idle2", "alien_walk1", "alien_walk2",
    "makon_side_idle", "makon_side_walk1", "makon_side_walk2",
    "makon_side_club_idle", "makon_side_club_walk1", "makon_side_club_walk2", "makon_side_club_attack",
    "makon_front_idle", "makon_front_walk1", "makon_front_walk2", "makon_front_attack",
    "makon_back_idle", "makon_back_walk1", "makon_back_walk2",
    "makon_diag_front_idle", "makon_diag_front_walk1", "makon_diag_front_walk2",
    "makon_diag_back_idle", "makon_diag_back_walk1", "makon_diag_back_walk2"
]:
    p = os.path.join("Assets", "Resources", "Creatures", f"{name}.png")
    if os.path.exists(p):
        data["creatures"][name] = get_b64(p)

with open(os.path.join("preview", "all_assets_data.js"), "w", encoding="utf-8") as f:
    f.write("window.GAME_ASSETS = " + json.dumps(data, indent=2) + ";\n")

print(f"Packed: {len(data['grass'])} grass, {len(data['trees'])} trees, {len(data['rocks'])} rocks, {len(data['creatures'])} creatures.")
