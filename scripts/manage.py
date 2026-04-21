#!/usr/bin/env python3
"""
aishare content manager — add shares/courses, search, build data.js

Usage:
  python scripts/manage.py add share
  python scripts/manage.py add course
  python scripts/manage.py list [--type share|course]
  python scripts/manage.py search <query>
  python scripts/manage.py delete <id>
  python scripts/manage.py build
"""

import sqlite3
import json
import argparse
import math
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "aishare.db"
DATA_JS_PATH = ROOT / "data" / "data.js"
META_JS_PATH = ROOT / "data" / "meta.js"
SEARCH_INDEX_PATH = ROOT / "data" / "search-index.js"
PAGES_DIR = ROOT / "data" / "pages"
PAGE_SIZE = 50

BASE_URL = "https://yinghe1.github.io/aishare"

SEED_SHARES = [
    {
        "date": "04/18/2026",
        "title": "Claude Design",
        "author": "Ryan Mather",
        "tag": "Ryan Mather",
        "read_time": "2 min read",
        "url": f"{BASE_URL}/share/agency/ClaudeDesignByRyanMather04182026.html",
        "content": "",
    },
    {
        "date": "04/10/2026",
        "title": "Scaling Managed Agents: Decoupling the brain from the hands",
        "author": "Anthropic",
        "tag": "Anthropic",
        "read_time": "10 min read",
        "url": "https://www.anthropic.com/engineering/managed-agents",
        "content": "Managed agents architecture decouples brain (Claude + harness) from hands (sandboxes + tools). Covers session management, security boundaries, 60% reduction in time-to-first-token at p50.",
    },
    {
        "date": "04/11/2026",
        "title": "Thin Harness Fat Skills",
        "author": "Garry Tan",
        "tag": "Garry Tan",
        "read_time": "6 min read",
        "url": f"{BASE_URL}/share/agency/ThinHarnessFatSkillsByGaryTan04112026.html",
        "content": "",
    },
    {
        "date": "04/06/2026",
        "title": "Why System Like OpenClaw Is an Agent Loop",
        "author": "",
        "tag": "",
        "read_time": "3 min read",
        "url": f"{BASE_URL}/share/agency/agent_loop_explainer.html",
        "content": "",
    },
    {
        "date": "04/05/2026",
        "title": "Personalize Your FREE AI Learning",
        "author": "",
        "tag": "",
        "read_time": "8 min read",
        "url": f"{BASE_URL}/share/04052026/slides04052026.html",
        "content": "",
    },
]

