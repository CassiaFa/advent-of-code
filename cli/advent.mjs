#!/usr/bin/env node
// Mode terminal du Calendrier de l'Avent du Code (prototype, sans dépendance).
// Même contenu et même juge que la webapp.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { chargerContenu, trouverExercice } from "../scripts/lib.mjs";
import { juger, resume } from "../runner/runner.mjs";

const couleur = !process.env.NO_COLOR && process.stdout.isTTY;
const c = (code, t) => (couleur ? `\x1b[${code}m${t}\x1b[0m` : t);
const vert = (t) => c("32", t);
const rouge = (t) => c("31", t);
const or = (t) => c("33", t);
const gris = (t) => c("2", t);
const gras = (t) => c("1", t);

// --- arguments --------------------------------------------------------------
const [, , commande, ...reste] = process.argv;
const positionnels = [];
const options = {};
for (let i = 0; i < reste.length; i++) {
  const a = reste[i];
  if (a.startsWith("--")) {
    const cle = a.slice(2);
    const suivant = reste[i + 1];
    if (suivant && !suivant.startsWith("--")) {
      options[cle] = suivant;
      i++;
    } else options[cle] = true;
  } else positionnels.push(a);
}

const contenu = chargerContenu();
const langages = contenu.meta.languages;
const niveaux = contenu.meta.levels;
const lang = options.lang || process.env.ADVENT_LANG || "javascript";
const niveau = options.level || process.env.ADVENT_LEVEL || "debutant";
const dossierTravail = resolve(options.dir || "advent-work");

function fin(message, code = 1) {
  console.error(message);
  process.exit(code);
}

function verifierChoix() {
  const l = langages.find((x) => x.id === lang);
  if (!l) fin(`Langage inconnu : « ${lang} ». Choix : ${langages.map((x) => x.id).join(", ")}.`);
  if (!niveaux.some((x) => x.id === niveau)) fin(`Niveau inconnu : « ${niveau} ». Choix : ${niveaux.map((x) => x.id).join(", ")}.`);
  return l;
}

function jourDemande() {
  const n = Number(positionnels[0]);
  if (!Number.isInteger(n) || n < 1 || n > 24) fin("Indique un jour entre 1 et 24, par exemple : advent show 3");
  return n;
}

function exerciceDuJour(n) {
  const ex = trouverExercice(contenu, n, niveau);
  if (!ex) {
    const histoire = contenu.story.find((s) => s.day === n);
    fin(`Pas encore d'exercice pour le jour ${n} (${niveau}).${histoire ? " Lis l'histoire avec : advent show " + n : ""}`);
  }
  return ex;
}

function fichierDuJour(n, ext) {
  return join(dossierTravail, `jour-${String(n).padStart(2, "0")}.${ext}`);
}

