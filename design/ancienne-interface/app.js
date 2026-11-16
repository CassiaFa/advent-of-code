// Calendrier de l'Avent du Code : webapp statique, sans dépendance.
// Le contenu vient de data/content.json (généré par `npm run build`).
// Le code des joueurs ne s'exécute que dans judge.worker.js.

const KEY = "advent-code-v1";
const WORKER_URL = "judge.worker.js";
const ATTEMPTS_FOR_SOLUTION = 2;
const TIMEOUT_MS = { javascript: 3000, python: 5000 };
const INDENT = { javascript: "  ", python: "    " };
const DEFAULT_STATE = { lang: "javascript", level: "debutant", realDates: false, placementSeen: false, progress: {} };
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
    .map((seg, i) => (i % 2 ? `<code>${esc(seg)}</code>` : esc(seg).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")))
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
    if (codes.length) sortie.push('<pre class="codeblock"><code>' + codes.map(esc).join("\n") + "</code></pre>");
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

// ---------------------------------------------------------------- en-tête et routage

const segment = (nom, items) =>
  items.map((it) => `<label><input type="radio" name="${nom}" value="${esc(it.id)}"><span>${esc(it.label)}</span></label>`).join("");

function buildChrome() {
  $("#tagline").textContent = content.meta.tagline;
  $("#seg-lang").insertAdjacentHTML("beforeend", segment("lang", content.meta.languages));
  $("#seg-level").insertAdjacentHTML("beforeend", segment("level", content.meta.levels));
  syncChrome();

  $("#seg-lang").addEventListener("change", (e) => {
    state.lang = e.target.value;
    saveState();
    route();
  });
  $("#seg-level").addEventListener("change", (e) => {
    state.level = e.target.value;
    saveState();
    route();
  });
  $("#chk-dates").addEventListener("change", (e) => {
    state.realDates = e.target.checked;
    saveState();
    route();
  });

  const menu = $("#menu");
  const fermerMenu = () => menu.removeAttribute("open");
  document.addEventListener("click", (e) => {
    if (menu.open && !menu.contains(e.target)) fermerMenu();
  });
  menu.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu.open) {
      fermerMenu();
      $("summary", menu).focus();
    }
  });

  $("#btn-placement").addEventListener("click", () => {
    fermerMenu();
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
}

function syncChrome() {
  for (const [nom, valeur] of [["lang", state.lang], ["level", state.level]]) {
    const radio = document.querySelector(`input[name="${nom}"][value="${valeur}"]`);
    if (radio) radio.checked = true;
  }
  $("#chk-dates").checked = state.realDates;
}

function route() {
  if (flushPending) flushPending();
  flushPending = null;
  const m = location.hash.match(/^#\/jour\/(\d+)$/);
  const jour = m ? Number(m[1]) : null;
  if (jour && jour >= 1 && jour <= 24) showDay(jour);
  else showCalendar();
}

// ---------------------------------------------------------------- calendrier

const conceptOf = (day) => content.days?.find((d) => d.day === day)?.concept || findEx(day)?.concept || "";
const solvedAt = (day, niveau) => {
  const ex = findEx(day, niveau);
  return !!ex && !!state.progress[progKey(ex)]?.solved;
};

// Une pastille par niveau : pleine si l'exercice de ce niveau est réparé dans le langage courant.
const levelDots = (day) =>
  content.meta.levels
    .map((l) => `<i class="dot${solvedAt(day, l.id) ? " on" : ""}${l.id === state.level ? " cur" : ""}"></i>`)
    .join("");

function showCalendar() {
  $("#view-day").hidden = true;
  $("#view-calendar").hidden = false;
  document.title = content.meta.title;

  const grille = $("#grid");
  let disponibles = 0;
  let reussis = 0;
  let suivant = null;
  const cartes = [];

  for (let n = 1; n <= 24; n++) {
    const histoire = storyOf(n);
    const ex = findEx(n);
    const verrou = isLocked(n);
    const prog = ex ? getProg(ex) : null;
    const resolu = !!prog?.solved;
    const commence = !!prog && !resolu && (prog.attempts > 0 || prog.code !== undefined);
    if (ex) disponibles++;
    if (resolu) reussis++;
    if (ex && !resolu && !verrou && suivant === null) suivant = n;

    const etat = verrou ? "locked" : !ex ? "soon" : resolu ? "solved" : commence ? "started" : "closed";
    const libelle = { locked: `ouvre le ${n} décembre`, soon: "histoire seulement", solved: "réparé", started: "en cours", closed: "à ouvrir" }[etat];
    const badge = { locked: `dès le ${n} déc.`, soon: "histoire", solved: "réparé", started: "en cours", closed: "" }[etat];
    const interieur = `
        <span class="door-wrap"><span class="door-num">${n}</span>${badge ? `<span class="door-badge">${etat === "solved" ? "✓ " : ""}${badge}</span>` : ""}</span>
        <span class="door-info">
          <span class="door-title">${esc(histoire.title)}</span>
          <span class="door-foot"><span class="door-concept">${esc(conceptOf(n))}</span><span class="dots" aria-hidden="true">${levelDots(n)}</span></span>
        </span>`;
    const classe = `door${justSolved === n ? " lighting" : ""}${suivant === n ? " next" : ""}`;
    const aria = `Jour ${n}, ${histoire.title}, ${libelle}`;
    cartes.push(
      verrou
        ? `<li><span class="${classe}" data-day="${n}" data-state="${etat}" data-tone="${n % 4}" aria-disabled="true" aria-label="${esc(aria)}" role="img">${interieur}</span></li>`
        : `<li><a class="${classe}" href="#/jour/${n}" data-day="${n}" data-state="${etat}" data-tone="${n % 4}" aria-label="${esc(aria)}">${interieur}</a></li>`
    );
  }
  grille.innerHTML = cartes.join("");
  justSolved = null;

  // Jauge : les fenêtres rallumées, pour le niveau et le langage courants.
  const part = disponibles ? reussis / disponibles : 0;
  const rayon = 52;
  const tour = 2 * Math.PI * rayon;
  $("#gauge").innerHTML = `
    <svg viewBox="0 0 120 120" aria-hidden="true">
      <circle class="gauge-track" cx="60" cy="60" r="${rayon}"></circle>
      <circle class="gauge-fill" cx="60" cy="60" r="${rayon}" stroke-dasharray="${tour}" stroke-dashoffset="${tour * (1 - part)}"></circle>
    </svg>
    <p class="gauge-num"><strong>${reussis}</strong><span>sur ${disponibles}</span></p>
    <p class="gauge-label">panne${reussis > 1 ? "s" : ""} réparée${reussis > 1 ? "s" : ""}<br><small>${esc(levelInfo().label)} · ${esc(langInfo().label)}</small></p>`;

  const reprise = $("#resume");
  if (suivant !== null) {
    const verbe = reussis === 0 && !Object.keys(state.progress).length ? "Commencer" : "Reprendre";
    reprise.innerHTML = `<a class="primary big" href="#/jour/${suivant}">${verbe} : jour ${suivant}, ${esc(storyOf(suivant).title)} <span aria-hidden="true">→</span></a>`;
  } else if (disponibles && reussis === disponibles) {
    reprise.innerHTML = `<p class="alldone">✦ Tout est réparé à ce niveau. Givreville te dit merci ! Envie d'essayer un autre niveau ou l'autre langage ?</p>`;
  } else {
    reprise.innerHTML = `<p class="alldone">La prochaine porte n'est pas encore ouverte. Reviens demain, ou décoche « Une porte par jour » dans les réglages.</p>`;
  }

  // Première visite : on propose le test de niveau sans l'imposer.
  const accueil = $("#welcome");
  if (!state.placementSeen) {
    accueil.innerHTML = `
      <div class="welcome">
        <div>
          <h2>Première visite ?</h2>
          <p>Choisis ton langage et ton niveau en haut de la page. Si tu hésites, huit questions suffisent pour te proposer un niveau. Tu pourras en changer à tout moment.</p>
        </div>
        <div class="welcome-actions">
          <button class="primary" type="button" id="btn-welcome-test">Faire le test de niveau</button>
          <button class="ghost" type="button" id="btn-welcome-skip">Je choisis moi-même</button>
        </div>
      </div>`;
    $("#btn-welcome-test").addEventListener("click", () => openPlacement());
    $("#btn-welcome-skip").addEventListener("click", () => {
      state.placementSeen = true;
      saveState();
      accueil.innerHTML = "";
    });
  } else {
    accueil.innerHTML = "";
  }

  if (lastDayVisited) {
    $(`.door[data-day="${lastDayVisited}"]`)?.focus({ preventScroll: false });
    lastDayVisited = null;
  }
}

// ---------------------------------------------------------------- une journée

function showDay(n) {
  $("#view-calendar").hidden = true;
  const vue = $("#view-day");
  vue.hidden = false;
  lastDayVisited = n;

  const histoire = storyOf(n);
  document.title = `Jour ${n} : ${histoire.title} — ${content.meta.title}`;
  const nav = `
    <nav class="daynav" aria-label="Navigation entre les jours">
      <a class="back" href="#/"><span aria-hidden="true">←</span> Le calendrier</a>
      <span class="pair">
        ${n > 1 ? `<a href="#/jour/${n - 1}" aria-label="Jour précédent, jour ${n - 1}"><span aria-hidden="true">←</span> Jour ${n - 1}</a>` : ""}
        ${n < 24 ? `<a href="#/jour/${n + 1}" aria-label="Jour suivant, jour ${n + 1}">Jour ${n + 1} <span aria-hidden="true">→</span></a>` : ""}
      </span>
    </nav>`;
  const titre = `<header class="dayhead"><span class="daynum" aria-hidden="true">${n}</span><div><p class="eyebrow">Jour ${n} sur 24</p><h1 id="day-title" tabindex="-1"><span class="sr-only">Jour ${n} : </span>${esc(histoire.title)}</h1></div></header>`;

  if (isLocked(n)) {
    vue.innerHTML = `${nav}<article class="prose">${titre}<div class="empty"><p>Cette porte s'ouvre le ${n} décembre.</p><p>Tu veux jouer dès maintenant ? Décoche « Une porte par jour » dans les réglages, en haut de la page.</p></div></article>`;
    $("#day-title").focus();
    return;
  }

  const ex = findEx(n);
  const histoireHtml = `<p class="story">${esc(histoire.text)}</p>`;

  if (!ex) {
    const autre = content.meta.levels.find((l) => l.id !== state.level && findEx(n, l.id));
    vue.innerHTML = `${nav}<article class="prose">${titre}${histoireHtml}
      <div class="empty">
        <p>L'exercice de ce jour n'est pas encore écrit pour le niveau ${esc(levelInfo().label)}.</p>
        ${autre ? `<p><button class="ghost" type="button" id="btn-other-level">Passer au niveau ${esc(autre.label)}</button></p>` : "<p>Reviens bientôt : cette porte est encore en travaux.</p>"}
      </div></article>`;
    $("#btn-other-level")?.addEventListener("click", () => {
      state.level = autre.id;
      saveState();
      syncChrome();
      route();
    });
    $("#day-title").focus();
    return;
  }

  const lang = state.lang;
  const prog = getProg(ex);
  const fichier = `jour-${String(n).padStart(2, "0")}.${langInfo().ext}`;
  const exemples = ex.tests
    .filter((t) => !t.hidden)
    .slice(0, 3)
    .map((t) => `${ex.fn[lang]}(${t.args.map(lit).join(", ")})  →  ${lit(t.expected)}`)
    .join("\n");
  const niveaux = content.meta.levels
    .filter((l) => findEx(n, l.id))
    .map((l) => {
      const fait = solvedAt(n, l.id);
      return `<button type="button" class="pill${l.id === state.level ? " on" : ""}${fait ? " done" : ""}" data-level="${esc(l.id)}" aria-pressed="${l.id === state.level}">${fait ? '<span aria-hidden="true">✓ </span>' : ""}${esc(l.label)}${fait ? '<span class="sr-only"> (réparé)</span>' : ""}</button>`;
    })
    .join("");

  vue.innerHTML = `${nav}
    <div class="day">
      <article class="prose">
        ${titre}
        ${histoireHtml}
        <section class="card exo" aria-labelledby="exo-title">
          <div class="pills" role="group" aria-label="Niveau de l'exercice">${niveaux}</div>
          <h2 id="exo-title">${esc(ex.title)}</h2>
          <p class="concept"><span class="chip">Notion</span> ${esc(ex.concept)}</p>
          ${md(statementOf(ex))}
          <h3 class="minor">Exemples</h3>
          <pre class="examples">${esc(exemples)}</pre>
          <details class="hint"><summary>Un indice</summary><p>${inline(ex.hint)}</p></details>
        </section>
      </article>

      <section class="work" aria-label="Ton espace de code">
        <div class="panel">
          <div class="bar">
            <span class="lights" aria-hidden="true"><i></i><i></i><i></i></span>
            <span class="file">${esc(fichier)}</span>
            <span class="spacer"></span>
            <button class="ghost small" type="button" id="btn-reset">Repartir de zéro</button>
            <button class="primary" type="button" id="btn-run"><span aria-hidden="true">▶</span> Lancer les tests</button>
          </div>
          <div class="editor">
            <pre class="gutter" id="gutter" aria-hidden="true"></pre>
            <textarea id="code" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off"
                      aria-label="Ton code en ${esc(langInfo().label)}"></textarea>
          </div>
          <p class="keys"><kbd>Ctrl</kbd> + <kbd>Entrée</kbd> lance les tests. Pour quitter l'éditeur au clavier : <kbd>Échap</kbd>, puis <kbd>Tab</kbd>.</p>
        </div>
        <p class="status" id="status" role="status"></p>
        <div class="results" id="results" aria-live="polite"></div>
        <div class="solution" id="solution"></div>
      </section>
    </div>`;

  vue.querySelector(".pills").addEventListener("click", (e) => {
    const pastille = e.target.closest(".pill");
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

  const majGouttiere = () => {
    const lignes = ta.value.split("\n").length;
    gouttiere.textContent = Array.from({ length: lignes }, (_, i) => i + 1).join("\n");
    gouttiere.scrollTop = ta.scrollTop;
  };
  const sauver = () => {
    clearTimeout(minuteurSauvegarde);
    if (ta.value !== (getProg(ex).code ?? ex.starter[lang])) setProg(ex, { code: ta.value });
  };
  flushPending = sauver;
  majGouttiere();

  ta.addEventListener("input", () => {
    majGouttiere();
    clearTimeout(minuteurSauvegarde);
    minuteurSauvegarde = setTimeout(sauver, 400);
  });
  ta.addEventListener("scroll", () => (gouttiere.scrollTop = ta.scrollTop));

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
    resultats.innerHTML = "";
    ta.focus();
  });

  const afficherSolution = () => {
    const p = getProg(ex);
    const debloquee = p.solved || p.attempts >= ATTEMPTS_FOR_SOLUTION;
    const zone = $("#solution");
    if (!debloquee) {
      const reste = ATTEMPTS_FOR_SOLUTION - p.attempts;
      zone.innerHTML = `<p>La solution se débloque après ${ATTEMPTS_FOR_SOLUTION} essais, ou dès que tes tests passent (encore ${reste} essai${reste > 1 ? "s" : ""}).</p><button class="ghost" type="button" disabled>Voir la solution</button>`;
      return;
    }
    zone.innerHTML = solutionVisible
      ? `<button class="ghost" type="button" id="btn-solution">Masquer la solution</button>
         <pre><code>${esc(ex.solution[lang])}</code></pre>
         <p class="why">Il y a rarement une seule bonne façon de faire. Compare avec la tienne : qu'est-ce qui change ?</p>`
      : `<button class="ghost" type="button" id="btn-solution">Voir la solution</button>`;
    $("#btn-solution").addEventListener("click", () => {
      solutionVisible = !solutionVisible;
      afficherSolution();
      $("#btn-solution").focus();
    });
  };

  const afficherResultats = (rapport) => {
    const total = rapport.results.length;
    const ok = rapport.results.filter((r) => r.ok).length;
    const tout = !rapport.error && total > 0 && ok === total;
    let html = "";

    if (rapport.error) {
      html += `<div class="errbox" role="alert">${esc(rapport.error)}</div>`;
    } else {
      html += `<h3 class="verdict ${tout ? "ok" : "ko"}">${tout ? "✦ Bravo, la panne est réparée !" : "Pas encore…"} <span>${ok} test${ok > 1 ? "s" : ""} réussi${ok > 1 ? "s" : ""} sur ${total}</span></h3>
        <div class="meter" aria-hidden="true"><span style="width:${total ? Math.round((ok / total) * 100) : 0}%"></span></div>
        <ul class="tests">${rapport.results.map(ligneTest).join("")}</ul>`;
    }
    if (rapport.logs) html += `<details class="logs"><summary>Ce que ton programme a affiché</summary><pre>${esc(rapport.logs)}</pre></details>`;
    if (tout) {
      html += `<div class="after">${n < 24 ? `<a class="primary" href="#/jour/${n + 1}">Porte suivante</a>` : ""}<a class="ghost" href="#/">Revenir au calendrier</a></div>`;
    }
    resultats.innerHTML = html;
  };

  const ligneTest = (r) => {
    const marque = r.ok ? '<span class="mark" aria-hidden="true">✓</span><span class="sr-only">Réussi : </span>' : '<span class="mark" aria-hidden="true">✗</span><span class="sr-only">Échec : </span>';
    if (r.hidden) {
      return `<li class="${r.ok ? "ok" : "ko"}">${marque}Test caché${r.ok ? "" : '<p class="hintline">Ton code échoue sur un cas qu\'on ne te montre pas. Pense aux cas limites : liste vide, zéro, un seul élément.</p>'}</li>`;
    }
    const appel = `${ex.fn[lang]}(${r.args.map(lit).join(", ")})`;
    if (r.ok) return `<li class="ok">${marque}${esc(appel)}  →  ${esc(gotLit(r.got))}</li>`;
    const sansRetour = !r.error && (r.got === "undefined" || r.got === "None");
    return `<li class="ko">${marque}${esc(appel)}
      <dl><dt>attendu</dt><dd>${esc(lit(r.expected))}</dd><dt>obtenu</dt><dd class="${r.error ? "err" : ""}">${esc(r.error || gotLit(r.got))}</dd></dl>
      ${sansRetour ? '<p class="hintline">Ta fonction ne renvoie rien. As-tu écrit <code>return</code> ?</p>' : ""}</li>`;
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
    if (tout) vue.querySelector(`.pill[data-level="${ex.level}"]`)?.classList.add("done");
  }

  $("#btn-run").addEventListener("click", lancer);
  afficherSolution();
  $("#day-title").focus({ preventScroll: true });
}

// ---------------------------------------------------------------- test de niveau

function openPlacement() {
  const dlg = $("#dlg-placement");
  const { questions, intro, thresholds } = content.placement;
  const reponses = [];
  let i = 0;

  const intro_ = () => {
    dlg.innerHTML = `
      <h2 id="dlg-title">Par où commencer ?</h2>
      <p>${esc(intro)}</p>
      <div class="actions">
        <button class="ghost" type="button" data-act="close">Je choisis moi-même</button>
        <button class="primary" type="button" data-act="start">Faire le test</button>
      </div>`;
    dlg.querySelector('[data-act="close"]').onclick = () => dlg.close();
    dlg.querySelector('[data-act="start"]').onclick = question;
  };

  const question = () => {
    const q = questions[i];
    const dernier = i === questions.length - 1;
    dlg.innerHTML = `
      <p class="q-progress">Question ${i + 1} sur ${questions.length}</p>
      <h2 id="dlg-title" class="sr-only">Test de niveau, question ${i + 1}</h2>
      <div class="q-prompt">${md(q.prompt)}</div>
      <form>
        <fieldset>
          <legend>Choisis une réponse</legend>
          ${q.options.map((o, k) => `<label class="opt"><input type="radio" name="opt" value="${k}"><span>${esc(o)}</span></label>`).join("")}
        </fieldset>
        <div class="actions">
          <button class="ghost" type="button" data-act="close">Arrêter</button>
          <button class="primary" type="submit" disabled>${dernier ? "Voir mon niveau" : "Suivant"}</button>
        </div>
      </form>`;
    const form = dlg.querySelector("form");
    const suivant = form.querySelector('[type="submit"]');
    form.addEventListener("change", () => (suivant.disabled = false));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      reponses[i] = Number(new FormData(form).get("opt"));
      i++;
      i < questions.length ? question() : resultat();
    });
    form.querySelector('[data-act="close"]').onclick = () => dlg.close();
  };

  const resultat = () => {
    const score = questions.filter((q, k) => reponses[k] === q.answer).length;
    const propose = [...thresholds].sort((a, b) => b.minScore - a.minScore).find((t) => score >= t.minScore).level;
    const info = levelInfo(propose);
    const erreurs = questions.map((q, k) => ({ q, k })).filter(({ q, k }) => reponses[k] !== q.answer);
    dlg.innerHTML = `
      <h2 id="dlg-title">On te propose : ${esc(info.label)}</h2>
      <p class="score">${score} bonne${score > 1 ? "s" : ""} réponse${score > 1 ? "s" : ""} sur ${questions.length}. ${esc(info.help)}</p>
      <p>Ce n'est qu'une suggestion : tu peux changer de niveau à tout moment avec le menu en haut de la page.</p>
      ${erreurs.length ? `<h3>À retenir</h3><ul class="review">${erreurs.map(({ q, k }) => `<li><strong>Question ${k + 1}.</strong> ${inline(q.explain)}</li>`).join("")}</ul>` : "<p>Sans faute, bravo !</p>"}
      <div class="actions">
        <button class="ghost" type="button" data-act="keep">Garder ${esc(levelInfo().label)}</button>
        <button class="primary" type="button" data-act="apply">Jouer en ${esc(info.label)}</button>
      </div>`;
    dlg.querySelector('[data-act="keep"]').onclick = () => dlg.close();
    dlg.querySelector('[data-act="apply"]').onclick = () => {
      state.level = propose;
      saveState();
      syncChrome();
      dlg.close();
    };
  };

  dlg.addEventListener(
    "close",
    () => {
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
    $("#main").innerHTML = `<div class="empty"><p>Le contenu est introuvable.</p><p>Lance <code>npm run dev</code> depuis la racine du projet, puis ouvre <code>http://localhost:5173</code>.</p></div>`;
    return;
  }
  if (!content.meta.languages.some((l) => l.id === state.lang)) state.lang = content.meta.languages[0].id;
  if (!content.meta.levels.some((l) => l.id === state.level)) state.level = content.meta.levels[0].id;

  buildChrome();
  window.addEventListener("hashchange", route);
  window.addEventListener("pagehide", () => flushPending && flushPending());
  route();
}

init();