SEED_COURSES = [
    {
        "date": "04/18/2026",
        "title": "Hermes Agent: How It Works",
        "tag": "6 modules",
        "read_time": "~45 min",
        "url": f"{BASE_URL}/courses/hermes-course/",
        "src_url": "https://github.com/nousresearch/hermes-agent",
    },
    {
        "date": "04/05/2026",
        "title": "Inside Oh My OpenCode",
        "tag": "6 modules",
        "read_time": "~45 min",
        "url": f"{BASE_URL}/courses/oh-my-opencode-course/",
        "src_url": "https://github.com/opensoft/oh-my-opencode",
    },
]


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            type       TEXT NOT NULL CHECK(type IN ('share','course')),
            date       TEXT NOT NULL,
            title      TEXT NOT NULL,
            author     TEXT DEFAULT '',
            tag        TEXT DEFAULT '',
            read_time  TEXT DEFAULT '',
            url        TEXT NOT NULL,
            src_url    TEXT DEFAULT '',
            content    TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
            title,
            author,
            content,
            content='items',
            content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
            INSERT INTO items_fts(rowid, title, author, content)
            VALUES (new.id, new.title, new.author, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
            INSERT INTO items_fts(items_fts, rowid, title, author, content)
            VALUES ('delete', old.id, old.title, old.author, old.content);
        END;

        CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
            INSERT INTO items_fts(items_fts, rowid, title, author, content)
            VALUES ('delete', old.id, old.title, old.author, old.content);
            INSERT INTO items_fts(rowid, title, author, content)
            VALUES (new.id, new.title, new.author, new.content);
        END;
    """)
    conn.commit()


def _seed_if_empty(conn):
    count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    if count > 0:
        return
    print("Seeding initial data...")
    for s in SEED_SHARES:
        conn.execute(
            "INSERT INTO items (type,date,title,author,tag,read_time,url,content) VALUES (?,?,?,?,?,?,?,?)",
            ("share", s["date"], s["title"], s["author"], s["tag"], s["read_time"], s["url"], s["content"]),
        )
    for c in SEED_COURSES:
        conn.execute(
            "INSERT INTO items (type,date,title,tag,read_time,url,src_url) VALUES (?,?,?,?,?,?,?)",
            ("course", c["date"], c["title"], c["tag"], c["read_time"], c["url"], c["src_url"]),
        )
    conn.commit()


def _prompt(label, default=""):
    if default:
        val = input(f"  {label} [{default}]: ").strip()
        return val if val else default
    return input(f"  {label}: ").strip()


def _date_sort_key(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        return datetime.min


def cmd_add(args):
    conn = get_conn()
    today = datetime.now().strftime("%m/%d/%Y")

    if args.subtype == "share":
        print("\nAdd Share")
        date = _prompt("Date (MM/DD/YYYY)", today)
        title = _prompt("Title")
        author = _prompt("Author/Tag (optional)")
        read_time = _prompt("Read time (e.g. '5 min read') (optional)")
        url = _prompt("URL")
        content = _prompt("Content notes for search (optional)")

        conn.execute(
            "INSERT INTO items (type,date,title,author,tag,read_time,url,content) VALUES (?,?,?,?,?,?,?,?)",
            ("share", date, title, author, author, read_time, url, content),
        )

    elif args.subtype == "course":
        print("\nAdd Course")
        date = _prompt("Date (MM/DD/YYYY)", today)
        title = _prompt("Title")
        modules = _prompt("Modules count (e.g. 6)")
        tag = f"{modules} modules" if modules else ""
        src_url = _prompt("GitHub src URL (optional)")
        read_time = _prompt("Read time (e.g. '~45 min') (optional)")
        url = _prompt("Course URL")

        conn.execute(
            "INSERT INTO items (type,date,title,tag,read_time,url,src_url) VALUES (?,?,?,?,?,?,?)",
            ("course", date, title, tag, read_time, url, src_url),
        )

    conn.commit()
    print(f"\n✓ Added '{title}'")
    conn.close()


def cmd_list(args):
    conn = get_conn()
    where = f"WHERE type='{args.type}'" if args.type else ""
    rows = conn.execute(f"SELECT id,type,date,title,author,tag FROM items {where} ORDER BY created_at DESC LIMIT ?", (args.limit,)).fetchall()
    if not rows:
        print("No items found.")
        return
    for r in rows:
        tag_display = r["author"] or r["tag"]
        print(f"[{r['id']:3}] {r['type']:6}  {r['date']}  {r['title'][:55]:<55}  {tag_display}")
    conn.close()


def cmd_search(args):
    conn = get_conn()
    query = " ".join(args.query)

    # FTS5 search
    rows = conn.execute("""
        SELECT i.id, i.type, i.date, i.title, i.author, i.tag
        FROM items_fts f
        JOIN items i ON i.id = f.rowid
        WHERE items_fts MATCH ?
        ORDER BY rank
    """, (query,)).fetchall()

    # Fallback: LIKE search
    if not rows:
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT id, type, date, title, author, tag FROM items
            WHERE title LIKE ? OR author LIKE ? OR content LIKE ?
            ORDER BY date DESC
        """, (like, like, like)).fetchall()

    if not rows:
        print(f"No results for '{query}'")
        return

    print(f"\n{len(rows)} result(s) for '{query}':\n")
    for r in rows:
        tag_display = r["author"] or r["tag"]
        print(f"[{r['id']:3}] {r['type']:6}  {r['date']}  {r['title'][:55]:<55}  {tag_display}")
    conn.close()


