const http = require("node:http");
const fs = require("node:fs/promises");
const path = require("node:path");

const root = __dirname;
const host = process.env.HOST || "0.0.0.0";
const port = Number(process.env.PORT || 4286);

const types = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".webp": "image/webp",
  ".xml": "application/xml; charset=utf-8"
};

const responseHeaders = {
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN"
};

function resolvePath(requestUrl) {
  const url = new URL(requestUrl, `http://localhost:${port}`);
  const pathname = decodeURIComponent(url.pathname);
  const normalized = path.normalize(pathname).replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(root, normalized === "/" ? "index.html" : normalized);
  if (!filePath.startsWith(root)) {
    return null;
  }
  return { filePath, pathname: url.pathname };
}

const server = http.createServer(async (req, res) => {
  const resolved = resolvePath(req.url || "/");
  if (!resolved) {
    res.writeHead(403, { ...responseHeaders, "Content-Type": "text/plain; charset=utf-8" });
    res.end("Forbidden");
    return;
  }

  if (resolved.pathname === "/healthz") {
    res.writeHead(200, {
      ...responseHeaders,
      "Cache-Control": "no-cache",
      "Content-Type": "application/json; charset=utf-8"
    });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  try {
    const stat = await fs.stat(resolved.filePath);
    const finalPath = stat.isDirectory() ? path.join(resolved.filePath, "index.html") : resolved.filePath;
    const data = await fs.readFile(finalPath);
    const ext = path.extname(finalPath).toLowerCase();
    res.writeHead(200, {
      ...responseHeaders,
      "Cache-Control": ext === ".html" ? "no-cache" : "public, max-age=31536000, immutable",
      "Content-Type": types[ext] || "application/octet-stream"
    });
    res.end(data);
  } catch (error) {
    res.writeHead(404, { ...responseHeaders, "Content-Type": "text/plain; charset=utf-8" });
    res.end("Not found");
  }
});

server.listen(port, host, () => {
  console.log(`Battlefield 6 static site: http://${host}:${port}`);
});
