# aishare — Site README

## DB Design

**File:** `data/aishare.db` (SQLite, gitignored)

### `items` table

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER PK | Auto-increment |
| `type` | TEXT | `'share'` or `'course'` |
| `date` | TEXT | Display format: `MM/DD/YYYY` |
| `title` | TEXT | Card title |
| `author` | TEXT | Share only: author/tag label |
| `tag` | TEXT | Share: same as author; Course: e.g. `"6 modules"` |
| `read_time` | TEXT | e.g. `"10 min read"` or `"~45 min"` |
| `url` | TEXT | Primary link target |
| `src_url` | TEXT | Course only: GitHub source URL |
| `content` | TEXT | CLI-only notes/summary, used for FTS search |
| `created_at` | TEXT | ISO datetime, set on insert |

### `items_fts` virtual table (FTS5)

Full-text search index over `title`, `author`, and `content`. Kept in sync with `items` via three triggers (`items_ai`, `items_ad`, `items_au`). Uses `content='items'` mode — no data duplication.

---

## Frontend Data Files

`build` generates these files from the DB. Commit them; `data/aishare.db` stays local.

| File | Size at 10k items | Purpose |
|------|-------------------|---------|
| `data/meta.js` | ~200 bytes | Page counts and totals, loaded on every visit |
| `data/pages/shares-N.js` | ~12 KB each | 50 shares per page, first page loaded on visit |
| `data/pages/courses-N.js` | ~12 KB each | 50 courses per page, first page loaded on visit |
| `data/search-index.js` | ~500 KB gzipped | All items (minimal fields), lazy-loaded only when user searches |
| `data/data.js` | legacy | Full dataset, kept for reference only |

### Loading strategy

- **Page load**: fetches `meta.js` + `pages/shares-1.js` + `pages/courses-1.js` only (~25 KB total)
- **Load more**: each click fetches the next page file (~12 KB)
- **Search**: `search-index.js` is injected as a `<script>` tag on first keystroke, cached in memory for the session

---

## Raw SQLite Queries

```bash
# Open the DB
sqlite3 data/aishare.db
```

```sql
-- List all shares sorted by date
SELECT id, date, title, author, read_time FROM items
WHERE type = 'share'
ORDER BY date DESC;

-- List all courses
SELECT id, date, title, tag, url FROM items
WHERE type = 'course';

-- Full-text search (FTS5)
SELECT i.id, i.type, i.date, i.title
FROM items_fts f
JOIN items i ON i.id = f.rowid
WHERE items_fts MATCH 'managed agents'
ORDER BY rank;

-- Search by author (exact LIKE)
SELECT id, date, title FROM items
WHERE author LIKE '%Anthropic%';

-- Count by type
SELECT type, COUNT(*) FROM items GROUP BY type;

-- View a full record
SELECT * FROM items WHERE id = 2;

-- Delete a record
DELETE FROM items WHERE id = 2;
```

---

## Workflow

### Add a share
```bash
python3 scripts/manage.py add share
# prompts: date, title, author, read time, URL, content notes
```

### Add a course
```bash
python3 scripts/manage.py add course
# prompts: date, title, modules count, GitHub src URL, read time, URL
```

### List all items
```bash
python3 scripts/manage.py list
python3 scripts/manage.py list --type share
python3 scripts/manage.py list --type course
```

### Search (FTS5 on title + author + content)
```bash
python3 scripts/manage.py search "managed agents"
python3 scripts/manage.py search "anthropic"
```

### Delete an item
```bash
python3 scripts/manage.py delete <id>
# confirms before deleting
```

### Build the frontend
Regenerates all data files from the DB. Run after any add/delete before committing.
```bash
python3 scripts/manage.py build
```

### Deploy
```bash
git add data/meta.js data/search-index.js data/pages/ data/data.js
git commit -m "add: <title>"
git push
```

`data/aishare.db` is gitignored and stays local only. All `data/*.js` and `data/pages/*.js` files are committed and served by GitHub Pages.
