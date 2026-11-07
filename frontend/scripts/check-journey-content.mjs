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
    if (t.remediation) {
      const r = t.remediation;
      for (const k of ['id', 'knowledgeId', 'title', 'intro', 'code', 'prompt', 'insight']) requireThat(text(r[k]), `${file}/${t.id}: missing remediation ${k}`);
      const f = r.field;
      requireThat(f && text(f.id) && text(f.label) && Array.isArray(f.options) && f.options.length >= 2, `${file}/${t.id}: invalid remediation field`);
      unique(f.options.map(o => o.id), `${file}/${r.id}`);
      unique(f.options.map(o => o.text), `${file}/${r.id}`);
      requireThat(f.options.every(o => text(o.id) && text(o.text) && text(o.feedback)) && f.options.some(o => o.id === f.correctOptionId), `${file}/${r.id}: invalid remediation options`);
      requireThat(r.prompt !== t.prompt && r.code !== t.code, `${file}/${r.id}: remediation must use different material`);
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
const delayed = JSON.parse(fs.readFileSync(path.join(root, 'src/content/delayedChecks.json'), 'utf8'));
requireThat(Number.isInteger(delayed.version) && delayed.version > 0 && Array.isArray(delayed.items), 'invalid delayed bank');
unique(delayed.items.map(i => i.id), 'delayed items');
for (const item of delayed.items) {
  for (const k of ['id', 'slug', 'taskId', 'knowledgeId', 'title', 'prompt', 'code', 'explanation']) requireThat(text(item[k]), `delayed: missing ${k}`);
  const lesson = JSON.parse(fs.readFileSync(path.join(dir, `${item.slug}.json`), 'utf8'));
  const task = lesson.tasks.find(t => t.id === item.taskId);
  requireThat(task?.remediation?.knowledgeId === item.knowledgeId, `delayed ${item.id}: unknown concept`);
  requireThat(item.code !== task.code && item.code !== task.remediation.code, `delayed ${item.id}: reused material`);
  requireThat(Array.isArray(item.options) && item.options.length >= 2 && item.options.every(o => text(o.id) && text(o.text)), `delayed ${item.id}: invalid choices`);
  unique(item.options.map(o => o.id), item.id); unique(item.options.map(o => o.text), item.id);
  requireThat(item.options.some(o => o.id === item.correctOptionId), `delayed ${item.id}: missing answer`);
}
const delayedHash = crypto.createHash('sha256').update(JSON.stringify(delayed)).digest('hex');
const oldDelayed = releases['delayed-checks'];
if (oldDelayed) requireThat(delayed.version > oldDelayed.version || (delayed.version === oldDelayed.version && delayedHash === oldDelayed.hash), 'published delayed bank changed; increment version and use new IDs for revised material');
next['delayed-checks'] = { version: delayed.version, hash: delayedHash };
const guides = JSON.parse(fs.readFileSync(path.join(root, 'src/content/standardGuides.json'), 'utf8'));
requireThat(Number.isInteger(guides.version) && guides.version > 0, 'invalid standard guide version');
const l2Slugs = Object.keys(next).filter(slug => slug.startsWith('l2-'));
requireThat(Object.keys(guides.lessons).length === l2Slugs.length && l2Slugs.every(slug => guides.lessons[slug]), 'standard guides must cover L2');
for (const [slug, guide] of Object.entries(guides.lessons)) {
  const lesson = JSON.parse(fs.readFileSync(path.join(dir, `${slug}.json`), 'utf8'));
  requireThat(text(guide.title) && Array.isArray(guide.sections), `${slug}: invalid guide`);
  unique(guide.sections.map(s => s.id), `${slug}: guide IDs`);
  requireThat(guide.sections.length === lesson.tasks.length && lesson.tasks.every(t => guide.sections.some(s => s.id === t.id)), `${slug}: guide coverage`);
  requireThat(guide.sections.every(s => ['title','body','boundary'].every(k => text(s[k]))), `${slug}: empty standard section`);
  requireThat(Array.isArray(guide.sources) && guide.sources.length && guide.sources.every(s => text(s.title) && new URL(s.url).origin === 'https://spark.apache.org'), `${slug}: missing official sources`);
}
const guidesHash = crypto.createHash('sha256').update(JSON.stringify(guides)).digest('hex');
const oldGuides = releases['standard-guides'];
if (oldGuides) requireThat(guides.version > oldGuides.version || (guides.version === oldGuides.version && guidesHash === oldGuides.hash), 'published standard guides changed; increment guide version');
next['standard-guides'] = {version: guides.version, hash: guidesHash};
if (process.argv.includes('--record-release')) fs.writeFileSync(releasePath, JSON.stringify(next, null, 2) + '\n');
console.log(`PASS content: ${Object.keys(next).length - 2} lessons / ${tasks} tasks / ${delayed.items.length} delayed checks, IDs, feedback, assets and release versions`);
