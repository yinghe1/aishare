# Module 5: 40+ Powers — The Toolkit

### Teaching Arc
- **Metaphor:** Hermes' tools are like a Swiss Army knife — each blade is specialized, retractable when not needed, and there's a safety lock for the dangerous ones. You wouldn't use a corkscrew to cut bread, and Hermes won't use a file-delete tool when a read will do.
- **Opening hook:** "When you ask Hermes to 'build me a REST API,' it doesn't guess what commands to run. It has 40+ specific tools — each purpose-built for one kind of task. And before it does anything destructive, it asks you first."
- **Key insight:** Tools are organized into "toolsets" — logical groupings like 'terminal', 'file', 'web'. You can enable or disable whole toolsets. Dangerous commands require explicit approval. The approval system is a security layer that prevents accidents.
- **"Why should I care?":** Knowing which toolsets exist means you can tell Hermes exactly what permissions to use, debug "why won't it do X," and understand what it can and can't touch on your system.

### Screens (5)

1. **The Tool Zoo** — Visual overview of the major tool categories: Terminal (run commands), File (read/write/patch), Web (search, browse, extract), Memory (read/write notes), Skills (invoke skills), Delegate (spawn subagents), Cron (schedule jobs), Vision (analyze images), Voice (transcribe audio), MCP (connect to external services). Pattern cards.
2. **Toolsets: The Permission System** — You can configure which toolsets are enabled. `hermes tools` shows the menu. Toolsets are defined in `toolsets.py`. Each toolset is a named group of tools. Default toolsets for subagents: terminal, file, web. Code↔English on the TOOLSETS structure.
3. **The Dangerous Command Gate** — When a tool call matches a dangerous pattern (rm -rf, chmod 777, writing to /etc/), Hermes pauses and asks. The approval system has three levels: approve once, approve for session, add to permanent allowlist. Smart approval via auxiliary LLM auto-approves clearly low-risk commands.
4. **MCP: Connect to Anything** — MCP (Model Context Protocol) lets you connect Hermes to external services: Google Drive, Gmail, GitHub, Slack. These appear as tools. OAuth flow happens once and credentials are stored. This is how Hermes becomes a hub for your entire digital life.
5. **Parallel Tool Execution** — Some tools run simultaneously. Example: Hermes needs to search the web AND read a local file — it dispatches both at once. The _PARALLEL_SAFE_TOOLS list defines which are safe to parallelize. This can dramatically speed up complex tasks.

### Code Snippets (pre-extracted)

File: tools/approval.py (lines 76-84)
```python
DANGEROUS_PATTERNS = [
    (r'\brm\s+(-[^\s]*\s+)*/', "delete in root path"),
    (r'\brm\s+-[^\s]*r', "recursive delete"),
    (r'\brm\s+--recursive\b', "recursive delete (long flag)"),
    (r'\bchmod\s+(-[^\s]*\s+)*(777|666|o\+[rwx]*w|a\+[rwx]*w)\b', "world/other-writable permissions"),
]
```

File: tools/approval.py (lines 1-11) — module docstring
```python
"""Dangerous command approval -- detection, prompting, and per-session state.

This module is the single source of truth for the dangerous command system:
- Pattern detection (DANGEROUS_PATTERNS, detect_dangerous_command)
- Per-session approval state (thread-safe, keyed by session_key)
- Approval prompting (CLI interactive + gateway async)
- Smart approval via auxiliary LLM (auto-approve low-risk commands)
- Permanent allowlist persistence (config.yaml)
"""
```

File: tools/delegate_tool.py (lines 40-46) — toolset list for subagents
```python
_EXCLUDED_TOOLSET_NAMES = frozenset({"debugging", "safe", "delegation", "moa", "rl"})
_SUBAGENT_TOOLSETS = sorted(
    name for name, defn in TOOLSETS.items()
    if name not in _EXCLUDED_TOOLSET_NAMES
    and not name.startswith("hermes-")
    and not all(t in DELEGATE_BLOCKED_TOOLS for t in defn.get("tools", []))
)
```

### Interactive Elements

- [x] **Code↔English translation** — Use the DANGEROUS_PATTERNS snippet. Right side: "These are the patterns Hermes checks before running any shell command. If a command matches, it stops and asks you. 'rm -rf /' would match line 1. 'chmod 777 myfile' matches line 4. This is your safety net."
- [x] **Drag-and-drop** — Task: "Match each task to the right toolset." Chips: "Browse a website", "Run 'git status'", "Write a file", "Transcribe a voice message", "Search Google". Zones: Web tools, Terminal tools, File tools, Voice tools, Web tools. Teaches learner which toolset handles what.
- [x] **Quiz** — 3 questions. Q1: "Hermes is about to run 'rm -rf ./node_modules'. It pauses and asks you. You know this is safe. What's the fastest way to prevent future interruptions for this exact command?" Q2: "You want Hermes to only use web tools — no terminal access. How would you restrict this?" Q3: "You connected Gmail via MCP. Now Hermes can read your emails as a tool. Is this data stored permanently by Hermes?"
- [x] **Glossary tooltips** — toolset, MCP (Model Context Protocol), OAuth, regex, pattern matching, allowlist, shell command, parallel execution

### Reference Files to Read
- `references/content-philosophy.md` → full file
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Drag-and-Drop Matching", "Code↔English Translation Blocks", "Multiple-Choice Quizzes", "Pattern Cards"

### Connections
- **Previous module:** "The Long Arm" — showed gateway, cron, delegation. This module is about what's in the toolbox those systems use.
- **Next module:** "Design Lens" — will step back and analyze why these design decisions were made, what trade-offs were accepted, and what's next.
- **Tone/style notes:** Teal accent. Module 5 uses `--color-bg` (off-white). Keep the Swiss Army knife metaphor light — one mention at the start.
