// -------------------------------------------------------------
// SIMULADOR DE VIDA - MOTOR 4X: MUNDO 160x120, ROCAS Y MAKONES
// -------------------------------------------------------------

const ROCK_TILES_INFO = [
  { name: "rock_01_large_boulder", title: "Roca Grande Imponente" },
  { name: "rock_02_twin_overlapping", title: "Dos Rocas Superpuestas" },
  { name: "rock_03_cluster_small", title: "Grupito de Roquitas" },
  { name: "rock_04_crag_angular", title: "Peñasco Angular Afilado" },
  { name: "rock_05_mossy_slate", title: "Losa Gris Estratificada" },
  { name: "rock_06_stacked_stones", title: "Rocas Apiladas (Cairn)" },
  { name: "rock_07_flat_slab", title: "Piedra Plana de Río" },
  { name: "rock_08_monolith_pillar", title: "Monolito / Aguja Vertical" }
];

const PRESET_ALIEN_COLORS = [
  "#ff6ea6", // Rosa Neón
  "#be7fff", // Violeta Cósmico
  "#40d1f2", // Cian Eléctrico
  "#9de64d", // Lima Alienígena
  "#ffa626", // Ámbar Solar
  "#4de09e"  // Menta Esmeralda
];

const PRESET_MAKON_COLORS = [
  "#d8d8e0", // Gris Ceniza Claro
  "#b2b8c2", // Pizarra Roca Gris
  "#eaeaf2", // Blanco Grisáceo Glacial
  "#949aa6", // Gris Carbón Suave
  "#f27aa0", // Pelaje Rosa Salvaje
  "#6bd0ea", // Pelaje Azul Escarcha
  "#df94f2", // Pelaje Lila Makón
  "#ffb84d", // Pelaje Ámbar León
  "#8cd873"  // Pelaje Musgo Primitivo
];

// Estado de la simulación
const state = {
  width: 160,
  height: 120,
  seed: 777,
  useRocks: true,
  useTrees: true,
  
  // Rejillas
  grassGrid: [],
  rockGrid: [],
  treeGrid: [],
  impassableGrid: [],
  
  // Criaturas
  creatures: [],
  selectedCreature: null,
  
  // Cámara
  zoom: 1.0,
  panX: 0,
  panY: 0,
  isDragging: false,
  dragStartX: 0,
  dragStartY: 0,
  showGrid: false,
  showCRT: false,
  
  // Buffers gráficos
  offscreenWorld: null
};

// Contenedores de imágenes
const loadedAssets = {
  grass: {},
  trees: {},
  rocks: {},
  creatures: {}
};

// Referencias DOM
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const viewport = document.getElementById('viewport-container');
const minimapCanvas = document.getElementById('minimap-canvas');
const minimapCtx = minimapCanvas.getContext('2d');
const crtOverlay = document.getElementById('crt-overlay');

const statDims = document.getElementById('stat-dims');
const statZoom = document.getElementById('stat-zoom');
const statCreatures = document.getElementById('stat-creatures');

// Inicialización de recursos gráficos
function initAssets() {
  const assets = window.GAME_ASSETS || {};
  let toLoad = 0;
  let loaded = 0;

  ['grass', 'trees', 'rocks', 'creatures'].forEach(cat => {
    const items = assets[cat] || {};
    for (const key in items) {
      toLoad++;
      const img = new Image();
      img.src = items[key];
      img.onload = () => {
        loaded++;
        if (loaded === toLoad) {
          onAllAssetsReady();
        }
      };
      loadedAssets[cat][key] = img;
    }
  });
}

function onAllAssetsReady() {
  buildSidebarRocksPalette();
  drawAvatarPreviews();
  regenerateWorld();
  centerCamera();
  setupEventListeners();
  requestAnimationFrame(gameLoop);
}

// -------------------------------------------------------------
// GENERACIÓN PROCEDURAL DEL MUNDO 160x120
// -------------------------------------------------------------

function pseudoNoise2D(x, y, seed) {
  const n = Math.sin(x * 12.9898 + y * 78.233 + seed * 37.719) * 43758.5453123;
  return n - Math.floor(n);
}

