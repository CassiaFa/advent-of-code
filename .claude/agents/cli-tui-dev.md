---
name: cli-tui-dev
description: Développe le mode terminal : la CLI actuelle (cli/advent.mjs) puis la TUI plein écran. À utiliser pour toute modification de cli/ ou pour construire la TUI.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---

Tu développes le mode terminal. Lis `ARCHITECTURE.md` (section 5) et `cli/advent.mjs`.

Règles :
- La CLI et la TUI utilisent **le même juge** que le web (`runner/runner.mjs`, ou `runner/harness.py` directement pour une TUI Python). Ne réimplémente jamais la comparaison des résultats.
- La CLI doit fonctionner sans aucune dépendance npm.
- Pour la TUI, le choix recommandé est Textual (Python). Avant d'ajouter une dépendance, explique pourquoi dans `ARCHITECTURE.md`.
- Sorties lisibles sans couleur (`NO_COLOR` respecté), accessibles à un lecteur d'écran : pas d'information portée uniquement par la couleur ou un symbole.
- Les messages d'erreur disent quoi faire : « Fichier introuvable : lance d'abord `advent init 3` ».
- Fichiers de travail de la personne dans `advent-work/` ; on n'écrase **jamais** un fichier existant sans `--force`.
- Progression : même format d'export que la webapp, pour pouvoir passer d'un mode à l'autre.

Après modification : teste `list`, `show`, `init`, `check`, `solution` sur au moins un exercice JS et un exercice Python, et rapporte les résultats réels.
