# Calendrier de l'Avent du Code

Un calendrier de l'Avent pour apprendre ou réviser la programmation, avec une histoire de Noël, en JavaScript ou en Python.

## Essayer le prototype

Il faut seulement Node.js 18+ (et Python 3 pour tester les exercices Python en terminal).

```bash
npm run dev          # ouvre http://localhost:5173
```

Au premier lancement, la webapp propose un test de niveau (12 questions). Les 24 portes sont jouables, en quatre niveaux : débutant, intermédiaire, confirmé, expert.

En terminal :

```bash
node cli/advent.mjs list
node cli/advent.mjs show 1
node cli/advent.mjs init 1 --lang python
# édite advent-work/jour-01.py, puis :
node cli/advent.mjs check 1 --lang python
```

Documentation : `CLAUDE.md` (règles et commandes), `ARCHITECTURE.md`, `ROADMAP.md`.
