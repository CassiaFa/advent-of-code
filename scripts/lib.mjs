// Chargement du contenu : partagé par build, validate et la CLI.
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

export const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..");
export const CONTENU = join(RACINE, "content");

function lireJSON(chemin) {
  try {
    return JSON.parse(readFileSync(chemin, "utf8"));
  } catch (e) {
    throw new Error(`Impossible de lire ${chemin} : ${e.message}`);
  }
}

export function chargerContenu() {
  const meta = lireJSON(join(CONTENU, "meta.json"));
  const story = lireJSON(join(CONTENU, "story.json"));
  const placement = lireJSON(join(CONTENU, "placement.json"));

  const dossier = join(CONTENU, "exercises");
  const fichiers = readdirSync(dossier).filter((f) => /^day-\d{2}\.json$/.test(f)).sort();
  const jours = fichiers.map((f) => ({ fichier: f, ...lireJSON(join(dossier, f)) }));
  const exercices = jours.flatMap((j) => j.exercises);

  return { meta, story, placement, jours, exercices };
}

export function trouverExercice(contenu, jour, niveau) {
  return contenu.exercices.find((e) => e.day === jour && e.level === niveau);
}
