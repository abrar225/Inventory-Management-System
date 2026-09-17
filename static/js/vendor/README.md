# Vendored JavaScript libraries

These files are **generated** — do not edit them by hand.

Alpine.js and HTMX are declared as npm dependencies in `package.json`. Running
`npm install` fetches them and the `postinstall` hook (`scripts/vendor-js.mjs`)
copies the minified builds here:

- `alpine.min.js` ← `node_modules/alpinejs/dist/cdn.min.js`
- `htmx.min.js` ← `node_modules/htmx.org/dist/htmx.min.js`

To refresh manually: `npm run vendor:js`. To bump versions, edit the ranges in
`package.json` and re-run `npm install`.

They are committed to the repo (not loaded from a CDN at runtime) so the app
works offline with no third-party runtime dependency.

Chart.js, Tom Select, and Heroicons are added in the phases that first use them
(Dashboard, catalog forms), following the same approach.