function smoothNoise2D(x, y, seed) {
  const i = Math.floor(x);
  const j = Math.floor(y);
  const fx = x - i;
  const fy = y - j;
  const sfx = fx * fx * (3 - 2 * fx);
  const sfy = fy * fy * (3 - 2 * fy);

  const n00 = pseudoNoise2D(i, j, seed);
  const n10 = pseudoNoise2D(i + 1, j, seed);
  const n01 = pseudoNoise2D(i, j + 1, seed);
  const n11 = pseudoNoise2D(i + 1, j + 1, seed);

  const nx0 = n00 * (1 - sfx) + n10 * sfx;
  const nx1 = n01 * (1 - sfx) + n11 * sfx;
  return nx0 * (1 - sfy) + nx1 * sfy;
}

function regenerateWorld() {
  const W = state.width;
  const H = state.height;
  const S = state.seed;

  state.grassGrid = new Int8Array(W * H);
  state.rockGrid = new Int8Array(W * H); // -1 = no rock, 0..7 = rock sprite idx
  state.rockGrid.fill(-1);
  state.treeGrid = new Int8Array(W * H); // -1 = no tree, 0..7 = tree sprite idx
  state.treeGrid.fill(-1);
  state.impassableGrid = new Uint8Array(W * H); // 1 = blocked, 0 = walkable

  // 1. Hierba base continua
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const fn = smoothNoise2D(x * 0.06, y * 0.06, S + 10);
      const cn = smoothNoise2D(x * 0.06, y * 0.06, S + 40);
      const dn = smoothNoise2D(x * 0.12, y * 0.12, S + 70);
      const r = pseudoNoise2D(x, y, S + 99);

      let idx = 0;
      if (fn > 0.68) idx = (r < 0.85) ? 3 : 1;
      else if (cn > 0.68) idx = (r < 0.85) ? 4 : 1;
      else if (dn > 0.72) idx = 2;
      else {
        if (r < 0.48) idx = 0;
        else if (r < 0.78) idx = 1;
        else if (r < 0.88) idx = 5;
        else if (r < 0.94) idx = 7;
        else idx = 6;
      }
      state.grassGrid[y * W + x] = idx;
    }
  }

  // 2. Mosaicos y Grupos de Rocas (Obstáculos coherentes)
  if (state.useRocks) {
    const isR = new Uint8Array(W * H);
    const borderThick = 2;

    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        // Muralla exterior
        if (x < borderThick || x >= W - borderThick || y < borderThick || y >= H - borderThick) {
          isR[y * W + x] = 1;
          continue;
        }

        // Afloramientos rocosos en grupos
        const rn = smoothNoise2D(x * 0.045, y * 0.045, S + 120);
        const distFromCenter = Math.hypot(x - W * 0.5, y - H * 0.5);
        const centerDampen = Math.min(1, distFromCenter / (W * 0.35));

        if (rn > 0.65 && centerDampen > 0.3) {
          isR[y * W + x] = 1;
        }
      }
    }

    // Variedad estética de rocas según densidad y vecinos
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        if (!isR[y * W + x]) continue;

        const hasN = (y + 1 < H) && isR[(y + 1) * W + x];
        const hasS = (y - 1 >= 0) && isR[(y - 1) * W + x];
        const hasW = (x - 1 >= 0) && isR[y * W + (x - 1)];
        const hasE = (x + 1 < W) && isR[y * W + (x + 1)];

        const r = pseudoNoise2D(x, y, S + 77);
        let rockIdx = 0;

        if (!hasN && !hasS && !hasW && !hasE) {
          // Aislada: 50% grande, 30% grupito, 20% monolito
          if (r < 0.50) rockIdx = 0; // roca grande
          else if (r < 0.80) rockIdx = 2; // grupito
          else rockIdx = 7; // monolito
        } else if (hasW || hasE) {
          // Cadena horizontal: dos superpuestas o angulares
          if (r < 0.45) rockIdx = 1; // dos superpuestas
          else if (r < 0.75) rockIdx = 3; // angular
          else rockIdx = 4; // losa
        } else {
          // Cadena vertical / centro: apiladas o grande
          if (r < 0.50) rockIdx = 5; // apiladas
          else if (r < 0.80) rockIdx = 0; // grande
          else rockIdx = 6; // losa plana
        }

        state.rockGrid[y * W + x] = rockIdx;
        state.impassableGrid[y * W + x] = 1; // IMPEDIR PASO
      }
    }
  }

  // 3. Arboledas en grupos
  if (state.useTrees) {
    const groveCount = 14;
    const treeKeys = Object.keys(loadedAssets.trees);
    let rng = createRng(S + 333);

    for (let g = 0; g < groveCount; g++) {
      const cx = Math.floor(rng() * (W - 12)) + 6;
      const cy = Math.floor(rng() * (H - 12)) + 6;
      const treesInGrove = Math.floor(rng() * 5) + 3;

      for (let t = 0; t < treesInGrove; t++) {
        const tx = Math.max(3, Math.min(W - 4, cx + Math.floor(rng() * 7) - 3));
        const ty = Math.max(3, Math.min(H - 4, cy + Math.floor(rng() * 7) - 3));
        const idx = ty * W + tx;

        if (state.rockGrid[idx] === -1 && state.treeGrid[idx] === -1) {
          state.treeGrid[idx] = Math.floor(rng() * treeKeys.length);
          state.impassableGrid[idx] = 1;
        }
      }
    }
  }

  // 4. Renderizar el buffer estático del mundo
  renderOffscreenWorld();

  // 5. Generar criaturas (Gelatinosos y Makones)
  spawnInitialCreatures();

  updateStatsUI();
  drawMinimap();
}

