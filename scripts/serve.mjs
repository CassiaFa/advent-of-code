// Petit serveur statique pour web/ (aucune dépendance).
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { RACINE } from "./lib.mjs";

const RACINE_WEB = join(RACINE, "web");
const PORT = Number(process.env.PORT) || 5173;
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".py": "text/plain; charset=utf-8",
  ".svg": "image/svg+xml",
};

createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  let chemin = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, "");
  if (chemin.endsWith("/")) chemin += "index.html";
  const complet = join(RACINE_WEB, chemin);
  if (!complet.startsWith(RACINE_WEB)) {
    res.writeHead(403).end("Interdit");
    return;
  }
  try {
    const contenu = await readFile(complet);
    res.writeHead(200, { "Content-Type": TYPES[extname(complet)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(contenu);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("Introuvable");
  }
}).listen(PORT, () => console.log(`Calendrier de l'Avent : http://localhost:${PORT}`));
