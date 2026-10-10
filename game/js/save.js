// save.js: local save state, the shared Hunter XP hook, and the no-repeat question memory.
const KEY = 'mh_game_save_v1';
const RECENT_MAX = 60;

function defaultSave() {
  return {
    started: false,
    x: 20, y: 14, dir: 'down',
    team: [],            // [{species, name}]
    dex: {},             // species -> count won over
    wins: 0,
    xp: 0,
    recentQuestions: []
  };
}

function loadSave() {
  let s = defaultSave();
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) s = Object.assign(s, JSON.parse(raw));
  } catch (e) { /* corrupt save: start fresh */ }
  s.recentQuestions = Array.isArray(s.recentQuestions) ? s.recentQuestions : [];
  return s;
}

function saveGame(s) {
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* storage full or blocked */ }
}

function resetSave() {
  try { localStorage.removeItem(KEY); } catch (e) {}
}

// Shared Hunter XP. The main app levels one Hunter across app and game; until the
// app's awardXP lands (planned separate PR), the game writes the same localStorage
// key ('mh_xp') the app already reads, so totals line up on next app load.
function awardXP(amount, source) {
  const cur = parseInt(localStorage.getItem('mh_xp') || '0', 10) || 0;
  const next = Math.max(0, cur + amount);
  try { localStorage.setItem('mh_xp', String(next)); } catch (e) {}
  return next;
}

function rememberQuestion(s, id) {
  s.recentQuestions.push(id);
  if (s.recentQuestions.length > RECENT_MAX) s.recentQuestions.splice(0, s.recentQuestions.length - RECENT_MAX);
}

export { defaultSave, loadSave, saveGame, resetSave, awardXP, rememberQuestion, KEY };