function createRng(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return function() {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

// -------------------------------------------------------------
// RENDERIZADO DEL BUFFER OFFSCREEN DEL MUNDO
// -------------------------------------------------------------

function renderOffscreenWorld() {
  const W = state.width;
  const H = state.height;
  const tileSize = 32;

  if (!state.offscreenWorld) {
    state.offscreenWorld = document.createElement('canvas');
  }
  state.offscreenWorld.width = W * tileSize;
  state.offscreenWorld.height = H * tileSize;
  const bCtx = state.offscreenWorld.getContext('2d');
  bCtx.imageSmoothingEnabled = false;

  const grassKeys = Object.keys(loadedAssets.grass);
  const rockKeys = Object.keys(loadedAssets.rocks);
  const treeKeys = Object.keys(loadedAssets.trees);

  // 1. Capa Hierba
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const gIdx = state.grassGrid[y * W + x];
      const img = loadedAssets.grass[grassKeys[gIdx]];
      if (img) {
        bCtx.drawImage(img, x * tileSize, y * tileSize, tileSize, tileSize);
      }
    }
  }

  // 2. Capa Rocas y Árboles con Y-sorting
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const rIdx = state.rockGrid[y * W + x];
      if (rIdx !== -1) {
        const rImg = loadedAssets.rocks[rockKeys[rIdx]];
        if (rImg) {
          bCtx.drawImage(rImg, x * tileSize, y * tileSize, tileSize, tileSize);
        }
      }

      const tIdx = state.treeGrid[y * W + x];
      if (tIdx !== -1) {
        const tImg = loadedAssets.trees[treeKeys[tIdx]];
        if (tImg) {
          bCtx.drawImage(tImg, x * tileSize, y * tileSize, tileSize, tileSize);
        }
      }
    }
  }
}

// -------------------------------------------------------------
// SISTEMA DE CRIATURAS (GELATINOSO + MAKÓN CON GARROTE)
// -------------------------------------------------------------

class Creature {
  constructor(species, color, x, y, hasWeapon = false) {
    this.species = species; // 'gelatinous' | 'makon'
    this.color = color;
    this.x = x;
    this.y = y;
    this.targetX = x;
    this.targetY = y;
    this.hasWeapon = false; // Sin armas de momento
    
    this.speed = (species === 'makon') ? (1.3 + Math.random() * 0.4) : (1.9 + Math.random() * 0.5);
    this.state = 'idle'; // 'idle' | 'wandering' | 'looking' | 'eating'
    this.facing = 'front'; // 'front' | 'back' | 'left' | 'right' | 'diag_front_right' | etc.
    this.stateTimer = 1.0 + Math.random() * 2.0;
    this.animTimer = Math.random() * 10;
    this.flipX = false;
    this.waddleAngle = 0;
    this.hopBounceY = 0;

    this.tintCache = {};
    this.pickNewTarget();
  }

