// Valide le contenu : schéma, puis exécution réelle des starters et des solutions.
import { chargerContenu } from "./lib.mjs";
import { juger, resume } from "../runner/runner.mjs";

const contenu = chargerContenu();
const { meta, story, placement } = contenu;
// `npm run validate -- 13 14` ne contrôle que les exercices des jours 13 et 14.
const filtre = process.argv.slice(2).map(Number).filter((n) => Number.isInteger(n) && n > 0);
const jours = filtre.length ? contenu.jours.filter((j) => filtre.includes(j.day)) : contenu.jours;
const exercices = jours.flatMap((j) => j.exercises);
const langages = meta.languages.map((l) => l.id);
const niveaux = meta.levels.map((l) => l.id);

let erreurs = 0;
let avertissements = 0;
const echec = (id, msg) => {
  erreurs++;
  console.log(`  ✗ ${id} : ${msg}`);
};
const alerte = (id, msg) => {
  avertissements++;
  console.log(`  ! ${id} : ${msg}`);
};

function jsonPur(valeur) {
  if (valeur === null) return true;
  const t = typeof valeur;
  if (t === "string" || t === "boolean") return true;
  if (t === "number") return Number.isFinite(valeur);
  if (Array.isArray(valeur)) return valeur.every(jsonPur);
  if (t === "object") return Object.values(valeur).every(jsonPur);
  return false;
}

console.log("Histoire");
if (story.length !== 24) echec("story.json", `24 entrées attendues, ${story.length} trouvées`);
story.forEach((s, i) => {
  if (s.day !== i + 1) echec("story.json", `entrée ${i + 1} : champ day = ${s.day}`);
  if (!s.title || !s.text) echec("story.json", `jour ${i + 1} : titre ou texte manquant`);
  if (s.text && s.text.length > 400) alerte("story.json", `jour ${s.day} : ${s.text.length} caractères (400 conseillés)`);
});

console.log("Test de niveau");
// Le test est noté par paliers (`bands`) : chaque palier réussi, dans l'ordre, propose son niveau.
const paliers = placement.bands || [];
if (!paliers.length) echec("placement.json", "aucun palier (`bands`)");
const idsQuestions = new Set();
placement.questions.forEach((q) => {
  if (idsQuestions.has(q.id)) echec(q.id, "identifiant de question en double");
  idsQuestions.add(q.id);
  if (!q.prompt) echec(q.id, "question sans texte");
  if (!Array.isArray(q.options) || q.options.length < 3) echec(q.id, "au moins 3 réponses attendues");
  else if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer >= q.options.length) echec(q.id, "indice de bonne réponse invalide");
  else if (/^je ne sais pas/i.test(q.options[q.answer])) echec(q.id, "la bonne réponse ne peut pas être « Je ne sais pas »");
  if (!q.explain) echec(q.id, "explication manquante");
  if (!paliers.some((p) => p.id === q.band)) echec(q.id, `palier inconnu : ${q.band}`);
});
let rangPrecedent = -1;
paliers.forEach((p) => {
  const nb = placement.questions.filter((q) => q.band === p.id).length;
  if (!p.label) echec("placement.json", `palier ${p.id} : libellé manquant`);
  if (!niveaux.includes(p.level)) echec("placement.json", `palier ${p.id} : niveau inconnu : ${p.level}`);
  if (niveaux.indexOf(p.level) <= rangPrecedent) echec("placement.json", `palier ${p.id} : les niveaux doivent être strictement croissants`);
  rangPrecedent = niveaux.indexOf(p.level);
  if (!Number.isInteger(p.minCorrect) || p.minCorrect < 1 || p.minCorrect > nb) echec("placement.json", `palier ${p.id} : minCorrect (${p.minCorrect}) incompatible avec ses ${nb} question(s)`);
});
if (paliers.length && paliers[0].level !== niveaux[0]) echec("placement.json", `le premier palier doit proposer le niveau « ${niveaux[0]} »`);

console.log("Exercices");
const ids = new Set();
for (const jour of jours) {
  const numero = Number(jour.fichier.match(/\d+/)[0]);
  if (jour.day !== numero) echec(jour.fichier, `champ day (${jour.day}) différent du nom de fichier`);
  if (numero < 1 || numero > 24) echec(jour.fichier, "jour hors de 1..24");
}

