// data.js: loads game data from /data/ (network-first, same origin) and picks questions.
const CREATURES = {
  coinling: { name: 'Coinling', type: 'cash',  sx: 0,  sy: 48, maxhp: 34, topics: ['banking', 'cashback'] },
  piggle:   { name: 'Piggle',   type: 'save',  sx: 32, sy: 48, maxhp: 38, topics: ['saving', 'bills'] },
  budgit:   { name: 'Budgit',   type: 'grow',  sx: 64, sy: 48, maxhp: 30, topics: ['budgeting', 'shopping'] }
};

// simple circle: each type beats one and is beaten by one (expanded in a later task)
const TYPE_CHART = {
  cash: { strongVs: 'grow', weakVs: 'save' },
  save: { strongVs: 'cash', weakVs: 'grow' },
  grow: { strongVs: 'save', weakVs: 'cash' }
};

async function fetchJSON(url) {
  try {
    const res = await fetch(url + '?v=' + Date.now());
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

async function loadData() {
  const [q, p] = await Promise.all([
    fetchJSON('/data/questions.json'),
    fetchJSON('/data/playbook.json')
  ]);
  const questions = (q && q.questions) ? q.questions : [];
  const playbook = (p && p.chapters) ? p : { chapters: [] };
  const byTopic = {};
  for (const question of questions) {
    (byTopic[question.topic || 'general'] = byTopic[question.topic || 'general'] || []).push(question);
  }
  return { questions, byTopic, playbook };
}

// pick a question for a creature, avoiding recently seen ones (no-repeat rotation)
function pickQuestion(data, topics, exclude) {
  let pool = [];
  for (const t of topics) pool = pool.concat(data.byTopic[t] || []);
  if (!pool.length) pool = data.questions;
  const fresh = pool.filter(q => !exclude.has(q.id));
  const use = fresh.length ? fresh : pool;
  return use[Math.floor(Math.random() * use.length)];
}

export { CREATURES, TYPE_CHART, loadData, pickQuestion };