  isWalkable(tileX, tileY) {
    if (tileX < 0 || tileX >= state.width || tileY < 0 || tileY >= state.height) return false;
    return state.impassableGrid[tileY * state.width + tileX] === 0;
  }

  pickNewTarget() {
    for (let attempt = 0; attempt < 20; attempt++) {
      const angle = Math.random() * Math.PI * 2;
      const dist = 3 + Math.random() * 12;
      const tx = Math.floor(this.x + Math.cos(angle) * dist);
      const ty = Math.floor(this.y + Math.sin(angle) * dist);

      if (this.isWalkable(tx, ty)) {
        this.targetX = tx + 0.5;
        this.targetY = ty + 0.5;
        return;
      }
    }
    this.targetX = this.x;
    this.targetY = this.y;
  }

  update(dt) {
    this.stateTimer -= dt;
    this.animTimer += dt * 6.0;

    if (this.state === 'idle') {
      this.waddleAngle = 0;
      this.hopBounceY = 0;
      if (this.stateTimer <= 0) {
        const roll = Math.random();
        if (roll < 0.65) {
          this.pickNewTarget();
          this.state = 'wandering';
          this.stateTimer = 3.0 + Math.random() * 4.0;
        } else if (roll < 0.85) {
          this.state = 'looking';
          this.stateTimer = 1.5 + Math.random() * 2.0;
        } else {
          this.state = 'eating';
          this.stateTimer = 2.0 + Math.random() * 2.5;
        }
      }
    } else if (this.state === 'wandering') {
      const dx = this.targetX - this.x;
      const dy = this.targetY - this.y;
      const dist = Math.hypot(dx, dy);

      // Actualizar orientación (Facing) con soporte de 8 direcciones y diagonales
      const absX = Math.abs(dx);
      const absY = Math.abs(dy);
      if (absY > absX * 1.8) {
        this.facing = (dy > 0) ? 'front' : 'back';
      } else if (absX > absY * 1.8) {
        this.facing = (dx < 0) ? 'left' : 'right';
      } else {
        if (dy > 0) {
          this.facing = (dx < 0) ? 'diag_front_left' : 'diag_front_right';
        } else {
          this.facing = (dx < 0) ? 'diag_back_left' : 'diag_back_right';
        }
      }

      if (dist < 0.3 || this.stateTimer <= 0) {
        this.state = 'idle';
        this.stateTimer = 1.5 + Math.random() * 3.0;
        this.waddleAngle = 0;
        this.hopBounceY = 0;
        return;
      }

      const dirX = dx / dist;
      const dirY = dy / dist;
      const step = this.speed * dt;
      const nextX = this.x + dirX * step;
      const nextY = this.y + dirY * step;

      // Sonda hacia adelante para evitar rocas
      const probeX = Math.floor(this.x + dirX * 0.7);
      const probeY = Math.floor(this.y + dirY * 0.7);

      if (!this.isWalkable(probeX, probeY)) {
        this.state = 'looking';
        this.stateTimer = 1.0 + Math.random();
        this.pickNewTarget();
        return;
      }

      this.x = nextX;
      this.y = nextY;

      if (this.species === 'makon') {
        // Makón: paso cómico y bamboleo sutil con cadencia de pisada
        this.waddleAngle = Math.sin(this.animTimer * 1.4) * 0.05;
        this.hopBounceY = -Math.abs(Math.sin(this.animTimer * 1.4)) * 0.06;
      } else {
        // Gelatinoso: rebotes saltarines en Y
        this.waddleAngle = 0;
        this.hopBounceY = -Math.abs(Math.sin(this.animTimer * 1.8)) * 0.25;
      }
    } else if (this.state === 'looking') {
      this.facing = (Math.floor(this.animTimer * 0.5) % 2 === 0) ? 'left' : 'right';
      if (this.stateTimer <= 0) {
        this.state = 'wandering';
        this.pickNewTarget();
        this.stateTimer = 3.0 + Math.random() * 4.0;
      }
    } else if (this.state === 'eating') {
      if (this.stateTimer <= 0) {
        this.state = 'idle';
        this.stateTimer = 1.0 + Math.random() * 2.0;
      }
    }
  }

