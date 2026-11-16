// Fusionne content/ en un seul fichier pour la webapp et copie le juge dans web/.
import { mkdirSync, writeFileSync, copyFileSync } from "node:fs";
import { join } from "node:path";
import { chargerContenu, RACINE } from "./lib.mjs";

const { meta, story, placement, jours, exercices } = chargerContenu();

const bundle = {
  meta,
  story,
  days: jours.map((j) => ({ day: j.day, concept: j.concept })),
  placement,
  exercises: exercices,
  builtAt: new Date().toISOString(),
};

const dataDir = join(RACINE, "web", "data");
const runnerDir = join(RACINE, "web", "runner");
mkdirSync(dataDir, { recursive: true });
mkdirSync(runnerDir, { recursive: true });

writeFileSync(join(dataDir, "content.json"), JSON.stringify(bundle));
copyFileSync(join(RACINE, "runner", "harness.js"), join(runnerDir, "harness.js"));
copyFileSync(join(RACINE, "runner", "harness.py"), join(runnerDir, "harness.py"));

console.log(`Bundle écrit : ${exercices.length} exercices, ${story.length} jours d'histoire → web/data/content.json`);
