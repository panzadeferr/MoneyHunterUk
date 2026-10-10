// world.js: tile map rendering, grid movement, collision, encounter rolls, signs and NPCs.
import { CREATURES } from './data.js';

const TILE = 16;
const SPRITE = 'assets/sprites.png';
// spritesheet coords (px): tiles row 0-1, character row 2, creatures rows 3-4
const TILE_SRC = {
  grass: [0, 0], tall: [16, 0], path: [32, 0], water: [48, 0], flower: [64, 0],
  fence: [80, 0], sign: [96, 0], door: [112, 0], tree: [0, 16], wall: [16, 16],
  roof: [32, 16], window: [48, 16]
};
const SOLID_IDS = new Set([3, 5, 6, 7, 8, 9, 10, 11]); // water, fence, sign, door, tree, wall, roof, window
const TALL_ID = 1;
const CHAR_SRC = { down: [0, 32], left: [16, 32], right: [32, 32], up: [48, 32] };
const VIEW_W = 480, VIEW_H = 320; // 30x20 tiles

function parseMap(tmj) {
  const ground = tmj.layers.find(l => l.name === 'ground').data;
  const solid = tmj.layers.find(l => l.name === 'solid').data;
  const w = tmj.width, h = tmj.height;
  const objLayer = tmj.layers.find(l => l.type === 'objectgroup');
  const props = o => Object.fromEntries((o.properties || []).map(p => [p.name, p.value]));
  const objects = { spawn: null, encounters: [], signs: [], npcs: [] };
  for (const o of (objLayer ? objLayer.objects : [])) {
    const p = props(o);
    if (o.type === 'spawn') objects.spawn = { x: o.x / TILE, y: o.y / TILE };
    else if (o.type === 'encounter') objects.encounters.push({ x: o.x / TILE, y: o.y / TILE, w: o.width / TILE, h: o.height / TILE, creatures: (p.creatures || '').split(','), rate: p.rate || 0.12 });
    else if (o.type === 'sign') objects.signs.push({ x: o.x / TILE, y: o.y / TILE, text: p.text || '' });
    else if (o.type === 'npc') objects.npcs.push({ x: o.x / TILE, y: o.y / TILE, sprite: p.sprite || 'down', text: p.text || '' });
  }
  return { w, h, ground, solid, objects };
}

function isSolid(map, x, y) {
  if (x < 0 || y < 0 || x >= map.w || y >= map.h) return true;
  return SOLID_IDS.has(map.solid[y * map.w + x]);
}

function initWorld(canvas, mapTmj, save, hooks, sheet) {
  if (!sheet || !sheet.complete || !sheet.naturalWidth) throw new Error('sprites.png not loaded');
  const map = parseMap(mapTmj);
  const groundCanvas = document.createElement('canvas');
  groundCanvas.width = map.w * TILE; groundCanvas.height = map.h * TILE;
  const g = groundCanvas.getContext('2d');
  for (let y = 0; y < map.h; y++) for (let x = 0; x < map.w; x++) {
    const t = map.ground[y * map.w + x];
    const src = TILE_SRC[['grass', 'tall', 'path', 'water', 'flower', 'fence', 'sign', 'door', 'tree', 'wall', 'roof', 'window'][t]];
    if (src) g.drawImage(sheet, src[0], src[1], TILE, TILE, x * TILE, y * TILE, TILE, TILE);
  }
  const st = {
    map, sheet, groundCanvas, hooks,
    x: save.x, y: save.y, dir: save.dir || 'down',
    moving: false, moveFrom: null, moveT: 0,
    encounterCooldown: 2 // tiles walked before encounters can trigger
  };
  return st;
}

function facingTile(st) {
  const d = { down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] }[st.dir];
  return { x: st.x + d[0], y: st.y + d[1] };
}

function objectAt(st, list, x, y) {
  return list.find(o => o.x === x && o.y === y);
}