  getCurrentSpriteName() {
    if (this.species === 'gelatinous') {
      if (this.state === 'idle') {
        const f = (Math.floor(this.animTimer * 0.4) % 4 === 0) ? 2 : 1;
        return `alien_idle${f}`;
      } else {
        const f = (Math.floor(this.animTimer) % 2 === 0) ? 1 : 2;
        return `alien_walk${f}`;
      }
    }

    // Especie MAKÓN (Animación con movimiento en los pies y sin armas)
    const isWalk = (this.state === 'wandering');
    const walkF = (Math.floor(this.animTimer) % 2 === 0) ? 1 : 2;

    if (this.facing === 'front') {
      return isWalk ? `makon_front_walk${walkF}` : 'makon_front_idle';
    } else if (this.facing === 'back') {
      return isWalk ? `makon_back_walk${walkF}` : 'makon_back_idle';
    } else if (this.facing === 'diag_front_right' || this.facing === 'diag_front_left') {
      return isWalk ? `makon_diag_front_walk${walkF}` : 'makon_diag_front_idle';
    } else if (this.facing === 'diag_back_right' || this.facing === 'diag_back_left') {
      return isWalk ? `makon_diag_back_walk${walkF}` : 'makon_diag_back_idle';
    } else { // 'left' o 'right'
      return isWalk ? `makon_side_walk${walkF}` : 'makon_side_idle';
    }
  }

  draw(targetCtx, tileSize) {
    const sName = this.getCurrentSpriteName();
    const baseImg = loadedAssets.creatures[sName];
    if (!baseImg) return;

    let tinted = this.tintCache[sName];
    if (!tinted) {
      tinted = createTintedCanvas(baseImg, this.color);
      this.tintCache[sName] = tinted;
    }

    const px = this.x * tileSize;
    const py = (this.y + this.hopBounceY) * tileSize;
    
    // Proporciones: Makón nuevo es 256x360 (~1:1.4), gelatinoso es 16x16
    const drawW = (this.species === 'makon') ? 34 : 32;
    const drawH = (this.species === 'makon') ? 48 : 32;

    targetCtx.save();
    targetCtx.translate(px, py);
    targetCtx.rotate(this.waddleAngle);
    
    const shouldFlip = (this.facing === 'left' || this.facing === 'diag_front_left' || this.facing === 'diag_back_left');
    if (shouldFlip) {
      targetCtx.scale(-1, 1);
    }

    // Sombra ovalada realista bajo los pies en el suelo
    targetCtx.fillStyle = "rgba(0, 0, 0, 0.32)";
    targetCtx.beginPath();
    targetCtx.ellipse(0, 0, drawW * 0.40, drawW * 0.16, 0, 0, Math.PI * 2);
    targetCtx.fill();

    // En los sprites 256x360 los pies tocan a ~94% de la altura
    const offsetY = (this.species === 'makon') ? (-drawH * 0.94) : (-drawH * 0.5);
    targetCtx.drawImage(tinted, -drawW * 0.5, offsetY, drawW, drawH);
    targetCtx.restore();
  }
}

function createTintedCanvas(img, tintColor) {
  const c = document.createElement('canvas');
  c.width = img.width;
  c.height = img.height;
  const cx = c.getContext('2d');

  cx.drawImage(img, 0, 0);
  cx.globalCompositeOperation = 'multiply';
  cx.fillStyle = tintColor;
  cx.fillRect(0, 0, c.width, c.height);

  cx.globalCompositeOperation = 'destination-in';
  cx.drawImage(img, 0, 0);
  return c;
}

