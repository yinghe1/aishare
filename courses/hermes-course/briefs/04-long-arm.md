# Module 4: The Long Arm

### Teaching Arc
- **Metaphor:** Hermes is like a field operations center that can deploy agents anywhere. You're the general at HQ (Telegram on your phone). The ops center (Gateway) receives your orders 24/7. Subagents (Delegation) run parallel missions. The scheduler (Cron) handles standing orders. All reporting back to you.
- **Opening hook:** "Most AI tools only work when your laptop is open. Hermes runs on a $5 VPS, a GPU cluster, or a serverless platform — and you can talk to it from Telegram while it works. Here's how it reaches so far."
- **Key insight:** Three systems multiply Hermes' reach: Gateway (talks back through any messaging platform), Cron (acts on a schedule without you asking), and Delegation (spawns copies of itself to work in parallel). Each is a force multiplier.
- **"Why should I care?":** This is where Hermes graduates from 'smart chatbot' to 'autonomous assistant.' When you understand these three systems, you can design workflows that run while you sleep.

### Screens (5)

1. **The Gateway: Always-On Ears** — Hermes can receive messages from Telegram, Discord, Slack, WhatsApp, Signal, Email. The Gateway process runs separately, forwards messages to AIAgent, and sends replies back. Flow diagram: You → Telegram → Gateway → AIAgent → Gateway → Telegram → You.
2. **Six Places to Run** — Six terminal backends: local, Docker, SSH, Daytona, Singularity, Modal. Badge list with one-liners. Modal/Daytona = serverless — hibernates when idle, costs nearly nothing between sessions.
3. **The Cron Scheduler: Standing Orders** — You can create scheduled tasks with natural language: "Every morning at 8am, summarize my emails." Cron stores these as JSON jobs. Each job gets its own agent session. Security: cron prompts get scanned for injection attacks before running.
4. **Delegation: The Army of One** — `delegate_task` spawns child AIAgent instances. Each child: fresh context, restricted toolset, own terminal session, focused goal. Parent sees only the summary — not the child's reasoning. Up to 3 children run in parallel by default. Group chat animation.
5. **Delegation Safety: What Children Can't Do** — Children can never: call `delegate_task` again (no infinite nesting), interact with the user, write to shared memory, spawn their own gateway effects. MAX_DEPTH = 2 (parent → child → grandchild rejected). This is intentional.

### Code Snippets (pre-extracted)

File: tools/delegate_tool.py (lines 27-38)
```python
# Tools that children must never have access to
DELEGATE_BLOCKED_TOOLS = frozenset([
    "delegate_task",   # no recursive delegation
    "clarify",         # no user interaction
    "memory",          # no writes to shared MEMORY.md
    "send_message",    # no cross-platform side effects
    "execute_code",    # children should reason step-by-step, not write scripts
])
```

File: tools/delegate_tool.py (lines 47-50)
```python
_DEFAULT_MAX_CONCURRENT_CHILDREN = 3
MAX_DEPTH = 2  # parent (0) -> child (1) -> grandchild rejected (2)
```

File: tools/cronjob_tools.py (lines 1-15)
```python
"""
Cron job management tools for Hermes Agent.

Expose a single compressed action-oriented tool to avoid schema/context bloat.
"""
```

### Interactive Elements

- [x] **Data flow animation** — "You send a Telegram message: 'check the server status.'" Actors: You (📱), Telegram, Gateway, AIAgent, Terminal. Steps: (1) You → Telegram (message sent); (2) Telegram → Gateway (webhook received); (3) Gateway → AIAgent (new session started); (4) AIAgent → Terminal (runs 'uptime, df -h, ...'); (5) Terminal → AIAgent (results); (6) AIAgent → Gateway (response ready); (7) Gateway → Telegram → You (reply arrives).
- [x] **Code↔English translation** — Use the DELEGATE_BLOCKED_TOOLS snippet. Right side: "These are tools children are forbidden to use. No recursive delegation (prevents infinite army spawning). No user interaction (children work silently). No shared memory writes (prevents one child corrupting another's data). No sending messages (children can't pretend to be you)."
- [x] **Group chat animation** — Actors: User (🧑), HermesParent (🤖), Child1 (🔬), Child2 (📊). User: "Research the top 3 Python testing frameworks and compare their performance." HermesParent: "I'll delegate this to 3 parallel subagents." Child1: "Researching pytest..." Child2: "Researching unittest..." HermesParent (after): "All children complete. Combining results... Here's your comparison."
- [x] **Quiz** — 3 questions. Q1: "You want Hermes to send you a daily weather briefing at 7am even when your laptop is off. Which feature do you use?" Q2: "You asked Hermes to delegate a task and it spawned subagents. One of the subagents seems to be repeating the same mistake. Can it ask you for help?" Q3: "You want a subagent to write to the shared MEMORY.md file. Hermes refuses. Why is this a good design decision?"
- [x] **Glossary tooltips** — gateway, webhook, cron, daemon, subagent, delegation, serverless, container, terminal backend

### Reference Files to Read
- `references/content-philosophy.md` → full file
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Data Flow Animation", "Group Chat Animation", "Code↔English Translation Blocks", "Multiple-Choice Quizzes"

### Connections
- **Previous module:** "Never Forget" — showed memory and skills. This module shows the *reach* beyond the current session.
- **Next module:** "40+ Powers" — will catalog the full toolkit and explain the security system around dangerous commands.
- **Tone/style notes:** Teal accent. Module 4 uses `--color-bg-warm`. The military/ops metaphor should feel energizing, not heavy.
