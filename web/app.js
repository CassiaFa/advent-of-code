// Calendrier de l'Avent du Code : webapp statique, sans dépendance.
// Le contenu vient de data/content.json (généré par `npm run build`).
// Le code des joueurs ne s'exécute que dans judge.worker.js.

const KEY = "advent-code-v1";
const WORKER_URL = "judge.worker.js";
const ATTEMPTS_FOR_SOLUTION = 2;
const TIMEOUT_MS = { javascript: 3000, python: 5000 };
const INDENT = { javascript: "  ", python: "    " };
const DEFAULT_STATE = { lang: "javascript", level: "debutant", theme: "nuit", realDates: false, placementSeen: false, progress: {} };
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const $ = (sel, root = document) => root.querySelector(sel);
const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ESC[c]);

let content = null;
let state = loadState();
let flushPending = null; // enregistre le code en cours avant de changer de vue
let lastDayVisited = null;
let justSolved = null; // jour qui vient d'être réparé : sa porte s'allume au retour sur le calendrier

// ---------------------------------------------------------------- état

function loadState() {
  try {
    const brut = JSON.parse(localStorage.getItem(KEY) || "{}");
    return { ...DEFAULT_STATE, ...brut, progress: { ...(brut.progress || {}) } };
  } catch {
    return { ...DEFAULT_STATE };
  }
}

function saveState() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* stockage indisponible (navigation privée…) : on continue sans enregistrer */
  }
}

const progKey = (ex, lang = state.lang) => `${ex.id}:${lang}`;
const getProg = (ex) => state.progress[progKey(ex)] || { solved: false, attempts: 0 };
function setProg(ex, patch) {
  state.progress[progKey(ex)] = { ...getProg(ex), ...patch };
  saveState();
}

// ---------------------------------------------------------------- contenu

const findEx = (day, level = state.level) => content.exercises.find((e) => e.day === day && e.level === level);
const storyOf = (day) => content.story.find((s) => s.day === day);
const langInfo = () => content.meta.languages.find((l) => l.id === state.lang);
const levelInfo = (id = state.level) => content.meta.levels.find((l) => l.id === id);
const statementOf = (ex) => ex.statement.replaceAll("{fn}", ex.fn[state.lang]);

function isLocked(day) {
  if (!state.realDates) return false;
  const maintenant = new Date();
  const mois = maintenant.getMonth();
  if (mois === 0) return false; // en janvier, on rejoue tout
  if (mois < 11) return true;
  return maintenant.getDate() < day;
}

// ---------------------------------------------------------------- mini-markdown (échappé)