function spawnInitialCreatures() {
  state.creatures = [];

  // 16 Gelatinosos saltarines
  for (let i = 0; i < 16; i++) {
    const pt = findWalkablePoint();
    const color = PRESET_ALIEN_COLORS[i % PRESET_ALIEN_COLORS.length];
    state.creatures.push(new Creature('gelatinous', color, pt.x, pt.y));
  }

  // 36 Makones peludos pacíficos con movimiento en los pies
  for (let i = 0; i < 36; i++) {
    const pt = findWalkablePoint();
    const color = PRESET_MAKON_COLORS[i % PRESET_MAKON_COLORS.length];
    state.creatures.push(new Creature('makon', color, pt.x, pt.y, false));
  }
}

function findWalkablePoint() {
  for (let attempt = 0; attempt < 50; attempt++) {
    const x = Math.floor(Math.random() * (state.width - 10)) + 5;
    const y = Math.floor(Math.random() * (state.height - 10)) + 5;
    if (state.impassableGrid[y * state.width + x] === 0) {
      return { x: x + 0.5, y: y + 0.5 };
    }
  }
  return { x: state.width * 0.5, y: state.height * 0.5 };
}

// -------------------------------------------------------------
// BUCLE PRINCIPAL DE JUEGO (60 FPS)
// -------------------------------------------------------------

let lastTime = performance.now();

function gameLoop(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.1);
  lastTime = now;

  for (let i = 0; i < state.creatures.length; i++) {
    state.creatures[i].update(dt);
  }

  if (state.selectedCreature) {
    const tileSize = 32;
    state.panX = canvas.width * 0.5 - state.selectedCreature.x * tileSize * state.zoom;
    state.panY = canvas.height * 0.5 - state.selectedCreature.y * tileSize * state.zoom;
  }

  render();
  drawMinimap();
  requestAnimationFrame(gameLoop);
}

function render() {
  if (canvas.width !== viewport.clientWidth || canvas.height !== viewport.clientHeight) {
    canvas.width = viewport.clientWidth;
    canvas.height = viewport.clientHeight;
  }

  ctx.fillStyle = "#0a100c";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.imageSmoothingEnabled = false;

  ctx.save();
  ctx.translate(state.panX, state.panY);
  ctx.scale(state.zoom, state.zoom);

  // 1. Mapa desde offscreen buffer
  if (state.offscreenWorld) {
    ctx.drawImage(state.offscreenWorld, 0, 0);
  }

  // 2. Criaturas con Y-sorting
  const sorted = [...state.creatures].sort((a, b) => a.y - b.y);
  for (let i = 0; i < sorted.length; i++) {
    sorted[i].draw(ctx, 32);
  }

  // 3. Indicador de selección
  if (state.selectedCreature) {
    ctx.strokeStyle = "#4ade80";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(state.selectedCreature.x * 32, state.selectedCreature.y * 32, 22, 0, Math.PI * 2);
    ctx.stroke();
  }

  // 4. Cuadrícula
  if (state.showGrid && state.zoom >= 0.8) {
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = 1;
    const maxW = state.width * 32;
    const maxH = state.height * 32;

    for (let x = 0; x <= maxW; x += 32) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, maxH);
      ctx.stroke();
    }
    for (let y = 0; y <= maxH; y += 32) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(maxW, y);
      ctx.stroke();
    }
  }

  ctx.restore();
}

// -------------------------------------------------------------
// RADAR MINIMAP
// -------------------------------------------------------------

function drawMinimap() {
  if (!minimapCanvas) return;
  const mw = minimapCanvas.width = 180;
  const mh = minimapCanvas.height = 135;

  minimapCtx.fillStyle = "#0d1a10";
  minimapCtx.fillRect(0, 0, mw, mh);

  const scaleX = mw / state.width;
  const scaleY = mh / state.height;

  // Rocas
  minimapCtx.fillStyle = "#707d8e";
  for (let y = 0; y < state.height; y += 2) {
    for (let x = 0; x < state.width; x += 2) {
      if (state.rockGrid[y * state.width + x] !== -1) {
        minimapCtx.fillRect(x * scaleX, y * scaleY, scaleX * 2, scaleY * 2);
      }
    }
  }

  // Criaturas
  for (let i = 0; i < state.creatures.length; i++) {
    const c = state.creatures[i];
    minimapCtx.fillStyle = (c.species === 'makon') ? "#f59e0b" : "#38bdf8";
    minimapCtx.fillRect(c.x * scaleX - 1.5, c.y * scaleY - 1.5, 3, 3);
  }

  // Viewport
  const tileSize = 32;
  const viewX = (-state.panX / (tileSize * state.zoom)) * scaleX;
  const viewY = (-state.panY / (tileSize * state.zoom)) * scaleY;
  const viewW = (canvas.width / (tileSize * state.zoom)) * scaleX;
  const viewH = (canvas.height / (tileSize * state.zoom)) * scaleY;

  minimapCtx.strokeStyle = "#4ade80";
  minimapCtx.lineWidth = 1.5;
  minimapCtx.strokeRect(viewX, viewY, viewW, viewH);
}

