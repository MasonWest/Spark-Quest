import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = path.join(root, 'src/content/lessons');
const releasePath = path.join(root, 'src/content/releases.json');
const releases = fs.existsSync(releasePath) ? JSON.parse(fs.readFileSync(releasePath, 'utf8')) : {};
const courseSeed = JSON.parse(fs.readFileSync(path.join(root, '../backend/app/course_seed.json'), 'utf8'));
const originals = new Map(courseSeed.levels.flatMap(level => level.lessons.map(lesson => [lesson.slug, lesson.content.explanation])));
const next = {};
let tasks = 0;
function requireThat(ok, message) { if (!ok) throw new Error(message); }
function text(s) { return typeof s === 'string' && s.trim().length > 0; }
function unique(items, name) { requireThat(new Set(items).size === items.length, `${name}: duplicate IDs or values`); }
for (const file of fs.readdirSync(dir).filter(f => f.endsWith('.json'))) {
  const l = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  requireThat(file === `${l.slug}.json`, `${file}: slug mismatch`);
  requireThat(Number.isInteger(l.version) && l.version > 0, `${file}: invalid version`);
  for (const k of ['title', 'mission', 'next', 'source']) requireThat(text(l[k]), `${file}: missing ${k}`);
  requireThat(new URL(l.source).protocol === 'https:', `${file}: source must use HTTPS`);
  requireThat(Array.isArray(l.tasks) && l.tasks.length > 0, `${file}: no tasks`);
  unique(l.tasks.map(t => t.id), file);
  for (const t of l.tasks) {
    tasks++;
    for (const k of ['id', 'title', 'intro', 'code', 'prompt', 'insight', 'ability']) requireThat(text(t[k]), `${file}/${t.id}: missing ${k}`);
    requireThat(Array.isArray(t.knowledgeIds) && t.knowledgeIds.length && t.knowledgeIds.every(text), `${file}/${t.id}: no knowledge IDs`);
    requireThat(Array.isArray(t.fields) && t.fields.length, `${file}/${t.id}: no answer fields`);
    unique(t.fields.map(f => f.id), `${file}/${t.id}`);
    for (const f of t.fields) {
      requireThat(text(f.id) && text(f.label) && Array.isArray(f.options) && f.options.length >= 2, `${file}/${t.id}: invalid field`);
      unique(f.options.map(o => o.id), `${file}/${t.id}/${f.id}`);
      unique(f.options.map(o => o.text), `${file}/${t.id}/${f.id}`);
      requireThat(f.options.every(o => text(o.id) && text(o.text) && text(o.feedback)), `${file}/${t.id}: option missing feedback`);
      requireThat(f.options.some(o => o.id === f.correctOptionId), `${file}/${t.id}: dangling correctOptionId`);
    }
    if (t.reading) {
      for (const k of ['sectionTitle', 'caution']) if (t.reading[k] !== undefined) requireThat(text(t.reading[k]), `${file}/${t.id}: empty reading ${k}`);
      for (const k of ['id', 'title', 'startMarker', 'endMarker', 'connection', 'boundary']) requireThat(text(t.reading[k]), `${file}/${t.id}: missing reading ${k}`);
      const original = originals.get(l.slug) ?? '';
      const start = original.indexOf(t.reading.startMarker);
      const from = start + t.reading.startMarker.length;
      const end = original.indexOf(t.reading.endMarker, from);
      requireThat(start >= 0 && original.indexOf(t.reading.startMarker, from) < 0 && end > from && text(original.slice(from, end)), `${file}/${t.id}: missing/ambiguous original reading segment`);
    }
    if (t.table) requireThat(t.table.columns.length && t.table.rows.every(r => r.length === t.table.columns.length), `${file}: invalid table`);
  }
  if (l.legacyTaskIds) {
    unique(l.legacyTaskIds, `${file}: legacy migration`);
    requireThat(l.legacyTaskIds.every(id => l.tasks.some(t => t.id === id)), `${file}: dangling migration ID`);
  }
  if (l.project) for (const d of [...l.project.downloads, l.project.solution]) {
    requireThat(text(d.label) && d.href.startsWith('/practice/'), `${file}: invalid download`);
    const dest = path.resolve(root, 'public', d.href.slice(1));
    requireThat(dest.startsWith(path.join(root, 'public') + path.sep) && fs.existsSync(dest), `${file}: missing/unsafe asset ${d.href}`);
  }
  const hash = crypto.createHash('sha256').update(JSON.stringify(l)).digest('hex');
  const previous = releases[l.slug];
  if (previous) requireThat(l.version > previous.version || (l.version === previous.version && hash === previous.hash), `${file}: published content changed; increment version, preserve IDs, then record release`);
  next[l.slug] = { version: l.version, hash };
}
if (process.argv.includes('--record-release')) fs.writeFileSync(releasePath, JSON.stringify(next, null, 2) + '\n');
console.log(`PASS content: ${Object.keys(next).length} lessons / ${tasks} tasks, IDs, feedback, assets and release versions`);
