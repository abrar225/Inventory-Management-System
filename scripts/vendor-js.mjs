/**
 * Copy vendored JS libraries from node_modules into static/js/vendor/.
 *
 * Runs on `npm install` (postinstall) and via `npm run vendor:js`. Keeping the
 * libraries committed under static/ means the app has no CDN runtime
 * dependency and works offline, while npm still owns the version pinning.
 */
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dest = resolve(root, "static/js/vendor");

const files = [
  ["node_modules/alpinejs/dist/cdn.min.js", "alpine.min.js"],
  ["node_modules/htmx.org/dist/htmx.min.js", "htmx.min.js"],
];

mkdirSync(dest, { recursive: true });

let copied = 0;
for (const [from, to] of files) {
  const src = resolve(root, from);
  if (!existsSync(src)) {
    console.warn(`[vendor-js] skip: ${from} not found (run npm install first)`);
    continue;
  }
  copyFileSync(src, resolve(dest, to));
  console.log(`[vendor-js] ${to}`);
  copied++;
}
console.log(`[vendor-js] copied ${copied}/${files.length} file(s).`);