// -------------------------------------------------------------
// INTERFAZ DE USUARIO Y EVENTOS
// -------------------------------------------------------------

function centerCamera() {
  state.selectedCreature = null;
  const tileSize = 32;
  const worldW = state.width * tileSize * state.zoom;
  const worldH = state.height * tileSize * state.zoom;
  state.panX = (canvas.width - worldW) * 0.5;
  state.panY = (canvas.height - worldH) * 0.5;
}

function setupEventListeners() {
  viewport.addEventListener('mousedown', e => {
    state.isDragging = true;
    state.dragStartX = e.clientX - state.panX;
    state.dragStartY = e.clientY - state.panY;
    state.selectedCreature = null;
  });

  window.addEventListener('mousemove', e => {
    if (!state.isDragging) return;
    state.panX = e.clientX - state.dragStartX;
    state.panY = e.clientY - state.dragStartY;
  });

  window.addEventListener('mouseup', () => {
    state.isDragging = false;
  });

  viewport.addEventListener('wheel', e => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    const mouseX = e.clientX - viewport.getBoundingClientRect().left;
    const mouseY = e.clientY - viewport.getBoundingClientRect().top;
    const newZoom = Math.max(0.2, Math.min(4.0, state.zoom * zoomFactor));

    state.panX = mouseX - (mouseX - state.panX) * (newZoom / state.zoom);
    state.panY = mouseY - (mouseY - state.panY) * (newZoom / state.zoom);
    state.zoom = newZoom;
    updateStatsUI();
  }, { passive: false });

  viewport.addEventListener('click', e => {
    const rect = viewport.getBoundingClientRect();
    const clickX = (e.clientX - rect.left - state.panX) / (32 * state.zoom);
    const clickY = (e.clientY - rect.top - state.panY) / (32 * state.zoom);

    for (let i = 0; i < state.creatures.length; i++) {
      const c = state.creatures[i];
      if (Math.hypot(c.x - clickX, c.y - clickY) < 0.9) {
        state.selectedCreature = c;
        return;
      }
    }
  });

  window.addEventListener('keydown', e => {
    const step = 40;
    if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') state.panY += step;
    if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') state.panY -= step;
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') state.panX += step;
    if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') state.panX -= step;
    if (e.key === 'r' || e.key === 'R') {
      state.seed = Math.floor(Math.random() * 999999);
      document.getElementById('input-seed').value = state.seed;
      regenerateWorld();
    }
  });

  document.getElementById('btn-zoom-in').onclick = () => {
    state.zoom = Math.min(4.0, state.zoom * 1.25);
    updateStatsUI();
  };
  document.getElementById('btn-zoom-out').onclick = () => {
    state.zoom = Math.max(0.2, state.zoom / 1.25);
    updateStatsUI();
  };
  document.getElementById('btn-zoom-reset').onclick = () => {
    state.zoom = 1.0;
    centerCamera();
    updateStatsUI();
  };
  document.getElementById('btn-center-cam').onclick = centerCamera;
  document.getElementById('btn-toggle-grid').onclick = (e) => {
    state.showGrid = !state.showGrid;
    e.currentTarget.classList.toggle('active', state.showGrid);
  };
  document.getElementById('btn-toggle-crt').onclick = (e) => {
    state.showCRT = !state.showCRT;
    crtOverlay.style.display = state.showCRT ? 'block' : 'none';
    e.currentTarget.classList.toggle('active', state.showCRT);
  };

  document.getElementById('btn-random-seed').onclick = () => {
    state.seed = Math.floor(Math.random() * 999999);
    document.getElementById('input-seed').value = state.seed;
    regenerateWorld();
  };

  document.getElementById('btn-apply-settings').onclick = () => {
    state.width = parseInt(document.getElementById('input-width').value) || 160;
    state.height = parseInt(document.getElementById('input-height').value) || 120;
    state.seed = parseInt(document.getElementById('input-seed').value) || 777;
    state.useRocks = document.getElementById('chk-rocks').checked;
    state.useTrees = document.getElementById('chk-trees').checked;
    regenerateWorld();
    centerCamera();
  };

  // Botones de spawn
  document.getElementById('btn-spawn-makon-club').onclick = () => {
    const pt = findWalkablePoint();
    const c = new Creature('makon', PRESET_MAKON_COLORS[Math.floor(Math.random() * 4)], pt.x, pt.y, false);
    state.creatures.push(c);
    state.selectedCreature = c;
    updateStatsUI();
  };

  document.getElementById('btn-spawn-makon-bare').onclick = () => {
    // Manada de 5 makones
    for (let k = 0; k < 5; k++) {
      const pt = findWalkablePoint();
      const c = new Creature('makon', PRESET_MAKON_COLORS[Math.floor(Math.random() * 4)], pt.x, pt.y, false);
      state.creatures.push(c);
    }
    updateStatsUI();
  };

  document.getElementById('btn-spawn-makon-color').onclick = () => {
    const pt = findWalkablePoint();
    const c = new Creature('makon', PRESET_MAKON_COLORS[4 + Math.floor(Math.random() * 5)], pt.x, pt.y, false);
    state.creatures.push(c);
    state.selectedCreature = c;
    updateStatsUI();
  };

  document.getElementById('btn-spawn-gel').onclick = () => {
    const pt = findWalkablePoint();
    const c = new Creature('gelatinous', PRESET_ALIEN_COLORS[Math.floor(Math.random() * PRESET_ALIEN_COLORS.length)], pt.x, pt.y);
    state.creatures.push(c);
    state.selectedCreature = c;
    updateStatsUI();
  };
}