function inline(texte) {
  return texte
    .split("`")
    .map((seg, i) => (i % 2 ? `<code class="ic">${esc(seg)}</code>` : esc(seg).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")))
    .join("");
}

function md(texte) {
  const sortie = [];
  let para = [];
  let liste = [];
  let codes = [];
  const vider = () => {
    if (para.length) sortie.push("<p>" + para.map(inline).join("<br>") + "</p>");
    if (liste.length) sortie.push("<ul>" + liste.map((l) => "<li>" + inline(l) + "</li>").join("") + "</ul>");
    if (codes.length) sortie.push('<pre class="codeblock">' + codes.map(esc).join("\n") + "</pre>");
    para = [];
    liste = [];
    codes = [];
  };
  for (const ligne of texte.split("\n")) {
    if (ligne.trim() === "") {
      vider();
      continue;
    }
    const seul = ligne.match(/^`([^`]+)`$/);
    if (seul) {
      if (para.length || liste.length) vider();
      codes.push(seul[1]);
    } else if (/^- /.test(ligne)) {
      if (para.length || codes.length) vider();
      liste.push(ligne.slice(2));
    } else {
      if (liste.length || codes.length) vider();
      para.push(ligne);
    }
  }
  vider();
  return sortie.join("");
}

// Valeurs JSON écrites avec la syntaxe du langage choisi (True/False/None en Python).
function lit(valeur) {
  if (state.lang !== "python") return JSON.stringify(valeur);
  if (valeur === null) return "None";
  if (valeur === true) return "True";
  if (valeur === false) return "False";
  if (Array.isArray(valeur)) return "[" + valeur.map(lit).join(", ") + "]";
  if (typeof valeur === "object") return "{" + Object.entries(valeur).map(([k, v]) => `${JSON.stringify(k)}: ${lit(v)}`).join(", ") + "}";
  return JSON.stringify(valeur);
}

function gotLit(got) {
  if (got === "undefined" || got === "None") return got;
  try {
    return lit(JSON.parse(got));
  } catch {
    return got;
  }
}

// ---------------------------------------------------------------- exécution (Worker)

let pyWorker = null;

function executer(lang, code, ex, surStatut) {
  return new Promise((resolve) => {
    const worker = lang === "python" ? (pyWorker ||= new Worker(WORKER_URL)) : new Worker(WORKER_URL);
    let minuteur = null;
    let fini = false;

    const terminer = (rapport) => {
      if (fini) return;
      fini = true;
      clearTimeout(minuteur);
      worker.removeEventListener("message", surMessage);
      worker.removeEventListener("error", surErreur);
      if (lang !== "python") worker.terminate();
      resolve(rapport);
    };
    const tuer = (message) => {
      worker.terminate();
      if (lang === "python") pyWorker = null;
      terminer({ error: message, results: [], logs: "", timeout: true });
    };
    const surMessage = (e) => {
      const m = e.data;
      if (m.type === "loading") surStatut("Chargement de Python, première fois seulement (environ 10 Mo)…");
      else if (m.type === "running") {
        surStatut("Exécution…");
        minuteur = setTimeout(() => tuer(`Temps dépassé (${TIMEOUT_MS[lang] / 1000} s). Une boucle qui ne s'arrête jamais ? Vérifie la condition d'arrêt. Sinon, ton code est peut-être juste trop lent pour un des tests.`), TIMEOUT_MS[lang]);
      } else if (m.type === "result") terminer(m.payload);
    };
    const surErreur = () => {
      worker.terminate();
      if (lang === "python") pyWorker = null;
      terminer({ error: "Le moteur d'exécution n'a pas démarré. Ouvre la page avec `npm run dev`, pas en double-cliquant sur le fichier.", results: [], logs: "" });
    };

    worker.addEventListener("message", surMessage);
    worker.addEventListener("error", surErreur);
    worker.postMessage({ lang, code, fn: ex.fn[lang], tests: ex.tests });
  });
}

// ---------------------------------------------------------------- coloration syntaxique
// Maison, sans dépendance : un découpage en une passe, suffisant pour des exercices courts.
// Limites connues : littéraux regex JavaScript et expressions imbriquées dans les gabarits non reconnus.
// Classes CSS : k mot-clé, f fonction, s chaîne, n nombre ou constante, c commentaire, p propriété, u ponctuation.

const SYNTAX = {
  javascript: {
    re: /(\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|$))|(`(?:\\[\s\S]|[^`\\])*`?|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)|(\b\d[\w.]*)|([A-Za-z_$][\w$]*)|([^\sA-Za-z_$\d"'`\/]+|\/)/g,
    keywords: new Set("async await break case catch class const continue default delete do else export extends finally for from function if import in instanceof let new of return static super switch this throw try typeof var void while yield".split(" ")),
    constants: new Set(["true", "false", "null", "undefined", "NaN", "Infinity"]),
  },
  python: {
    re: /(#[^\n]*)|((?:[rRbBfFuU]{1,2})?(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?))|(\b\d[\w.]*)|([A-Za-z_]\w*)|([^\sA-Za-z_\d"'#]+)/g,
    keywords: new Set("and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield match case".split(" ")),
    constants: new Set(["True", "False", "None"]),
  },
};

function highlight(code, lang) {
  const regles = SYNTAX[lang];
  if (!regles) return esc(code);
  const re = new RegExp(regles.re.source, "g");
  const span = (cls, texte) => `<span class="${cls}">${esc(texte)}</span>`;
  let html = "";
  let fin = 0;
  let apresPoint = false;
  let m;
  while ((m = re.exec(code))) {
    html += esc(code.slice(fin, m.index));
    fin = re.lastIndex;
    const [tout, commentaire, chaine, nombre, mot, ponctuation] = m;
    if (commentaire) html += span("c", tout);
    else if (chaine) html += span("s", tout);
    else if (nombre) html += span("n", tout);
    else if (mot) {
      const appel = /^[ \t]*\(/.test(code.slice(fin, fin + 8));
      if (!apresPoint && regles.keywords.has(mot)) html += span("k", mot);
      else if (!apresPoint && regles.constants.has(mot)) html += span("n", mot);
      else if (appel) html += span("f", mot);
      else if (apresPoint) html += span("p", mot);
      else html += esc(mot);
    } else html += span("u", tout);
    apresPoint = !!ponctuation && ponctuation.endsWith(".") && !ponctuation.endsWith("..");
    if (re.lastIndex === m.index) re.lastIndex++; // garde-fou : jamais de boucle infinie
  }
  return html + esc(code.slice(fin));
}

// ---------------------------------------------------------------- icônes (SVG en trait, jamais d'emoji)

const ICONS = {
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  back: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  prev: '<path d="M15 6l-6 6 6 6"/>',
  next: '<path d="M9 6l6 6-6 6"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  cross: '<path d="M6 6l12 12M18 6L6 18"/>',
  lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
  unlock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 7.5-2"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"/>',
  reset: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
  flake: '<path d="M12 2v6M12 16v6M2 12h6M16 12h6M5 5l3.5 3.5M15.5 15.5L19 19M5 19l3.5-3.5M15.5 8.5L19 5"/>',
  frost: '<circle cx="12" cy="12" r="4"/><path d="M12 3v4M12 17v4M4.2 7.5l3.5 2M16.3 14.5l3.5 2M4.2 16.5l3.5-2M16.3 9.5l3.5-2"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
};
// `label` : l'icône porte une information (lue par les lecteurs d'écran). Sinon elle est décorative.
const ico = (nom, { sm = false, label = "", style = "" } = {}) =>
  `<svg class="ico${sm ? " ico--sm" : ""}" viewBox="0 0 24 24"${label ? ` role="img" aria-label="${esc(label)}"` : ' aria-hidden="true"'}${style ? ` style="${style}"` : ""}>${ICONS[nom]}</svg>`;
const ICO_PLAY = '<svg class="ico ico--sm" viewBox="0 0 24 24" aria-hidden="true" style="fill: currentColor; stroke: none"><path d="M7 4.5v15l12-7.5z"/></svg>';
const SPARK = '<path d="M12 2l2 8 8 2-8 2-2 8-2-8-8-2 8-2z"/>';
const pluriel = (n, mot) => `${n} ${mot}${n > 1 ? "s" : ""}`;

// ---------------------------------------------------------------- en-tête et routage

const segment = (items, courant) =>
  items.map((it) => `<button type="button" class="seg__btn" data-id="${esc(it.id)}" aria-pressed="${it.id === courant}">${esc(it.label)}</button>`).join("");

function applyTheme() {
  const matin = state.theme === "matin";
  document.documentElement.classList.toggle("t-matin", matin);
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", matin ? "#eef3f7" : "#070f18");
}

function buildChrome() {
  $("#tagline").textContent = `${content.meta.tagline} Chaque exercice réussi rallume une fenêtre du village.`;
  // 14 flocons, lents, seulement dans l'en-tête (coupés par prefers-reduced-motion dans le CSS).
  $("#snow").innerHTML = [6, 13, 21, 29, 36, 44, 52, 58, 64, 71, 77, 84, 90, 96]
    .map((l, i) => {
      const s = [2, 3, 2, 4, 2, 3][i % 6];
      return `<i class="flake" style="left: ${l}%; width: ${s}px; height: ${s}px; animation-duration: ${14 + ((i * 7) % 11)}s; animation-delay: ${-((i * 3.7) % 14)}s"></i>`;
    })
    .join("");
  syncChrome();

  const choisir = (cle) => (e) => {
    const bouton = e.target.closest(".seg__btn");
    if (!bouton || bouton.dataset.id === state[cle]) return;
    state[cle] = bouton.dataset.id;
    saveState();
    syncChrome();
    route();
  };
  $("#seg-lang").addEventListener("click", choisir("lang"));
  $("#seg-level").addEventListener("click", choisir("level"));

  $("#chk-dates").addEventListener("click", () => {
    state.realDates = !state.realDates;
    saveState();
    syncChrome();
    route();
  });
  $("#chk-theme").addEventListener("click", () => {
    state.theme = state.theme === "matin" ? "nuit" : "matin";
    saveState();
    applyTheme();
    syncChrome();
  });

  const boite = $("#menu");
  const bouton = $("#btn-menu");
  const panneau = $("#reglages");
  const basculerMenu = (ouvert) => {
    panneau.hidden = !ouvert;
    bouton.setAttribute("aria-expanded", String(ouvert));
  };
  bouton.addEventListener("click", () => basculerMenu(panneau.hidden));
  document.addEventListener("click", (e) => {
    if (!panneau.hidden && !boite.contains(e.target)) basculerMenu(false);
  });
  boite.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panneau.hidden) {
      basculerMenu(false);
      bouton.focus();
    }
  });

  $("#btn-placement").addEventListener("click", () => {
    basculerMenu(false);
    openPlacement();
  });
  $("#btn-reset-all").addEventListener("click", () => {
    if (confirm("Effacer toute ta progression et ton code dans ce navigateur ? Cette action est définitive.")) {
      try {
        localStorage.removeItem(KEY);
      } catch {
        /* rien à faire */
      }
      location.hash = "#/";
      location.reload();
    }
  });

  // Ouvrir une porte : le seul moment spectaculaire. Un clic « normal » uniquement
  // (Ctrl/Cmd-clic ouvre un onglet comme d'habitude), et jamais si l'on a demandé moins d'animations.
  $("#grid").addEventListener("click", (e) => {
    const porte = e.target.closest("a.door");
    if (!porte || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (reduceMotion.matches) return;
    e.preventDefault();
    openDoor(Number(porte.dataset.day));
  });
}

function syncChrome() {
  $("#seg-lang").innerHTML = segment(content.meta.languages, state.lang);
  $("#seg-level").innerHTML = segment(content.meta.levels, state.level);
  $("#chk-dates").setAttribute("aria-checked", String(!!state.realDates));
  $("#chk-theme").setAttribute("aria-checked", String(state.theme === "matin"));
}

function route() {
  if (flushPending) flushPending();
  flushPending = null;
  const m = location.hash.match(/^#\/jour\/(\d+)$/);
  const jour = m ? Number(m[1]) : null;
  if (jour && jour >= 1 && jour <= 24) showDay(jour);
  else showCalendar();
}

// ---------------------------------------------------------------- ouverture d'une porte

// 0 → 200 ms : le voile arrive, la poignée s'enfonce, la couronne frémit.
// 200 → 1100 ms : le battant pivote sur sa charnière gauche, le halo ambre grandit, 8 flocons s'échappent.
// 1500 ms : on entre (navigation), le voile se dissipe. Un clic ou une touche de plus passe l'animation.
function openDoor(n) {
  const cible = `#/jour/${n}`;
  const eclats = Array.from({ length: 8 }, (_, i) => {
    const angle = (i / 8) * 2 * Math.PI + 0.4;
    const portee = 120 + (i % 3) * 26;
    return `<i class="burst" style="--dx: ${Math.round(Math.cos(angle) * portee)}px; --dy: ${Math.round(Math.sin(angle) * portee - 24)}px; animation-delay: ${(0.25 + i * 0.05).toFixed(2)}s"></i>`;
  }).join("");

  const voile = document.createElement("div");
  voile.className = "opening";
  voile.innerHTML = `
    <div class="opening__in">
      <div class="door3d door--c${n % 3}${n === 24 ? " door--noel" : ""}" aria-hidden="true">
        <div class="door3d__glow"></div>
        <div class="door3d__num">${n}</div>
        ${eclats}
        <div class="door3d__leaf"><span class="wreath"></span><span class="plaque">${n}</span><span class="knob"></span></div>
        <div class="door3d__cap"></div>
        <div class="door3d__sill"></div>
      </div>
      <p class="opening__cap" aria-hidden="true"><span class="eyebrow">Jour ${n} sur 24</span><strong>${esc(storyOf(n).title)}</strong></p>
    </div>`;
  document.body.append(voile);

  let parti = false;
  const minuteurs = [];
  const passer = () => partir();
  const partir = () => {
    if (parti) return;
    parti = true;
    minuteurs.forEach(clearTimeout);
    document.removeEventListener("keydown", passer);
    location.hash = cible;
    voile.classList.add("is-out");
    setTimeout(() => voile.remove(), 420);
  };
  voile.addEventListener("click", partir);
  requestAnimationFrame(() => requestAnimationFrame(() => voile.classList.add("is-in")));
  minuteurs.push(setTimeout(() => voile.classList.add("is-open"), 200));
  // La touche qui a ouvert la porte (Entrée) ne doit pas aussi passer l'animation.
  minuteurs.push(setTimeout(() => document.addEventListener("keydown", passer), 350));
  minuteurs.push(setTimeout(partir, 1500));
}

// ---------------------------------------------------------------- calendrier

const conceptOf = (day) => content.days?.find((d) => d.day === day)?.concept || findEx(day)?.concept || "";
const solvedAt = (day, niveau) => {
  const ex = findEx(day, niveau);
  return !!ex && !!state.progress[progKey(ex)]?.solved;
};

// Une pastille par niveau : pleine si l'exercice de ce niveau est réparé dans le langage courant.
const levelPips = (day) => content.meta.levels.map((l) => `<i class="pip${solvedAt(day, l.id) ? " pip--on" : ""}"></i>`).join("");

// Le village : 4 maisons, 6 fenêtres chacune. L'ordre mélange les jours pour que la lumière se répande partout.
const HOUSES = [
  { l: 3, w: 20, top: 54, rt: 34 },
  { l: 26, w: 25, top: 42, rt: 17, chim: true },
  { l: 55, w: 18, top: 58, rt: 41 },
  { l: 76, w: 21, top: 47, rt: 27, chim: true },
];
const WINDOW_ORDER = [7, 0, 14, 20, 3, 11, 18, 5, 22, 9, 1, 16, 12, 23, 4, 19, 8, 2, 15, 10, 21, 6, 13, 17];

function villageHtml(etatDuJour) {
  let html = '<div class="moon"></div>';
  const fenetres = [];
  for (const h of HOUSES) {
    const toit = Math.round(((h.top - h.rt) / (94 - h.rt)) * 1000) / 10;
    html += `<div class="house" style="left: ${h.l}%; width: ${h.w}%; top: ${h.rt}%; bottom: 6%">
      ${h.chim ? '<div class="house__chim" style="left: 68%; top: 4%; height: 22%"></div>' : ""}
      <div class="house__roof" style="top: 0; height: ${toit}%"></div>
      <div class="house__body" style="top: ${toit}%"></div>
    </div>`;
    const dispo = 86 - (h.top + 5);
    const haut = dispo * 0.34;
    for (let r = 0; r < 2; r++)
      for (let c = 0; c < 3; c++) fenetres.push({ x: h.l + h.w * (0.12 + c * 0.29), y: h.top + 5 + r * (haut + dispo * 0.2), w: h.w * 0.18, h: haut });
  }
  fenetres.forEach((f, idx) => {
    const jour = WINDOW_ORDER.indexOf(idx) + 1;
    const cls = { lit: " win--lit", cur: " win--cur" }[etatDuJour(jour)] || "";
    html += `<i class="win${cls}" data-day="${jour}" style="left: ${f.x.toFixed(2)}%; top: ${f.y.toFixed(2)}%; width: ${f.w.toFixed(2)}%; height: ${f.h.toFixed(2)}%"></i>`;
  });
  return html + '<div class="ground"></div>';
}

function showCalendar() {
  $("#view-day").hidden = true;
  $("#view-calendar").hidden = false;
  document.title = content.meta.title;

  const grille = $("#grid");
  let reussis = 0;
  let suivant = null;
  let prochainVerrou = null;
  const etats = {};
  const cartes = [];

  for (let n = 1; n <= 24; n++) {
    const histoire = storyOf(n);
    const ex = findEx(n);
    const verrou = isLocked(n);
    const prog = ex ? getProg(ex) : null;
    const resolu = !!prog?.solved;
    const commence = !!prog && !resolu && (prog.attempts > 0 || prog.code !== undefined);
    if (resolu) reussis++;
    if (ex && !resolu && !verrou && suivant === null) suivant = n;
    if (verrou && prochainVerrou === null) prochainVerrou = n;

    const noel = n === 24;
    const etat = verrou ? "locked" : resolu ? "lit" : commence ? "cur" : "open";
    etats[n] = etat;
    const libelle = verrou ? `verrouillée, ouvre le ${n} décembre` : !ex ? "histoire seulement" : { lit: "réparée", cur: "en cours", open: "disponible" }[etat];
    const badge = verrou
      ? `<span class="badge badge--lock">${ico("lock")}${n} déc.</span>`
      : resolu
        ? `<span class="badge badge--ok">${ico("check")}réparée</span>`
        : commence
          ? '<span class="badge badge--cur">en cours</span>'
          : noel
            ? '<span class="badge badge--noel">Nuit spéciale</span>'
            : `<span>${ex ? "À ouvrir" : "Histoire"}</span>`;
    // La porte qui vient d'être réparée s'affiche entrouverte, puis s'ouvre en grand (voir plus bas).
    const classeEtat = justSolved === n ? "cur" : etat;
    const interieur = `
        <div class="door__pane" aria-hidden="true">
          <span class="door__lights"></span>
          ${noel ? '<svg class="door__star" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.6 6.6L21 9.3l-5 4.4 1.6 6.8L12 16.9 6.4 20.5 8 13.7 3 9.3l6.4-.7z"/></svg>' : ""}
          <div class="door__arch">
            <div class="door__inside">
              <span class="door__inum">${n}</span>
              <svg class="door__tree" viewBox="0 0 24 30" fill="currentColor"><path d="M12 1l5 8h-3l5 7h-3l5 8H3l5-8H5l5-7H7z"/><rect x="10.5" y="24" width="3" height="5"/></svg>
            </div>
            <div class="door__leaf"><span class="wreath"></span><span class="plaque">${n}</span><span class="knob"></span></div>
            <span class="door__cap"></span>
          </div>
        </div>
        <div class="door__body">
          <span class="door__title">${esc(histoire.title)}</span>
          <span class="door__notion">${esc(conceptOf(n))}</span>
          <span class="door__foot">${badge}<span class="pips" aria-hidden="true">${levelPips(n)}</span></span>
        </div>`;
    const classe = `door door--${classeEtat} door--c${n % 3}${noel ? " door--noel" : ""}`;
    const aria = `Jour ${n} : ${histoire.title}. ${conceptOf(n)}. ${libelle}${noel ? ", nuit de Noël" : ""}.`;
    cartes.push(
      verrou
        ? `<li><div class="${classe}" data-day="${n}" role="img" aria-label="${esc(aria)}">${interieur}</div></li>`
        : `<li><a class="${classe}" href="#/jour/${n}" data-day="${n}" aria-label="${esc(aria)}">${interieur}</a></li>`
    );
  }
  grille.innerHTML = cartes.join("");

  // Le village sert de jauge : une fenêtre par jour, pour le niveau et le langage courants.
  const allume = justSolved;
  const village = $("#village");
  village.innerHTML = villageHtml((jour) => (jour === allume ? "" : etats[jour] === "lit" ? "lit" : jour === suivant ? "cur" : ""));
  village.setAttribute("aria-label", `Givreville : ${pluriel(reussis, "fenêtre")} allumée${reussis > 1 ? "s" : ""} sur 24`);
  const ticks = Array.from({ length: 24 }, (_, i) => `<i class="tick${etats[i + 1] === "lit" ? " tick--on" : i + 1 === suivant ? " tick--cur" : ""}"></i>`).join("");
  $("#gauge").innerHTML = `
    <div class="gauge__num">${reussis}<span>/ 24</span></div>
    <div>
      <div class="gauge__label">${reussis === 0 ? "Aucune fenêtre rallumée… pour l'instant" : `${pluriel(reussis, "fenêtre")} rallumée${reussis > 1 ? "s" : ""}`}</div>
      <div class="gauge__sub">${esc(levelInfo().label)} · ${esc(langInfo().label)}</div>
    </div>
    <div class="ticks" aria-hidden="true">${ticks}</div>`;

  // Retour d'une réussite : la porte s'ouvre en grand et sa fenêtre s'allume au village.
  if (allume) {
    justSolved = null;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        const porte = $(`.door[data-day="${allume}"]`);
        porte?.classList.replace("door--cur", "door--lit");
        $(`.win[data-day="${allume}"]`)?.classList.add("win--lit");
      })
    );
  }

  const reprise = $("#resume");
  const meta = `<span class="hero__meta">${ico("clock", { sm: true })}${prochainVerrou ? `Prochaine porte le ${prochainVerrou === 1 ? "1er" : prochainVerrou} décembre` : "Toutes les portes sont ouvertes"}</span>`;
  if (suivant !== null) {
    const debut = reussis === 0 && !Object.keys(state.progress).length;
    const texte = debut ? `Commencer : jour ${suivant}, ${storyOf(suivant).title}` : `Reprendre au jour ${suivant} · ${storyOf(suivant).title}`;
    reprise.innerHTML = `<a class="btn btn--primary btn--lg" href="#/jour/${suivant}">${esc(texte)}${ico("arrow")}</a>${meta}`;
  } else if (reussis === 24) {
    reprise.innerHTML = `<p class="hero__note">Tout est réparé à ce niveau. Givreville te dit merci ! Envie d'essayer un autre niveau ou l'autre langage ?</p>`;
  } else {
    reprise.innerHTML = `<p class="hero__note">La prochaine porte n'est pas encore ouverte. Reviens demain, ou désactive « Une porte par jour » dans les réglages.</p>${meta}`;
  }

  // Première visite : on propose le test de niveau sans l'imposer.
  const accueil = $("#welcome");
  accueil.hidden = !!state.placementSeen;
  if (!state.placementSeen) {
    accueil.innerHTML = `
      <div class="welcome">
        <div class="welcome__pic" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 19c2-7 7-12 15-15 1 5 3 10 5 15"/><circle cx="25" cy="4" r="1.6"/><path d="M9 19h22"/><circle cx="20" cy="26" r="8"/><path d="M12 24l-5-3 2 6M28 24l5-3-2 6"/><circle cx="17" cy="25" r=".9" fill="currentColor"/><circle cx="23" cy="25" r=".9" fill="currentColor"/><path d="M17.5 29c1.5 1 3.5 1 5 0"/></svg>
        </div>
        <div>
          <h2 id="bienvenue">Première visite ? Pixel t'attendait.</h2>
          <p>Choisis ton langage et ton niveau en haut de la page. Si tu hésites, un petit test suffit pour te proposer un niveau. Tu pourras en changer à tout moment.</p>
        </div>
        <div class="welcome__actions">
          <button class="btn btn--primary" type="button" id="btn-welcome-test">Faire le test de niveau</button>
          <button class="btn btn--secondary" type="button" id="btn-welcome-skip">Je choisis moi-même</button>
        </div>
      </div>`;
    $("#btn-welcome-test").addEventListener("click", () => openPlacement());
    $("#btn-welcome-skip").addEventListener("click", () => {
      state.placementSeen = true;
      saveState();
      accueil.hidden = true;
      accueil.innerHTML = "";
    });
  } else {
    accueil.innerHTML = "";
  }

  if (lastDayVisited) {
    $(`a.door[data-day="${lastDayVisited}"]`)?.focus({ preventScroll: false });
    lastDayVisited = null;
  }
}

// ---------------------------------------------------------------- une journée

function showDay(n) {
  $("#view-calendar").hidden = true;
  const vue = $("#view-day");
  vue.hidden = false;
  lastDayVisited = n;
  window.scrollTo(0, 0);

  const histoire = storyOf(n);
  document.title = `Jour ${n} : ${histoire.title} — ${content.meta.title}`;
  const nav = `
    <nav class="daynav" aria-label="Navigation entre les jours">
      <a class="back" href="#/">${ico("back")}Le calendrier</a>
      <div class="pager">
        ${n > 1 ? `<a class="btn btn--secondary" href="#/jour/${n - 1}" aria-label="Jour précédent : jour ${n - 1}">${ico("prev", { sm: true })}Jour ${n - 1}</a>` : ""}
        ${n < 24 ? `<a class="btn btn--secondary" href="#/jour/${n + 1}" aria-label="Jour suivant : jour ${n + 1}">Jour ${n + 1}${ico("next", { sm: true })}</a>` : ""}
      </div>
    </nav>`;
  const entete = (statut, repare) => `
    <header class="day__head">
      <div class="daybadge door--c${n % 3}${n === 24 ? " door--noel" : ""} ${repare ? "daybadge--lit" : "daybadge--glass"}" id="day-badge" aria-hidden="true"><span>${n}</span></div>
      <div>
        <p class="eyebrow">Jour ${n} sur 24 · <span id="day-status">${esc(statut)}</span></p>
        <h1 class="day__title" id="day-title" tabindex="-1"><span class="sr">Jour ${n} : </span>${esc(histoire.title)}</h1>
      </div>
    </header>`;
  const vide = (icone, titre, texte) => `<div class="empty"><div class="empty__ic" aria-hidden="true">${ico(icone)}</div><h3>${titre}</h3>${texte}</div>`;

  if (isLocked(n)) {
    vue.innerHTML = `${nav}<article style="padding: 16px 0 24px">${entete("verrouillée", false)}
      <div style="margin-top: 28px">${vide("lock", `Cette porte s'ouvre le ${n === 1 ? "1er" : n} décembre`, "<p>Tu veux jouer dès maintenant ? Désactive « Une porte par jour » dans les réglages, en haut de la page.</p>")}</div></article>`;
    $("#day-title").focus({ preventScroll: true });
    return;
  }

  const ex = findEx(n);
  // Lettrine : seulement si le conte commence par une lettre.
  const lettrine = /^\p{L}/u.test(histoire.text);
  const conte = `
    <section class="tale" aria-label="Le conte du jour">
      <p class="tale__label">Le conte · nuit ${n}</p>
      <p>${lettrine ? `<span class="drop" aria-hidden="true">${esc(histoire.text[0])}</span><span class="sr">${esc(histoire.text[0])}</span>${esc(histoire.text.slice(1))}` : esc(histoire.text)}</p>
    </section>`;

  if (!ex) {
    const autre = content.meta.levels.find((l) => l.id !== state.level && findEx(n, l.id));
    vue.innerHTML = `${nav}<article style="padding: 16px 0 24px">${entete("en travaux", false)}${conte}
      ${vide(
        "flake",
        `Pas encore d'exercice au niveau ${esc(levelInfo().label)}`,
        autre ? `<p style="margin-top: 16px"><button class="btn btn--secondary" type="button" id="btn-other-level">Passer au niveau ${esc(autre.label)}</button></p>` : "<p>Reviens bientôt : cette porte est encore en travaux.</p>"
      )}</article>`;
    $("#btn-other-level")?.addEventListener("click", () => {
      state.level = autre.id;
      saveState();
      syncChrome();
      route();
    });
    $("#day-title").focus({ preventScroll: true });
    return;
  }

  const lang = state.lang;
  const prog = getProg(ex);
  const fichier = `jour-${String(n).padStart(2, "0")}.${langInfo().ext}`;
  const libelleStatut = (p) => (p.solved ? "réparée" : p.attempts > 0 ? pluriel(p.attempts, "essai") : "à réparer");
  const exemples = ex.tests
    .filter((t) => !t.hidden)
    .slice(0, 3)
    .map((t) => `${esc(`${ex.fn[lang]}(${t.args.map(lit).join(", ")})`)}  <span class="arr">→</span>  ${esc(lit(t.expected))}`)
    .join("\n");
  const niveaux = content.meta.levels
    .filter((l) => findEx(n, l.id))
    .map((l) => {
      const fait = solvedAt(n, l.id);
      return `<button type="button" class="chip" data-level="${esc(l.id)}" aria-pressed="${l.id === state.level}">${fait ? ico("check") : ""}${esc(l.label)}${fait ? '<span class="sr"> (réparé)</span>' : ""}</button>`;
    })
    .join("");

  vue.innerHTML = `${nav}
    <div class="day">
      <article>
        ${entete(libelleStatut(prog), prog.solved)}
        ${conte}
        <section class="card" aria-labelledby="exo-title">
          <div class="chips" role="group" aria-label="Version de l'exercice">${niveaux}</div>
          <h2 class="ex-title" id="exo-title">${esc(ex.title)}</h2>
          <p class="notion"><span class="badge badge--notion">Notion</span>${esc(ex.concept)}</p>
          <div class="prose">${md(statementOf(ex))}</div>
          <p class="label-sm">Exemples</p>
          <pre class="codeblock">${exemples}</pre>
          <details class="hint">
            <summary>${ico("bulb")}Un indice<small>sans spoiler</small></summary>
            <div class="hint__body">${inline(ex.hint)}</div>
          </details>
        </section>
      </article>

      <section aria-label="Ton code et les résultats">
        <div class="editor">
          <div class="editor__bar">
            <span class="tab"><span class="tab__lang">${esc(langInfo().ext.toUpperCase())}</span>${esc(fichier)}</span>
            <span class="grow"></span>
            <button class="btn btn--ghost" type="button" id="btn-reset">${ico("reset", { sm: true })}Réinitialiser</button>
            <button class="btn btn--primary" type="button" id="btn-run">${ICO_PLAY}Tester<span class="kbd" aria-hidden="true">Ctrl ↵</span></button>
          </div>
          <div class="code">
            <pre class="gutter" id="gutter" aria-hidden="true"></pre>
            <div class="code__area" id="code-area">
              <pre class="hl" aria-hidden="true"><code id="hl"></code></pre>
              <textarea id="code" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off"
                        aria-label="Ton code en ${esc(langInfo().label)}, ${esc(fichier)}"></textarea>
            </div>
          </div>
          <div class="editor__foot">
            <span><span class="kbd">Ctrl</span>+<span class="kbd">Entrée</span> lance les tests</span>
            <span>Quitter l'éditeur au clavier : <span class="kbd">Échap</span> puis <span class="kbd">Tab</span></span>
          </div>
        </div>
        <p class="status" id="status" role="status"></p>
        <div class="results" id="results" aria-live="polite"></div>
        <div class="unlock" id="solution"></div>
      </section>
    </div>`;

  vue.querySelector(".chips").addEventListener("click", (e) => {
    const pastille = e.target.closest(".chip");
    if (!pastille || pastille.dataset.level === state.level) return;
    state.level = pastille.dataset.level;
    saveState();
    syncChrome();
    route();
  });

  const ta = $("#code");
  const gouttiere = $("#gutter");
  const statut = $("#status");
  const resultats = $("#results");
  let solutionVisible = false;
  let enCours = false;
  let tabLibre = false;
  let minuteurSauvegarde = null;

  ta.value = prog.code ?? ex.starter[lang];
  // Le calque coloré vit sous la zone de saisie (texte transparent, curseur visible) et la suit au défilement.
  const calque = $("#hl");
  const zone = $("#code-area");
  zone.style.tabSize = INDENT[lang].length;
  const colorer = () => {
    calque.innerHTML = highlight(ta.value, lang) + "\n";
    zone.classList.add("has-hl");
  };
  const suivre = () => {
    gouttiere.scrollTop = ta.scrollTop;
    calque.style.transform = `translate(${-ta.scrollLeft}px, ${-ta.scrollTop}px)`;
  };

  const etatVide = () => {
    resultats.innerHTML = vide("flake", "Rien à afficher pour l'instant", "<p>Écris ta fonction, puis lance les tests. Les résultats s'affichent ici, un par un.</p>");
  };
  const majGouttiere = () => {
    const lignes = ta.value.split("\n").length;
    gouttiere.textContent = Array.from({ length: lignes }, (_, i) => i + 1).join("\n");
    colorer();
    suivre();
  };
  const sauver = () => {
    clearTimeout(minuteurSauvegarde);
    if (ta.value !== (getProg(ex).code ?? ex.starter[lang])) setProg(ex, { code: ta.value });
  };
  flushPending = sauver;
  majGouttiere();
  etatVide();

  ta.addEventListener("input", () => {
    majGouttiere();
    clearTimeout(minuteurSauvegarde);
    minuteurSauvegarde = setTimeout(sauver, 400);
  });
  ta.addEventListener("scroll", suivre);

  // Remplace une plage en gardant l'historique d'annulation quand le navigateur le permet.
  const remplacer = (debut, fin, texte) => {
    ta.focus();
    ta.setSelectionRange(debut, fin);
    if (!document.execCommand("insertText", false, texte)) {
      ta.setRangeText(texte, debut, fin, "end");
      ta.dispatchEvent(new Event("input"));
    }
  };

  ta.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      tabLibre = true;
      return;
    }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      lancer();
      return;
    }
    if (e.key === "Tab") {
      if (tabLibre) return; // Échap puis Tab : on laisse le focus sortir
      e.preventDefault();
      const ind = INDENT[lang];
      const { selectionStart: s, selectionEnd: f, value: v } = ta;
      if (s === f && !e.shiftKey) return remplacer(s, f, ind);
      const debutLigne = v.lastIndexOf("\n", s - 1) + 1;
      const bloc = v.slice(debutLigne, f).split("\n");
      const neuf = bloc.map((l) => (e.shiftKey ? l.replace(new RegExp("^( {1," + ind.length + "}|\\t)"), "") : ind + l)).join("\n");
      remplacer(debutLigne, f, neuf);
      ta.setSelectionRange(debutLigne, debutLigne + neuf.length);
      return;
    }
    tabLibre = false;
    if (e.key === "Enter" && !e.shiftKey && !e.altKey) {
      const { selectionStart: s, selectionEnd: f, value: v } = ta;
      const debutLigne = v.lastIndexOf("\n", s - 1) + 1;
      const avant = v.slice(debutLigne, s);
      let marge = avant.match(/^[ \t]*/)[0];
      const ouvre = lang === "python" ? /:\s*$/ : /[{(\[]\s*$/;
      if (ouvre.test(avant)) marge += INDENT[lang];
      if (marge) {
        e.preventDefault();
        remplacer(s, f, "\n" + marge);
      }
    }
  });

  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("Remettre le code de départ ? Ton code actuel sera perdu.")) return;
    ta.value = ex.starter[lang];
    majGouttiere();
    sauver();
    etatVide();
    ta.focus();
  });

  const afficherSolution = () => {
    const p = getProg(ex);
    const debloquee = p.solved || p.attempts >= ATTEMPTS_FOR_SOLUTION;
    const zone = $("#solution");
    if (!debloquee) {
      const reste = ATTEMPTS_FOR_SOLUTION - p.attempts;
      zone.innerHTML = `<p>${ico("lock")}<span>La solution se débloque après ${ATTEMPTS_FOR_SOLUTION} essais, ou dès que tes tests passent. Encore ${pluriel(reste, "essai")}.</span></p>
        <button class="btn btn--secondary" type="button" disabled>Voir la solution</button>`;
      return;
    }
    zone.innerHTML = `<p>${ico("unlock", { style: "color: var(--ok)" })}<span>Solution débloquée. Compare-la à la tienne : il y a souvent plusieurs bonnes réponses.</span></p>
      <button class="btn btn--secondary" type="button" id="btn-solution" aria-expanded="${solutionVisible}">${solutionVisible ? "Masquer la solution" : "Voir la solution"}</button>
      ${solutionVisible ? `<pre class="codeblock solution__code">${highlight(ex.solution[lang], lang)}</pre>` : ""}`;
    $("#btn-solution").addEventListener("click", () => {
      solutionVisible = !solutionVisible;
      afficherSolution();
      $("#btn-solution").focus();
    });
  };

  const ligneTest = (r) => {
    const marque = r.ok
      ? `<span class="test__ic ic-ok">${ico("check", { label: "réussi" })}</span>`
      : `<span class="test__ic ic-ko">${ico("cross", { label: "échoué" })}</span>`;
    if (r.hidden) {
      return `<li class="test${r.ok ? "" : " test--ko"}"><div class="test__row">${marque}<span class="test__call">Test caché</span><span class="test__tag">contenu masqué</span></div>
        ${r.ok ? "" : `<dl class="test__detail"><dd class="why" style="margin-top: 0">${ico("info")}<span>Ton code échoue sur un cas qu'on ne te montre pas. Pense aux cas limites : liste vide, zéro, un seul élément.</span></dd></dl>`}</li>`;
    }
    const appel = `${ex.fn[lang]}(${r.args.map(lit).join(", ")})`;
    if (r.ok) return `<li class="test"><div class="test__row">${marque}<span class="test__call">${esc(appel)} <span class="arr">→</span> ${esc(gotLit(r.got))}</span></div></li>`;
    const sansRetour = !r.error && (r.got === "undefined" || r.got === "None");
    return `<li class="test test--ko"><div class="test__row">${marque}<span class="test__call">${esc(appel)}</span></div>
      <dl class="test__detail">
        <dt>Attendu</dt><dd class="v-exp">${esc(lit(r.expected))}</dd>
        <dt>Obtenu</dt><dd class="v-got${r.error ? " err" : ""}">${esc(r.error || gotLit(r.got))}</dd>
        ${sansRetour ? `<dd class="why">${ico("bulb")}<span>Ta fonction ne renvoie rien. As-tu écrit <code class="ic">return</code> ?</span></dd>` : ""}
      </dl></li>`;
  };

  const afficherResultats = (rapport) => {
    const total = rapport.results.length;
    const ok = rapport.results.filter((r) => r.ok).length;
    const tout = !rapport.error && total > 0 && ok === total;
    const compte = `${pluriel(ok, "test")} réussi${ok > 1 ? "s" : ""} sur ${total}`;
    const barre = `<div class="segbar" aria-hidden="true" style="grid-template-columns: repeat(${total || 1}, minmax(0, 1fr))">${rapport.results.map((r) => `<i class="${r.ok ? "on" : "ko"}"></i>`).join("")}</div>`;
    const liste = `<ul class="tests">${rapport.results.map(ligneTest).join("")}</ul>`;
    let html = "";

    if (rapport.error) {
      html += `<div class="errbox" role="alert">${esc(rapport.error)}</div>`;
    } else if (tout) {
      const apres = n < 24 && !isLocked(n + 1) ? `<a class="btn btn--amber" href="#/jour/${n + 1}">Jour ${n + 1} : ${esc(storyOf(n + 1).title)}${ico("arrow", { sm: true })}</a>` : "";
      html += `
        <div class="win-card" role="status">
          <div class="miniwin" aria-hidden="true">
            <div class="miniwin__arch">
              <div class="miniwin__pane"></div>
              <div class="miniwin__num">${n}</div>
              <div class="miniwin__leaf"></div>
              <div class="miniwin__cap"></div>
            </div>
            <div class="miniwin__sill"></div>
            <svg class="spark" viewBox="0 0 24 24" fill="currentColor" style="left: -10px; top: -8px; animation-delay: .5s">${SPARK}</svg>
            <svg class="spark" viewBox="0 0 24 24" fill="currentColor" style="right: -12px; top: 10px; width: 10px; height: 10px; animation-delay: .7s">${SPARK}</svg>
            <svg class="spark" viewBox="0 0 24 24" fill="currentColor" style="left: 40%; top: -18px; width: 9px; height: 9px; animation-delay: .9s">${SPARK}</svg>
          </div>
          <div>
            <p class="eyebrow">Porte ${n} ouverte · une fenêtre de plus au village</p>
            <h3>Bravo, la panne est réparée !</h3>
            <p>Givrebug recule d'un pas, et Givreville gagne une lumière.</p>
            <div class="win-card__actions">${apres}<a class="btn btn--secondary" href="#/">Voir le village</a></div>
          </div>
        </div>
        <div class="res-head" style="margin-top: 24px"><h3 style="font-size: 20px">${compte}</h3></div>
        ${barre}${liste}`;
    } else {
      const reste = total - ok;
      html += `
        <div class="res-head"><h3>${ok > 0 ? "Presque !" : "Pas encore…"}</h3><span class="count">${compte}</span></div>
        <p class="res-sub">${ico("frost", { style: "color: var(--givre)" })}Givrebug bloque encore ${pluriel(reste, "test")}.</p>
        ${barre}${liste}`;
    }
    if (rapport.logs) {
      const lignes = rapport.logs.replace(/\n$/, "").split("\n").length;
      html += `<div class="console"><div class="console__head"><span>Console</span><span>${pluriel(lignes, "ligne")}</span></div><pre>${esc(rapport.logs)}</pre></div>`;
    }
    resultats.innerHTML = html;
  };

  async function lancer() {
    if (enCours) return;
    enCours = true;
    $("#btn-run").disabled = true;
    resultats.innerHTML = "";
    statut.textContent = "Exécution…";
    const code = ta.value;
    const rapport = await executer(lang, code, ex, (t) => (statut.textContent = t));
    enCours = false;
    $("#btn-run").disabled = false;
    statut.textContent = "";

    const total = rapport.results.length;
    const tout = !rapport.error && total > 0 && rapport.results.every((r) => r.ok);
    const p = getProg(ex);
    if (tout && !p.solved) justSolved = n;
    setProg(ex, { code, attempts: p.attempts + 1, solved: p.solved || tout });
    afficherResultats(rapport);
    afficherSolution();

    const apres = getProg(ex);
    $("#day-status").textContent = libelleStatut(apres);
    if (apres.solved) {
      $("#day-badge").classList.replace("daybadge--glass", "daybadge--lit");
      const pastille = vue.querySelector(`.chip[data-level="${ex.level}"]`);
      if (pastille && !pastille.querySelector(".ico")) pastille.insertAdjacentHTML("afterbegin", ico("check"));
    }
  }

  $("#btn-run").addEventListener("click", lancer);
  afficherSolution();
  $("#day-title").focus({ preventScroll: true });
}

// ---------------------------------------------------------------- test de niveau

function openPlacement() {
  const dlg = $("#dlg-placement");
  const { questions, intro, bands } = content.placement;
  let reponses = [];
  let i = 0;
  let surTouche = null;

  const haut = (surtitre, libelleFermer, idTitre = "") => `
    <div class="modal__top">
      <p class="eyebrow"${idTitre ? ` id="${idTitre}"` : ""}>${surtitre}</p>
      <button type="button" class="btn btn--ghost btn--icon modal__close" aria-label="${libelleFermer}" data-act="close">${ico("cross")}</button>
    </div>`;
  const brancherFermeture = () => dlg.querySelectorAll('[data-act="close"]').forEach((b) => (b.onclick = () => dlg.close()));

  const intro_ = () => {
    surTouche = null;
    i = 0;
    reponses = [];
    dlg.innerHTML = `
      ${haut("Test de niveau", "Fermer")}
      <h2 id="dlg-title" style="margin-top: 10px">Par où commencer ?</h2>
      <p class="muted" style="margin-top: 12px; font-size: 17px; line-height: 1.6">${esc(intro)}</p>
      <ul class="facts">
        <li>${ico("list", { sm: true })}${questions.length} questions</li>
        <li>${ico("clock", { sm: true })}${Math.max(1, Math.round(questions.length / 3))} minutes environ</li>
        <li>${ico("reset", { sm: true })}Niveau modifiable à tout moment</li>
      </ul>
      <div class="modal__foot">
        <div class="right">
          <button class="btn btn--secondary" type="button" data-act="close">Je choisis moi-même</button>
          <button class="btn btn--primary" type="button" data-act="start">Faire le test</button>
        </div>
      </div>`;
    brancherFermeture();
    dlg.querySelector('[data-act="start"]').onclick = question;
  };

  const question = () => {
    const q = questions[i];
    const dernier = i === questions.length - 1;
    const barre = questions.map((_, k) => `<i class="${k < i ? "done" : k === i ? "now" : ""}"></i>`).join("");
    dlg.innerHTML = `
      ${haut(`Question ${i + 1} sur ${questions.length}`, "Arrêter le test", "dlg-title")}
      <div class="qbar" role="progressbar" aria-valuemin="1" aria-valuemax="${questions.length}" aria-valuenow="${i + 1}" aria-label="Progression du test">${barre}</div>
      <form>
        <div class="prose" id="q-prompt">${md(q.prompt)}</div>
        <fieldset class="opts" aria-labelledby="q-prompt">
          ${q.options
            .map(
              (o, k) => `<label class="opt${reponses[i] === k ? " opt--sel" : ""}${/^je ne sais pas/i.test(o) ? " opt--idk" : ""}">
                <input type="radio" name="opt" value="${k}"${reponses[i] === k ? " checked" : ""}>
                <span>${inline(o)}</span>
                ${k < 9 ? `<span class="kbd opt__key" aria-hidden="true">${k + 1}</span>` : ""}
              </label>`
            )
            .join("")}
        </fieldset>
        <div class="modal__foot">
          <button class="btn btn--ghost" type="button" data-act="prev"${i === 0 ? " disabled" : ""}>${ico("prev", { sm: true })}Précédente</button>
          <div class="right">
            <button class="btn btn--secondary" type="button" data-act="close">Arrêter</button>
            <button class="btn btn--primary" type="submit"${reponses[i] === undefined ? " disabled" : ""}>${dernier ? "Voir mon niveau" : "Suivant"}</button>
          </div>
        </div>
      </form>`;
    const form = dlg.querySelector("form");
    const suivant = form.querySelector('[type="submit"]');
    const marquer = () => {
      form.querySelectorAll(".opt").forEach((l) => l.classList.toggle("opt--sel", l.querySelector("input").checked));
      suivant.disabled = !form.querySelector("input:checked");
    };
    form.addEventListener("change", marquer);
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      reponses[i] = Number(new FormData(form).get("opt"));
      i++;
      i < questions.length ? question() : resultat();
    });
    form.querySelector('[data-act="prev"]').onclick = () => {
      const coche = form.querySelector("input:checked");
      if (coche) reponses[i] = Number(coche.value);
      i--;
      question();
    };
    brancherFermeture();
    // Raccourcis 1 à 4 : seulement dans la modale, et sans gêner les touches de modification.
    surTouche = (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const radio = form.querySelector(`input[value="${Number(e.key) - 1}"]`);
      if (!radio) return;
      radio.checked = true;
      radio.focus();
      marquer();
    };
    (form.querySelector("input:checked") || form.querySelector("input")).focus();
  };

  const resultat = () => {
    surTouche = null;
    const score = questions.filter((q, k) => reponses[k] === q.answer).length;
    // Notation par paliers : on propose le niveau du dernier palier validé, sans en sauter aucun.
    // Un palier est validé s'il est réussi, ou s'il est manqué d'une seule réponse alors que le palier
    // suivant est réussi (« rattrapé ») : les questions du dessus supposent déjà celles du dessous.
    // Au-delà d'une réponse d'écart, rien ne compense : des bases fragiles arrêtent le décompte.
    const paliers = bands.map((b) => {
      const indices = questions.map((q, k) => k).filter((k) => questions[k].band === b.id);
      const bonnes = indices.filter((k) => reponses[k] === questions[k].answer).length;
      return { ...b, bonnes, total: indices.length, reussi: bonnes >= b.minCorrect };
    });
    paliers.forEach((p, k) => {
      p.rattrape = !p.reussi && p.bonnes === p.minCorrect - 1 && !!paliers[k + 1]?.reussi;
    });
    let propose = paliers[0].level;
    let bloque = null; // premier palier non validé : c'est lui qui fixe le niveau proposé
    for (const p of paliers) {
      if (!p.reussi && !p.rattrape) {
        bloque = p;
        break;
      }
      propose = p.level;
    }
    paliers.forEach((p, k) => (p.compte = !bloque || k <= paliers.indexOf(bloque)));
    const info = levelInfo(propose);
    const auDessus = content.meta.levels[content.meta.levels.findIndex((l) => l.id === propose) + 1];
    const verdict = bloque
      ? `Le palier « ${esc(bloque.label)} » te résiste encore (${bloque.bonnes} sur ${bloque.total}, il en faut ${bloque.minCorrect}) : c'est lui qui fixe le niveau proposé.`
      : `Tu as franchi tous les paliers : le test ne mesure pas plus haut.${auDessus ? ` Si le niveau ${esc(info.label)} t'ennuie, essaie ${esc(auDessus.label)}.` : ""}`;
    const erreurs = questions.map((q, k) => ({ q, k })).filter(({ q, k }) => reponses[k] !== q.answer);
    let choisi = propose;
    dlg.innerHTML = `
      ${haut("Résultat", "Fermer")}
      <div class="score" style="margin-top: 12px">
        <div class="score__ring" style="background: conic-gradient(var(--amber) ${Math.round((score / questions.length) * 360)}deg, var(--surface-3) 0); padding: 6px">
          <span style="width: 100%; height: 100%; border-radius: 50%; background: var(--surface); display: grid; place-items: center">${score}/${questions.length}</span>
        </div>
        <div>
          <h2 id="dlg-title" tabindex="-1">On te propose : ${esc(info.label)}</h2>
          <p class="muted" style="margin-top: 6px">${pluriel(score, "bonne")} ${score > 1 ? "réponses" : "réponse"} sur ${questions.length}. Ce n'est qu'une suggestion.</p>
        </div>
      </div>
      <ul class="paliers" aria-label="Résultat par palier">
        ${paliers
          .map(
            (p) => `<li class="palier${(p.reussi || p.rattrape) && p.compte ? "" : " palier--non"}">
              <span class="test__ic ${p.reussi || p.rattrape ? "ic-ok" : "ic-ko"}">${ico(p.reussi || p.rattrape ? "check" : "cross", { label: p.reussi ? "palier réussi" : p.rattrape ? "palier rattrapé" : "palier manqué" })}</span>
              <span class="palier__nom">${esc(p.label)}${p.rattrape ? "<small>Manqué d'une réponse, rattrapé par le palier suivant.</small>" : p.reussi && !p.compte ? "<small>Réussi, mais un palier précédent manque.</small>" : ""}</span>
              <span class="palier__score">${p.bonnes} / ${p.total}</span>
            </li>`
          )
          .join("")}
      </ul>
      <p class="verdict">${verdict}</p>
      <p class="label-sm" style="margin-top: 26px">Tu peux changer</p>
      <div class="lvls" role="group" aria-label="Niveau choisi">
        ${content.meta.levels.map((l) => `<button type="button" class="lvl" data-level="${esc(l.id)}" aria-pressed="${l.id === choisi}">${esc(l.label)}<small>${esc(l.help)}</small></button>`).join("")}
      </div>
      ${
        erreurs.length
          ? `<details class="hint"><summary>${ico("bulb")}À retenir<small>${pluriel(erreurs.length, "question")}</small></summary>
              <ul class="review">${erreurs.map(({ q, k }) => `<li><strong>Question ${k + 1}.</strong> ${inline(q.explain)}</li>`).join("")}</ul></details>`
          : '<p class="muted" style="margin-top: 20px">Sans faute, bravo !</p>'
      }
      <div class="modal__foot">
        <button class="btn btn--ghost" type="button" data-act="again">Refaire le test</button>
        <div class="right"><button class="btn btn--primary" type="button" data-act="apply">C'est parti en ${esc(info.label)}</button></div>
      </div>`;
    const appliquer = dlg.querySelector('[data-act="apply"]');
    dlg.querySelector(".lvls").addEventListener("click", (e) => {
      const bouton = e.target.closest(".lvl");
      if (!bouton) return;
      choisi = bouton.dataset.level;
      dlg.querySelectorAll(".lvl").forEach((b) => b.setAttribute("aria-pressed", String(b === bouton)));
      appliquer.textContent = `C'est parti en ${levelInfo(choisi).label}`;
    });
    dlg.querySelector('[data-act="again"]').onclick = intro_;
    appliquer.onclick = () => {
      state.level = choisi;
      saveState();
      syncChrome();
      dlg.close();
    };
    brancherFermeture();
    dlg.querySelector("#dlg-title").focus();
  };

  const ecoute = (e) => surTouche && surTouche(e);
  dlg.addEventListener("keydown", ecoute);
  dlg.addEventListener(
    "close",
    () => {
      dlg.removeEventListener("keydown", ecoute);
      state.placementSeen = true;
      saveState();
      route();
    },
    { once: true }
  );
  intro_();
  dlg.showModal();
}

// ---------------------------------------------------------------- démarrage

async function init() {
  try {
    const reponse = await fetch("data/content.json");
    if (!reponse.ok) throw new Error(`HTTP ${reponse.status}`);
    content = await reponse.json();
  } catch {
    $("#main").innerHTML = `<div class="wrap" style="padding-top: 48px"><div class="empty"><h3>Le contenu est introuvable</h3><p>Lance <code class="ic">npm run dev</code> depuis la racine du projet, puis ouvre <code class="ic">http://localhost:5173</code>.</p></div></div>`;
    return;
  }
  if (!content.meta.languages.some((l) => l.id === state.lang)) state.lang = content.meta.languages[0].id;
  if (!content.meta.levels.some((l) => l.id === state.level)) state.level = content.meta.levels[0].id;

  applyTheme();
  buildChrome();
  window.addEventListener("hashchange", route);
  window.addEventListener("pagehide", () => flushPending && flushPending());
  route();
}

init();
