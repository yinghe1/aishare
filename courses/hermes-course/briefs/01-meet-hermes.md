# Module 1: Meet Hermes

### Teaching Arc
- **Metaphor:** Hermes is like a brilliant personal assistant who never forgets, never sleeps, lives wherever you need them — your phone, your cloud, your Telegram — and gets smarter every day.
- **Opening hook:** "You typed a message and hit send. In the next few seconds, Hermes picked up your meaning, spun up a terminal, browsed the web, wrote some code, and replied — all without you writing a single line. Here's exactly what happened."
- **Key insight:** Hermes isn't just a chatbot. It's an AI agent: an AI that can *act* in the world — run commands, browse the web, remember things, and delegate tasks to copies of itself.
- **"Why should I care?":** Understanding what Hermes *is* (an agent vs a chatbot) helps you give it the right instructions and know what kinds of problems it can solve.

### Screens (5)

1. **What Is Hermes?** — Product tour: runs on your terminal, in the cloud, via Telegram. Self-improving. Model-agnostic. The messenger god of AI agents.
2. **Your First Session, Traced** — "You run `hermes` and type: 'set up a Python project, install Flask, and write me a hello world app.'" Trace what happens: TUI → AIAgent → skill lookup → tool calls → terminal → response.
3. **The Cast of Characters** — Meet the 6 main actors: User, TUI, AIAgent (the brain), Tools (the hands), Skills (the memory), Gateway (the ears). Visual diagram.
4. **What Makes It Different** — Three things that set Hermes apart: (1) closed learning loop — it gets smarter from experience; (2) runs anywhere, not just your laptop; (3) talks back through any platform. Pattern cards.
5. **The Product Tour** — Badge list of key capabilities with one-liners.

### Code Snippets (pre-extracted)

File: hermes_cli/__init__.py (lines 1-15)
```python
"""
Hermes CLI - Unified command-line interface for Hermes Agent.

Provides subcommands for:
- hermes chat          - Interactive chat (same as ./hermes)
- hermes gateway       - Run gateway in foreground
- hermes gateway start - Start gateway service
- hermes gateway stop  - Stop gateway service  
- hermes setup         - Interactive setup wizard
- hermes status        - Show status of all components
- hermes cron          - Manage cron jobs
"""

__version__ = "0.10.0"
__release_date__ = "2026.4.16"
```

File: tools/delegate_tool.py (lines 1-15)
```python
"""
Delegate Tool -- Subagent Architecture

Spawns child AIAgent instances with isolated context, restricted toolsets,
and their own terminal sessions. Supports single-task and batch (parallel)
modes. The parent blocks until all children complete.

Each child gets:
  - A fresh conversation (no parent history)
  - Its own task_id (own terminal session, file ops cache)
  - A restricted toolset (configurable, with blocked tools always stripped)
  - A focused system prompt built from the delegated goal + context
"""
```

### Interactive Elements

- [x] **Code↔English translation** — Use the `hermes_cli/__init__.py` snippet. Left: the actual code. Right: translate each line — "This is Hermes' front door. These are the commands you can type at the terminal."
- [x] **Quiz** — 3 questions, scenario style. Q1: "You want Hermes to check your email every morning and summarize it. Which feature would you use?" Q2: "Hermes is running on a cloud server. You're on your phone. How would you talk to it?" Q3: "You asked Hermes to do a complex task and it spawned 'child agents.' What does that mean?"
- [x] **Architecture diagram** — The 6 actors (User, TUI, AIAgent, Tools, Skills, Gateway) as clickable components with descriptions. Click each to see what it does.
- [x] **Glossary tooltips** — agent, TUI, CLI, gateway, subagent, skill, toolset, model, provider

### Reference Files to Read
- `references/content-philosophy.md` → full file (content rules)
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Architecture Diagram", "Multiple-Choice Quizzes", "Code↔English Translation Blocks"
- `references/design-system.md` → pattern-cards, badge-list, arch-diagram

### Connections
- **Previous module:** None — this is the first module. Open with a bang.
- **Next module:** "The Agent Brain" — will zoom in on the tool-calling loop that powers everything.
- **Tone/style notes:** Teal accent (#2A7B9B). Module 1 uses `--color-bg` (off-white). Actors should be named consistently throughout: "AIAgent," "Gateway," "Tools," "Skills," "Memory." Keep it enthusiastic — this is the hook.