function updateStatsUI() {
  statDims.textContent = `${state.width} × ${state.height} (${state.width * state.height} tiles)`;
  statZoom.textContent = `${Math.round(state.zoom * 100)}%`;
  statCreatures.textContent = `${state.creatures.length} Vivas`;
}

function buildSidebarRocksPalette() {
  const container = document.getElementById('rocks-palette-container');
  if (!container) return;
  container.innerHTML = '';

  const rockKeys = Object.keys(loadedAssets.rocks);
  for (let i = 0; i < rockKeys.length; i++) {
    const key = rockKeys[i];
    const img = loadedAssets.rocks[key];
    const info = ROCK_TILES_INFO[i] || { title: key };

    const item = document.createElement('div');
    item.className = 'tile-item';
    item.innerHTML = `
      <img src="${img.src}" alt="${info.title}">
      <span class="tile-item-num">0${i + 1}</span>
      <span class="tile-item-label">${info.title}</span>
    `;
    container.appendChild(item);
  }
}

function drawAvatarPreviews() {
  const makonCanvas = document.getElementById('preview-avatar-makon');
  if (makonCanvas && loadedAssets.creatures['makon_front_idle']) {
    const mCtx = makonCanvas.getContext('2d');
    mCtx.imageSmoothingEnabled = true;
    mCtx.clearRect(0, 0, makonCanvas.width, makonCanvas.height);
    mCtx.drawImage(loadedAssets.creatures['makon_front_idle'], 0, 0, makonCanvas.width, makonCanvas.height);
  }

  const gelCanvas = document.getElementById('preview-avatar-gel');
  if (gelCanvas && loadedAssets.creatures['alien_idle1']) {
    const gCtx = gelCanvas.getContext('2d');
    gCtx.imageSmoothingEnabled = false;
    gCtx.drawImage(loadedAssets.creatures['alien_idle1'], 0, 0, 16, 16);
  }
}

window.addEventListener('DOMContentLoaded', initAssets);