for (const ex of exercices) {
  const nb = erreurs;
  if (ids.has(ex.id)) echec(ex.id, "identifiant en double");
  ids.add(ex.id);
  if (!niveaux.includes(ex.level)) echec(ex.id, `niveau inconnu : ${ex.level}`);
  if (ex.id !== `d${String(ex.day).padStart(2, "0")}-${ex.level}`) echec(ex.id, "identifiant attendu : dNN-niveau");
  for (const champ of ["title", "concept", "statement", "hint"]) {
    if (!ex[champ] || typeof ex[champ] !== "string") echec(ex.id, `champ « ${champ} » manquant`);
  }
  if (typeof ex.statement === "string") {
    const noms = new Set(langages.map((l) => ex.fn?.[l]).filter(Boolean));
    for (const nom of noms) {
      // Un nom propre à un seul langage (ex. estPalindrome) ne doit jamais apparaître en dur.
      const concerne = langages.some((l) => ex.fn[l] !== nom);
      if (concerne && ex.statement.includes(nom)) echec(ex.id, `l'énoncé cite « ${nom} » en dur : utilise {fn}`);
    }
  }
  if (!Array.isArray(ex.tests) || ex.tests.length < 4) echec(ex.id, "au moins 4 tests attendus (3 visibles + 1 caché)");
  else {
    if (ex.tests.filter((t) => !t.hidden).length < 3) echec(ex.id, "au moins 3 tests visibles");
    if (!ex.tests.some((t) => t.hidden)) echec(ex.id, "au moins 1 test caché");
    ex.tests.forEach((t, i) => {
      if (!Array.isArray(t.args) || !("expected" in t)) echec(ex.id, `test ${i + 1} : args/expected manquants`);
      else if (!jsonPur(t.args) || !jsonPur(t.expected)) echec(ex.id, `test ${i + 1} : valeurs non JSON`);
    });
  }
  for (const lang of langages) {
    if (!ex.fn?.[lang]) echec(ex.id, `fn.${lang} manquant`);
    if (!ex.starter?.[lang]) echec(ex.id, `starter.${lang} manquant`);
    if (!ex.solution?.[lang]) echec(ex.id, `solution.${lang} manquante`);
    if (ex.starter?.[lang] && ex.fn?.[lang] && !ex.starter[lang].includes(ex.fn[lang])) {
      echec(ex.id, `starter.${lang} ne contient pas la fonction ${ex.fn[lang]}`);
    }
  }
  if (erreurs > nb) continue; // inutile d'exécuter un exercice mal formé

  for (const lang of langages) {
    const sol = juger(lang, ex.solution[lang], ex);
    const rs = resume(sol);
    if (sol.missing) {
      alerte(ex.id, `${lang} : ${sol.error} (exécution ignorée)`);
      continue;
    }
    if (!rs.tout) {
      const detail = sol.error || sol.results.filter((r) => !r.ok).map((r) => `args=${JSON.stringify(r.args ?? "caché")} attendu=${JSON.stringify(r.expected ?? "caché")} obtenu=${r.got}${r.error ? " (" + r.error + ")" : ""}`).join(" | ");
      echec(ex.id, `solution ${lang} : ${rs.reussis}/${rs.total} → ${detail}`);
    }
    const dep = juger(lang, ex.starter[lang], ex);
    const rd = resume(dep);
    if (rd.tout) echec(ex.id, `starter ${lang} passe déjà tous les tests`);
    if (dep.timeout) echec(ex.id, `starter ${lang} : temps dépassé`);
  }
  if (erreurs === nb) console.log(`  ✓ ${ex.id}  ${ex.title}  (${langages.join(" + ")}, ${ex.tests.length} tests)`);
}

// Un jour jouable doit exister pour chaque niveau.
for (const jour of jours) {
  for (const niveau of niveaux) {
    if (!jour.exercises.some((e) => e.level === niveau)) alerte(jour.fichier, `pas d'exercice pour le niveau ${niveau}`);
  }
}

console.log(`\n${exercices.length} exercices, ${erreurs} erreur(s), ${avertissements} avertissement(s).`);
process.exit(erreurs ? 1 : 0);
