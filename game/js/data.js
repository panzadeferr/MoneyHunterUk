// data.js: loads game data from /data/ (network-first, same origin) and picks questions.
// Questions live in per-topic files under /data/questions/ listed in index.json.
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
  const [qIndex, p] = await Promise.all([
    fetchJSON('/data/questions/index.json'),
    fetchJSON('/data/playbook.json')
  ]);
  const playbook = (p && p.chapters) ? p : { chapters: [] };
  let questions = [];
  let investigations = [];
  if (qIndex && qIndex.files) {
    // legacy single-file fallback if the index lists it
    const parts = await Promise.all(
      Object.entries(qIndex.files).map(([topic, file]) => fetchJSON('/data/questions/' + file))
    );
    for (const part of parts) {
      if (part && part.questions && part.questions.length) {
        questions = questions.concat(part.questions);
      }
    }
    // investigations live in their own reviewed file, pointed to by the index
    if (qIndex.investigations_file) {
      const inv = await fetchJSON('/data/questions/' + qIndex.investigations_file);
      if (inv && inv.investigations && inv.investigations.length) {
        investigations = inv.investigations;
      }
    }
  } else {
    const legacy = await fetchJSON('/data/questions.json');
    if (legacy && legacy.questions) questions = legacy.questions;
  }
  const byTopic = {};
  for (const question of questions) {
    (byTopic[question.topic || 'general'] = byTopic[question.topic || 'general'] || []).push(question);
  }
  const investigationsByTopic = {};
  for (const investigation of investigations) {
    (investigationsByTopic[investigation.topic || 'general'] = investigationsByTopic[investigation.topic || 'general'] || []).push(investigation);
  }
  return { questions, byTopic, investigations, investigationsByTopic, playbook };
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