// update one frame; returns an event or null: {type:'encounter', zone} | {type:'dialog', text}
function updateWorld(st, dt, input, save) {
  if (st.moving) {
    st.moveT += dt * 6; // 6 tiles/sec
    if (st.moveT >= 1) {
      st.moving = false; st.moveT = 0;
      if (st.encounterCooldown > 0) st.encounterCooldown--;
      const zone = st.map.objects.encounters.find(z => st.x >= z.x && st.x < z.x + z.w && st.y >= z.y && st.y < z.y + z.h);
      const tile = st.map.ground[st.y * st.map.w + st.x];
      if (tile === TALL_ID && zone && st.encounterCooldown === 0 && Math.random() < zone.rate) {
        st.encounterCooldown = 3;
        const species = zone.creatures[Math.floor(Math.random() * zone.creatures.length)] || 'coinling';
        return { type: 'encounter', species };
      }
    }
    return null;
  }
  if (input.justA) {
    const f = facingTile(st);
    const sign = objectAt(st, st.map.objects.signs, f.x, f.y);
    if (sign) return { type: 'dialog', text: sign.text };
    const npc = objectAt(st, st.map.objects.npcs, f.x, f.y);
    if (npc) return { type: 'dialog', text: npc.text };
    return null;
  }
  const dir = input.up ? 'up' : input.down ? 'down' : input.left ? 'left' : input.right ? 'right' : null;
  if (!dir) return null;
  st.dir = dir;
  const f = facingTile(st);
  if (isSolid(st.map, f.x, f.y)) return null;
  const npcBlock = objectAt(st, st.map.objects.npcs, f.x, f.y);
  if (npcBlock) return null;
  st.moveFrom = { x: st.x, y: st.y };
  st.x = f.x; st.y = f.y;
  st.moving = true; st.moveT = 0;
  save.x = st.x; save.y = st.y; save.dir = st.dir;
  return null;
}

function drawWorld(ctx, st, save) {
  const px = st.moving ? (st.moveFrom.x + (st.x - st.moveFrom.x) * st.moveT) * TILE : st.x * TILE;
  const py = st.moving ? (st.moveFrom.y + (st.y - st.moveFrom.y) * st.moveT) * TILE : st.y * TILE;
  let camX = Math.round(px - VIEW_W / 2 + TILE / 2);
  let camY = Math.round(py - VIEW_H / 2 + TILE / 2);
  camX = Math.max(0, Math.min(st.map.w * TILE - VIEW_W, camX));
  camY = Math.max(0, Math.min(st.map.h * TILE - VIEW_H, camY));
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0, 0, VIEW_W, VIEW_H);
  ctx.drawImage(st.groundCanvas, camX, camY, VIEW_W, VIEW_H, 0, 0, VIEW_W, VIEW_H);
  // NPCs (static, use their sprite direction)
  for (const npc of st.map.objects.npcs) {
    const src = CHAR_SRC[npc.sprite] || CHAR_SRC.down;
    ctx.drawImage(st.sheet, src[0], src[1], TILE, TILE, npc.x * TILE - camX, npc.y * TILE - camY, TILE, TILE);
  }
  // player
  const src = CHAR_SRC[st.dir];
  ctx.drawImage(st.sheet, src[0], src[1], TILE, TILE, px - camX, py - camY, TILE, TILE);
  // tall grass in front of the player when standing in it
  const tile = st.map.ground[st.y * st.map.w + st.x];
  if (tile === TALL_ID) ctx.drawImage(st.sheet, 16, 0, TILE, TILE, st.x * TILE - camX, st.y * TILE - camY, TILE, TILE);
  // HUD
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(0, 0, VIEW_W, 22);
  ctx.fillStyle = '#fff';
  ctx.font = '10px monospace';
  ctx.fillText('COINSWORTH', 6, 14);
  ctx.fillText('Team: ' + (save.team.length || 0) + '   Wins: ' + (save.wins || 0), 96, 14);
}

export { initWorld, updateWorld, drawWorld, isSolid, TILE, VIEW_W, VIEW_H };
