// battle.js: the battle scene. Answers are the attack: correct answers damage the
// enemy creature, three of them win it over to your team (no throw/capture items).
// The battle screen layout is its own design: enemy panel top, yours bottom.
import { CREATURES, TYPE_CHART, pickQuestion } from './data.js';
import { awardXP, rememberQuestion } from './save.js';

const VIEW_W = 480, VIEW_H = 320;

function effectiveness(atkType, defType) {
  const c = TYPE_CHART[atkType];
  if (!c) return 1;
  return c.strongVs === defType ? 1.5 : c.weakVs === defType ? 0.66 : 1;
}

function makeCreature(species, level) {
  const def = CREATURES[species] || CREATURES.coinling;
  const maxhp = def.maxhp + level * 4;
  return { species, name: def.name, type: def.type, sx: def.sx, sy: def.sy, level, hp: maxhp, maxhp };
}

function startBattle(canvasCtx, opts) {
  // opts: { enemySpecies, save, data, hooks: { onEnd } }
  const save = opts.save;
  const level = 1 + Math.min(4, Math.floor((save.wins || 0) / 4));
  const sheet = opts.sheet;
  const enemy = makeCreature(opts.enemySpecies, level);
  const starter = save.team[0] || { species: 'coinling' };
  const player = makeCreature(starter.species, 1);
  player.hp = player.maxhp; // scaffold: the team is healed after every battle
  const st = {
    enemy, player, save, data: opts.data, hooks: opts.hooks,
    sheet,
    phase: 'intro', timer: 0,
    question: null, correctCount: 0, questionsAsked: 0, lastLearnMore: null,
    fx: { playerLunge: 0, enemyLunge: 0, playerFlash: 0, enemyFlash: 0, shake: 0 },
    floats: [],
    ui: {
      card: document.getElementById('battle-ui'),
      qtext: document.getElementById('bq-text'),
      opts: document.getElementById('bq-options'),
      fb: document.getElementById('bq-feedback'),
      end: document.getElementById('bq-end'),
      endTitle: document.getElementById('bq-end-title'),
      endBody: document.getElementById('bq-end-body'),
      learn: document.getElementById('bq-learn'),
      cont: document.getElementById('bq-continue')
    }
  };
  st.ui.card.classList.remove('hidden');
  return st;
}

function showQuestion(st) {
  const topics = (CREATURES[st.enemy.species] || CREATURES.coinling).topics;
  const exclude = new Set(st.save.recentQuestions || []);
  st.question = pickQuestion(st.data, topics, exclude);
  rememberQuestion(st.save, st.question.id);
  if (st.question.learn_more) st.lastLearnMore = st.question.learn_more;
  st.questionsAsked++;
  const q = st.question;
  st.ui.fb.textContent = '';
  st.ui.fb.className = '';
  st.ui.qtext.textContent = q.type === 'calc' ? q.question + '  (work it out)' : q.question;
  st.ui.opts.innerHTML = '';
  q.options.forEach((opt, i) => {
    const b = document.createElement('button');
    b.className = 'bq-opt';
    b.textContent = opt;
    b.addEventListener('click', () => answer(st, i, b));
    st.ui.opts.appendChild(b);
  });
  const flee = document.createElement('button');
  flee.className = 'bq-flee';
  flee.textContent = 'Run away';
  flee.addEventListener('click', () => endBattle(st, 'flee'));
  st.ui.opts.appendChild(flee);
}

function answer(st, i, btn) {
  if (st.phase !== 'question') return;
  const q = st.question;
  const correct = i === q.answer;
  st.ui.opts.querySelectorAll('.bq-opt').forEach((b, bi) => {
    b.disabled = true;
    if (bi === q.answer) b.classList.add('correct');
    else if (bi === i && !correct) b.classList.add('wrong');
  });
  st.ui.fb.textContent = q.explanation || (correct ? 'Correct.' : 'Not this time.');
  st.ui.fb.className = correct ? 'good' : 'bad';
  if (correct) {
    st.correctCount++;
    st.phase = 'playerAttack'; st.timer = 0;
  } else {
    st.phase = 'enemyAttack'; st.timer = 0;
  }
}

function float(st, x, y, text, color) {
  st.floats.push({ x, y, text, color, t: 0 });
}

function damageTo(st, target, amount) {
  target.hp = Math.max(0, target.hp - amount);
  if (target === st.enemy) { st.fx.enemyFlash = 0.3; st.fx.enemyLunge = 0.18; float(st, 330, 96, '-' + amount, '#ffd24a'); }
  else { st.fx.playerFlash = 0.3; st.fx.playerLunge = 0.18; st.fx.shake = 0.25; float(st, 140, 210, '-' + amount, '#ff8a7a'); }
}