def cmd_delete(args):
    conn = get_conn()
    row = conn.execute("SELECT title FROM items WHERE id=?", (args.id,)).fetchone()
    if not row:
        print(f"No item with id {args.id}")
        conn.close()
        return
    confirm = input(f"Delete '{row['title']}'? [y/N]: ").strip().lower()
    if confirm == "y":
        conn.execute("DELETE FROM items WHERE id=?", (args.id,))
        conn.commit()
        print("Deleted.")
    else:
        print("Cancelled.")
    conn.close()


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def cmd_build(args):
    conn = get_conn()
    _seed_if_empty(conn)

    shares_rows = conn.execute(
        "SELECT date,title,author,tag,read_time,url FROM items WHERE type='share'"
    ).fetchall()
    courses_rows = conn.execute(
        "SELECT date,title,tag,read_time,url,src_url FROM items WHERE type='course'"
    ).fetchall()
    conn.close()

    def clean(d):
        return {k: v for k, v in d.items() if v}

    shares = [clean(dict(r)) for r in sorted(shares_rows, key=lambda x: _date_sort_key(x["date"]), reverse=True)]
    courses = [clean(dict(r)) for r in sorted(courses_rows, key=lambda x: _date_sort_key(x["date"]), reverse=True)]

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    header = f"// Auto-generated by scripts/manage.py — do not edit manually\n// Last built: {now}\n"
    jc = (',', ':')  # compact separators

    # Paginated share pages
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    for f in PAGES_DIR.glob("*.js"):
        f.unlink()

    share_chunks = list(_chunks(shares, PAGE_SIZE)) or [[]]
    for i, chunk in enumerate(share_chunks):
        (PAGES_DIR / f"shares-{i+1}.js").write_text(
            f"{header}(window.SHARE_PAGES=window.SHARE_PAGES||[])[{i}]={json.dumps(chunk, separators=jc)};\n"
        )

    course_chunks = list(_chunks(courses, PAGE_SIZE)) or [[]]
    for i, chunk in enumerate(course_chunks):
        (PAGES_DIR / f"courses-{i+1}.js").write_text(
            f"{header}(window.COURSE_PAGES=window.COURSE_PAGES||[])[{i}]={json.dumps(chunk, separators=jc)};\n"
        )

    # Meta
    meta = {
        "shares_total": len(shares),
        "shares_pages": math.ceil(len(shares) / PAGE_SIZE) if shares else 1,
        "courses_total": len(courses),
        "courses_pages": math.ceil(len(courses) / PAGE_SIZE) if courses else 1,
        "page_size": PAGE_SIZE,
    }
    META_JS_PATH.write_text(f"{header}window.SITE_META={json.dumps(meta)};\n")

    # Lazy search index — all items, loaded only when user searches
    SEARCH_INDEX_PATH.write_text(
        f"{header}window.SEARCH_INDEX={json.dumps({'shares': shares, 'courses': courses}, separators=jc)};\n"
    )

    # Legacy data.js kept for reference
    DATA_JS_PATH.write_text(
        f"{header}window.SITE_DATA={json.dumps({'shares': shares, 'courses': courses}, indent=2)};\n"
    )

    sp = meta["shares_pages"]
    cp = meta["courses_pages"]
    print(f"Built: {len(shares)} shares ({sp} page{'s' if sp>1 else ''}), {len(courses)} courses ({cp} page{'s' if cp>1 else ''})")
    print(f"  data/meta.js  data/search-index.js  data/pages/ ({sp + cp} files)")


def main():
    parser = argparse.ArgumentParser(description="aishare content manager")
    sub = parser.add_subparsers(dest="cmd")

    # add
    add_p = sub.add_parser("add")
    add_p.add_argument("subtype", choices=["share", "course"])

    # list
    list_p = sub.add_parser("list")
    list_p.add_argument("--type", choices=["share", "course"])
    list_p.add_argument("--limit", type=int, default=50)

    # search
    search_p = sub.add_parser("search")
    search_p.add_argument("query", nargs="+")

    # delete
    del_p = sub.add_parser("delete")
    del_p.add_argument("id", type=int)

    # build
    sub.add_parser("build")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "delete":
        cmd_delete(args)
    elif args.cmd == "build":
        cmd_build(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
