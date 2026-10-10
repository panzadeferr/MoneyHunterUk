// main.js: boot, input, and the game loop that stitches world and battle together.
import { loadData } from './data.js';
import { loadSave, saveGame } from './save.js';
import { initWorld, updateWorld, drawWorld, VIEW_W, VIEW_H } from './world.js';
import { startBattle, updateBattle, drawBattle } from './battle.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const input = { up: false, down: false, left: false, right: false, justA: false };

function bindHeld(el, prop) {
  const on = e => { e.preventDefault(); input[prop] = true; };
  const off = e => { e.preventDefault(); input[prop] = false; };
  el.addEventListener('pointerdown', on);
  el.addEventListener('pointerup', off);
  el.addEventListener('pointerleave', off);
  el.addEventListener('pointercancel', off);
}
document.querySelectorAll('#dpad .pad').forEach(b => bindHeld(b, b.dataset.dir));

const btnA = document.getElementById('btn-a');
btnA.addEventListener('pointerdown', e => { e.preventDefault(); input.justA = true; });

const KEYMAP = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', w: 'up', s: 'down', a: 'left', d: 'right', W: 'up', S: 'down', A: 'left', D: 'right' };
addEventListener('keydown', e => {
  if (KEYMAP[e.key]) { input[KEYMAP[e.key]] = true; e.preventDefault(); }
  if (e.key === ' ' || e.key === 'Enter') input.justA = true;
});
addEventListener('keyup', e => { if (KEYMAP[e.key]) input[KEYMAP[e.key]] = false; });

const dialogEl = document.getElementById('dialog');
const dialogText = document.getElementById('dialog-text');
let dialogOpen = false;
document.getElementById('dialog-ok').addEventListener('click', () => { dialogEl.classList.add('hidden'); dialogOpen = false; });

let mode = 'loading';       // loading | title | world | battle
let world = null, battle = null, save = null, data = null;
let last = 0;

function showTitle() {
  mode = 'title';
  document.getElementById('title-screen').classList.remove('hidden');
  const hasSave = save.started && save.team.length;
  document.getElementById('title-continue-wrap').classList.toggle('hidden', !hasSave);
  document.getElementById('starter-pick').classList.toggle('hidden', hasSave);
}

function startWorld() {
  document.getElementById('title-screen').classList.add('hidden');
  fetch('maps/town.tmj?v=' + Date.now()).then(r => r.json()).then(tmj => {
    world = initWorld(canvas, tmj, save, {}, data.sheet);
    mode = 'world';
  }).catch(() => {
    dialogText.textContent = 'Could not load the map. Check your connection and reload.';
    dialogEl.classList.remove('hidden'); dialogOpen = true;
  });
}

document.querySelectorAll('.starter').forEach(b => b.addEventListener('click', () => {
  save.team = [{ species: b.dataset.species }];
  save.started = true;
  saveGame(save);
  startWorld();
}));
document.getElementById('btn-continue').addEventListener('click', () => startWorld());

function onBattleEnd(res) {
  saveGame(save);
  battle = null;
  mode = 'world';
}

async function boot() {
  save = loadSave();
  data = await loadData();
  const sheet = new Image();
  sheet.src = 'assets/sprites.png';
  await new Promise(res => { sheet.onload = res; sheet.onerror = res; });
  data.sheet = sheet;
  if (!data.questions.length) {
    dialogText.textContent = 'Game data could not load. Reload when you have a connection.';
    dialogEl.classList.remove('hidden'); dialogOpen = true;
  }
  showTitle();
}

function loop(ts) {
  const dt = Math.min(0.05, (ts - last) / 1000 || 0);
  last = ts;
  if (mode === 'world' && world && !dialogOpen) {
    const ev = updateWorld(world, dt, input, save);
    if (ev && ev.type === 'dialog') { dialogText.textContent = ev.text; dialogEl.classList.remove('hidden'); dialogOpen = true; }
    else if (ev && ev.type === 'encounter' && save.team.length) {
      battle = startBattle(ctx, { enemySpecies: ev.species, save, data, hooks: { onEnd: onBattleEnd } });
      mode = 'battle';
    }
    drawWorld(ctx, world, save);
  } else if (mode === 'battle' && battle) {
    updateBattle(battle, dt);
    drawBattle(ctx, battle);
  } else if (mode === 'title') {
    ctx.fillStyle = '#0b1622'; ctx.fillRect(0, 0, VIEW_W, VIEW_H);
  }
  input.justA = false;
  requestAnimationFrame(loop);
}

boot();
requestAnimationFrame(loop);