function endBattle(st, result, caught) {
  st.phase = 'done';
  const diff = st.question ? (st.question.difficulty || 1) : 1;
  const xp = st.correctCount * 8 * diff + (result === 'win' ? 25 : 0) + (caught ? 25 : 0);
  if (xp > 0) { st.save.xp += xp; awardXP(xp, 'battle'); }
  if (result === 'win') st.save.wins = (st.save.wins || 0) + 1;
  if (caught) st.save.dex[st.enemy.species] = (st.save.dex[st.enemy.species] || 0) + 1;
  // result: 'win' (enemy fainted or won over), 'lose' (your creature fainted), 'flee'
  const lm = st.lastLearnMore;
  st.ui.card.classList.add('hidden');
  st.ui.end.classList.remove('hidden');
  st.ui.endTitle.textContent = result === 'win' ? (caught ? st.enemy.name + ' joined your team!' : 'You won!') : result === 'lose' ? 'You blacked out...' : 'Got away safely.';
  st.ui.endBody.textContent = 'XP earned: ' + xp + (caught ? '   |   Team: ' + (st.save.wins || 0) + ' wins' : '');
  st.ui.learn.classList.toggle('hidden', !lm);
  if (lm) st.ui.learn.onclick = () => window.open('https://moneyhunters.co.uk/#' + lm, '_blank');
  st.ui.cont.onclick = () => {
    st.ui.end.classList.add('hidden');
    st.hooks.onEnd({ result, caught: !!caught, xp, learnMore: lm || null });
  };
}

// timed update; input unused (DOM buttons drive questions)
function updateBattle(st, dt) {
  for (const k of ['playerLunge', 'enemyLunge', 'playerFlash', 'enemyFlash', 'shake']) {
    if (st.fx[k] > 0) st.fx[k] = Math.max(0, st.fx[k] - dt);
  }
  st.floats = st.floats.filter(f => (f.t += dt) < 1);
  st.timer += dt;
  if (st.phase === 'intro' && st.timer > 1.1) {
    st.phase = 'question';
    showQuestion(st);
  } else if (st.phase === 'playerAttack' && st.timer > 0.15) {
    const eff = effectiveness(st.player.type, st.enemy.type);
    const dmg = Math.round((16 + 6 * (st.question.difficulty || 1)) * eff);
    damageTo(st, st.enemy, dmg);
    st.phase = 'afterPlayer'; st.timer = 0;
  } else if (st.phase === 'afterPlayer' && st.timer > 0.6) {
    if (st.enemy.hp <= 0) endBattle(st, 'win', true);
    else if (st.correctCount >= 3) endBattle(st, 'win', true);
    else { st.phase = 'question'; showQuestion(st); }
  } else if (st.phase === 'enemyAttack' && st.timer > 0.15) {
    const eff = effectiveness(st.enemy.type, st.player.type);
    const dmg = Math.max(1, Math.round((8 + 3 * st.enemy.level) * eff));
    damageTo(st, st.player, dmg);
    st.phase = 'afterEnemy'; st.timer = 0;
  } else if (st.phase === 'afterEnemy' && st.timer > 0.6) {
    if (st.player.hp <= 0) endBattle(st, 'lose');
    else { st.phase = 'question'; showQuestion(st); }
  }
}

function hpBar(ctx, x, y, w, frac, label, lvl) {
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.fillRect(x - 4, y - 4, w + 8, 30);
  ctx.fillStyle = '#fff';
  ctx.font = '9px monospace';
  ctx.fillText(label + '  Lv' + lvl, x, y + 6);
  ctx.fillStyle = '#333';
  ctx.fillRect(x, y + 11, w, 6);
  ctx.fillStyle = frac > 0.5 ? '#4ade80' : frac > 0.2 ? '#fbbf24' : '#ef4444';
  ctx.fillRect(x, y + 11, Math.round(w * frac), 6);
}

function drawBattle(ctx, st) {
  const shk = st.fx.shake > 0 ? (Math.random() * 4 - 2) : 0;
  ctx.save();
  ctx.translate(shk, 0);
  // arena
  const grad = ctx.createLinearGradient(0, 0, 0, VIEW_H);
  grad.addColorStop(0, '#1d3a5f'); grad.addColorStop(1, '#0f2233');
  ctx.fillStyle = grad;
  ctx.fillRect(-4, 0, VIEW_W + 8, VIEW_H);
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.beginPath(); ctx.ellipse(340, 110, 78, 22, 0, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(140, 246, 70, 20, 0, 0, Math.PI * 2); ctx.fill();
  ctx.imageSmoothingEnabled = false;
  // enemy (top right)
  const eOx = st.fx.enemyLunge > 0 ? -8 : 0;
  if (st.fx.enemyFlash <= 0 || Math.floor(st.timer * 20) % 2 === 0) {
    ctx.drawImage(st.sheet, st.enemy.sx, st.enemy.sy, 32, 32, 324 + eOx, 80, 64, 64);
  }
  // player creature (bottom left)
  const pOx = st.fx.playerLunge > 0 ? 8 : 0;
  ctx.drawImage(st.sheet, st.player.sx, st.player.sy, 32, 32, 108 + pOx, 214, 64, 64);
  // hp bars
  hpBar(ctx, 24, 24, 140, st.enemy.hp / st.enemy.maxhp, st.enemy.name, st.enemy.level);
  hpBar(ctx, VIEW_W - 164, 190, 140, st.player.hp / st.player.maxhp, st.player.name, st.player.level);
  // floats
  for (const f of st.floats) {
    ctx.globalAlpha = 1 - f.t;
    ctx.fillStyle = f.color;
    ctx.font = '12px monospace';
    ctx.fillText(f.text, f.x, f.y - f.t * 22);
    ctx.globalAlpha = 1;
  }
  // intro banner
  if (st.phase === 'intro') {
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(40, 140, 400, 36);
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText(st.enemy.name + ' blocks your path!', 70, 162);
  }
  ctx.restore();
}

export { startBattle, updateBattle, drawBattle, makeCreature, effectiveness, CREATURES, VIEW_W, VIEW_H };