// --- mise en forme ----------------------------------------------------------
function enrouler(texte, largeur = 78) {
  return texte
    .split("\n\n")
    .map((para) => {
      if (/^\s*[-`]/.test(para) || para.includes("\n")) return para;
      const mots = para.split(/\s+/);
      const lignes = [];
      let ligne = "";
      for (const m of mots) {
        if ((ligne + " " + m).trim().length > largeur) {
          lignes.push(ligne);
          ligne = m;
        } else ligne = (ligne + " " + m).trim();
      }
      if (ligne) lignes.push(ligne);
      return lignes.join("\n");
    })
    .join("\n\n");
}

const sansMarkdown = (t) => t.replace(/\*\*(.+?)\*\*/g, "$1");
const enonce = (ex) => sansMarkdown(ex.statement).replaceAll("{fn}", ex.fn[lang]);

// Écrit une valeur JSON avec la syntaxe du langage choisi (True/False/None en Python).
function litteral(valeur) {
  if (lang !== "python") return JSON.stringify(valeur);
  if (valeur === null) return "None";
  if (valeur === true) return "True";
  if (valeur === false) return "False";
  if (Array.isArray(valeur)) return "[" + valeur.map(litteral).join(", ") + "]";
  if (typeof valeur === "object") return "{" + Object.entries(valeur).map(([k, v]) => `${JSON.stringify(k)}: ${litteral(v)}`).join(", ") + "}";
  return JSON.stringify(valeur);
}

const SANS_RETOUR = new Set(["undefined", "None"]);

// La valeur obtenue arrive en JSON depuis le juge : on la réécrit dans la syntaxe du langage.
function obtenuLitteral(got) {
  if (SANS_RETOUR.has(got)) return got;
  try {
    return litteral(JSON.parse(got));
  } catch {
    return got;
  }
}

function afficherHistoire(n) {
  const h = contenu.story.find((s) => s.day === n);
  if (!h) return;
  console.log(or(`✦ Jour ${n} — ${h.title}`));
  console.log();
  console.log(enrouler(h.text));
}

function afficherEnonce(ex) {
  console.log(gras(`${ex.title}`) + gris(`  (${ex.concept}, ${niveau})`));
  console.log();
  console.log(enrouler(enonce(ex)));
  console.log();
  console.log(gris("Exemples :"));
  for (const t of ex.tests.filter((x) => !x.hidden).slice(0, 3)) {
    console.log(gris(`  ${ex.fn[lang]}(${t.args.map(litteral).join(", ")})  →  ${litteral(t.expected)}`));
  }
}

function afficherRapport(rapport) {
  if (rapport.error) {
    console.log(rouge("✗ " + rapport.error));
    return;
  }
  for (const r of rapport.results) {
    if (r.hidden) {
      console.log(`  ${r.ok ? vert("✓") : rouge("✗")} test caché${r.ok ? "" : gris("  — ton code échoue sur un cas non montré (pense aux cas limites)")}`);
    } else if (r.ok) {
      console.log(`  ${vert("✓")} ${r.args.map(litteral).join(", ")}  →  ${obtenuLitteral(r.got)}`);
    } else {
      console.log(`  ${rouge("✗")} ${r.args.map(litteral).join(", ")}`);
      console.log(`      attendu : ${litteral(r.expected)}`);
      console.log(`      obtenu  : ${r.error ? rouge(r.error) : obtenuLitteral(r.got)}`);
      if (!r.error && SANS_RETOUR.has(r.got)) console.log(gris("      (ta fonction ne renvoie rien : as-tu écrit `return` ?)"));
    }
  }
  if (rapport.logs) {
    console.log(gris("\nSortie de ton programme :"));
    console.log(gris(rapport.logs.split("\n").map((l) => "  " + l).join("\n")));
  }
}

// --- commandes --------------------------------------------------------------
const commandes = {
  list() {
    console.log(gras(contenu.meta.title) + "\n");
    for (let n = 1; n <= 24; n++) {
      const h = contenu.story.find((s) => s.day === n);
      const dispo = niveaux.map((nv) => (trouverExercice(contenu, n, nv.id) ? nv.id : null)).filter(Boolean);
      const etat = dispo.length ? vert(dispo.join(", ")) : gris("histoire seulement");
      console.log(`  ${String(n).padStart(2)}  ${h.title.padEnd(34)} ${etat}`);
    }
    console.log(gris(`\nLangage : ${lang}  Niveau : ${niveau}  (options --lang, --level)`));
  },

  show() {
    const n = jourDemande();
    afficherHistoire(n);
    const ex = trouverExercice(contenu, n, niveau);
    console.log("\n" + "─".repeat(60) + "\n");
    if (!ex) return console.log(gris("L'exercice de ce jour n'est pas encore disponible pour ce niveau."));
    verifierChoix();
    afficherEnonce(ex);
    if (options.hint) console.log("\n" + or("Indice : ") + ex.hint);
    else console.log(gris("\nUn coup de pouce ? advent show " + n + " --hint"));
    console.log(gris(`Pour coder : advent init ${n} --lang ${lang} --level ${niveau}`));
  },

  init() {
    const n = jourDemande();
    const l = verifierChoix();
    const ex = exerciceDuJour(n);
    const chemin = fichierDuJour(n, l.ext);
    if (existsSync(chemin) && !options.force) {
      fin(`Le fichier existe déjà : ${chemin}\nUtilise --force pour l'écraser (ton travail serait perdu), ou lance : advent check ${n}`);
    }
    const commentaire = l.id === "python" ? "# " : "// ";
    const entete = [
      `Jour ${n} — ${ex.title} (${niveau})`,
      "",
      ...enonce(ex).split("\n"),
      "",
      `Teste avec : node cli/advent.mjs check ${n} --lang ${lang} --level ${niveau}`,
    ].map((ligne) => (commentaire + ligne).trimEnd());
    mkdirSync(dirname(chemin), { recursive: true });
    writeFileSync(chemin, entete.join("\n") + "\n\n" + ex.starter[lang]);
    console.log(vert("✓ Fichier créé : ") + chemin);
    console.log(gris(`Édite-le dans ton éditeur, puis : advent check ${n} --lang ${lang} --level ${niveau}`));
  },

  check() {
    const n = jourDemande();
    const l = verifierChoix();
    const ex = exerciceDuJour(n);
    const chemin = options.file ? resolve(options.file) : fichierDuJour(n, l.ext);
    if (!existsSync(chemin)) fin(`Fichier introuvable : ${chemin}\nCrée-le d'abord avec : advent init ${n} --lang ${lang} --level ${niveau}`);
    const rapport = juger(lang, readFileSync(chemin, "utf8"), ex);
    console.log(gras(`Jour ${n} — ${ex.title}`) + gris(`  (${lang}, ${niveau})`) + "\n");
    afficherRapport(rapport);
    const r = resume(rapport);
    console.log();
    if (r.tout) {
      console.log(vert(`✦ Bravo ! ${r.reussis}/${r.total} tests réussis.`) + gris(`  Compare avec : advent solution ${n} --yes`));
      process.exit(0);
    }
    if (!rapport.error) console.log(or(`${r.reussis}/${r.total} tests réussis.`) + gris(`  Un indice ? advent show ${n} --hint`));
    process.exit(1);
  },

  solution() {
    const n = jourDemande();
    verifierChoix();
    const ex = exerciceDuJour(n);
    if (!options.yes) {
      fin(`Spoiler ! Ajoute --yes pour afficher la solution du jour ${n}.\nUn indice d'abord ? advent show ${n} --hint`, 2);
    }
    console.log(or(`Solution du jour ${n} — ${ex.title} (${lang})`) + "\n");
    console.log(ex.solution[lang]);
  },

  mail() {
    const n = jourDemande();
    const l = verifierChoix();
    const ex = exerciceDuJour(n);
    const h = contenu.story.find((s) => s.day === n);
    const nom = `jour-${String(n).padStart(2, "0")}.${l.ext}`;
    console.log(`À       : toi@exemple.invalid`);
    console.log(`De      : Pixel <pixel@givreville.invalid>`);
    console.log(`Objet   : 🎁 Case ${n} — ${h.title}`);
    console.log(`Pièce jointe : jour-${String(n).padStart(2, "0")}.zip  (${nom} + check)`);
    console.log("\n" + "=".repeat(60) + "\n");
    console.log(`Bonjour,\n`);
    console.log(enrouler(h.text) + "\n");
    console.log("— L'exercice du jour —\n");
    afficherEnonce(ex);
    console.log("\n— Comment jouer —\n");
    console.log(`  1. Décompresse le zip et ouvre ${nom} dans ton éditeur.`);
    console.log(`  2. Écris ta fonction ${ex.fn[lang]}.`);
    console.log(`  3. Teste en local : ${l.id === "python" ? "python3 check.py" : "node check.js"}`);
    console.log(`  4. Quand tu es prêt·e :`);
    console.log(`       Voir la solution     → https://exemple.invalid/solution/<jeton-signé>`);
    console.log(`       Soumettre ma réponse → https://exemple.invalid/soumettre/<jeton-signé>`);
    console.log(gris("\n(Aperçu : aucun mail n'est envoyé, les liens sont fictifs.)"));
  },
};

function aide() {
  console.log(`${gras(contenu.meta.title)} — mode terminal

Usage : node cli/advent.mjs <commande> [jour] [options]

  list                  les 24 jours et ce qui est jouable
  show <jour>           histoire + énoncé (--hint pour l'indice)
  init <jour>           crée ton fichier de travail dans advent-work/
  check <jour>          lance les tests sur ton fichier (--file pour un autre chemin)
  solution <jour> --yes affiche la solution (spoiler)
  mail <jour>           aperçu du mail de ce jour

Options : --lang ${langages.map((x) => x.id).join("|")}   --level ${niveaux.map((x) => x.id).join("|")}   --dir <dossier>   --force
Variables : ADVENT_LANG, ADVENT_LEVEL, NO_COLOR`);
}

if (!commande || commande === "help" || commande === "--help" || !commandes[commande]) {
  if (commande && commande !== "help" && commande !== "--help") console.error(`Commande inconnue : « ${commande} »\n`);
  aide();
  process.exit(commande && !["help", "--help"].includes(commande) ? 1 : 0);
}
commandes[commande]();
