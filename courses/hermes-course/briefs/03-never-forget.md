# Module 3: Never Forget

### Teaching Arc
- **Metaphor:** Hermes' memory system is like a surgeon's scrub-in protocol. Before every operation, the surgeon reads the patient chart (Memory), reviews the procedure notes (Skills), and briefs the team (system prompt). The surgery starts fresh but the surgeon's knowledge doesn't.
- **Opening hook:** "Most AI chatbots forget you the moment you close the tab. Hermes doesn't. It builds a profile of who you are, what you know, how you work — and it gets better at helping you every session. Here's how."
- **Key insight:** Hermes has three memory layers that work in different ways: MEMORY.md (things it notices), USER.md (who you are), and Skills (reusable procedures). All three are loaded *before* the conversation starts, so the AI starts every session already knowing you.
- **"Why should I care?":** This is what makes Hermes feel like a real assistant rather than a stranger you have to re-explain yourself to every time. If Hermes feels dumb, it's often because memory is empty or wrong — now you'll know how to fix it.

### Screens (5)

1. **Three Kinds of Memory** — Visual: MEMORY.md (agent's notebook), USER.md (user profile), Skills (procedure library). Icon rows showing what each stores. "All three get loaded into the system prompt before every session."
2. **How MEMORY.md Works** — The frozen snapshot pattern: memory is read at session start and injected into the system prompt. Mid-session writes go to disk immediately but DON'T change the current session. They take effect *next time*. Why? Prefix cache efficiency.
3. **Skills: Reusable Superpowers** — A Skill is a SKILL.md file with frontmatter + instructions. When you invoke `/skill-name`, the full instructions load. Progressive disclosure: skill list shows just name + description (token-efficient). Full content loads on demand. Code↔English on the skills_tool.py snippet.
4. **The Skills Hub** — Skills can be installed from GitHub, official optional-skills, or agentskills.io. They're stored in `~/.hermes/skills/`. Security scanning happens before install (skills_guard). Group chat animation.
5. **Self-Improvement in Action** — After complex tasks, Hermes writes new skills from experience. The closed learning loop: task → skill creation → next task benefits. How to trigger it: "Create a skill for what you just did." Why this matters: it's like training a new employee.

### Code Snippets (pre-extracted)

File: tools/memory_tool.py (lines 1-40) — key design comments
```python
"""
Memory Tool Module - Persistent Curated Memory

Provides bounded, file-backed memory that persists across sessions. Two stores:
  - MEMORY.md: agent's personal notes and observations (environment facts, project
    conventions, tool quirks, things learned)
  - USER.md: what the agent knows about the user (preferences, communication style,
    expectations, workflow habits)

Both are injected into the system prompt as a frozen snapshot at session start.
Mid-session writes update files on disk immediately (durable) but do NOT change
the system prompt -- this preserves the prefix cache for the entire session.
The snapshot refreshes on the next session start.

Entry delimiter: § (section sign). Entries can be multiline.
"""
```

File: tools/skills_tool.py (lines 1-30) — skill directory structure comment
```python
"""
Skills Tool Module

Skills are organized as directories containing a SKILL.md file (the main instructions)
and optional supporting files like references, templates, and examples.

Inspired by Anthropic's Claude Skills system with progressive disclosure architecture:
- Metadata (name ≤64 chars, description ≤1024 chars) - shown in skills_list
- Full Instructions - loaded via skill_view when needed
- Linked Files (references, templates) - loaded on demand

Directory Structure:
    skills/
    ├── my-skill/
    │   ├── SKILL.md           # Main instructions (required)
    │   ├── references/        # Supporting documentation
    │   └── assets/            # Supplementary files
    └── category/
        └── another-skill/
            └── SKILL.md
"""
```

File: agent/context_compressor.py (lines 1-20) — why context compression exists
```python
"""Automatic context window compression for long conversations.

Uses auxiliary model (cheap/fast) to summarize middle turns while
protecting head and tail context.

Improvements over v2:
  - Structured summary template with Resolved/Pending question tracking
  - "Remaining Work" replaces "Next Steps" to avoid reading as active instructions
  - Token-budget tail protection instead of fixed message count
  - Tool output pruning before LLM summarization (cheap pre-pass)
"""
```

### Interactive Elements

- [x] **Code↔English translation** — Use the memory_tool.py docstring. Right side, line by line: "MEMORY.md is where Hermes keeps its own notes. USER.md is your profile. Both get read before any conversation starts. Writes during a session hit disk immediately — but the AI doesn't see them until next session (for speed)."
- [x] **Group chat animation** — Actors: Hermes, SkillsHub, User. Messages: User: "Can you help me set up Axolotl for fine-tuning?" Hermes: "Let me check my skills..." SkillsHub: "Found: axolotl-finetuning skill. Loading full instructions..." Hermes: "Got it. I know this procedure. Step 1: install dependencies. Let me run that." User: "How did you know all that?" Hermes: "I learned it from a previous session and saved it as a skill. Now I always know it."
- [x] **Quiz** — 3 questions. Q1: "You tell Hermes your name and preferred coding language mid-conversation. Will it remember next time? What should you do to make sure?" Q2: "You installed a skill from GitHub. Hermes seems to know some steps but misses others. Where would you look to fix it?" Q3: "After a long debugging session, Hermes offers to create a skill from what it learned. Should you say yes? Why?"
- [x] **Pattern cards** — 3 cards: Skill (📋 "Reusable procedures — like macros for complex tasks"), Memory (🧠 "Persistent notes — facts Hermes learned about your environment"), User Profile (👤 "Your preferences — how you like to work, your expertise, your goals").
- [x] **Glossary tooltips** — system prompt, prefix cache, frontmatter, YAML, progressive disclosure, context window, token, FTS5

### Reference Files to Read
- `references/content-philosophy.md` → full file
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Group Chat Animation", "Code↔English Translation Blocks", "Multiple-Choice Quizzes", "Pattern Cards"

### Connections
- **Previous module:** "The Agent Brain" — showed the loop. This module explains what's pre-loaded into the system prompt that makes the loop smarter.
- **Next module:** "The Long Arm" — will show how Hermes reaches beyond the current session to talk on Telegram, schedule tasks, and delegate to subagents.
- **Tone/style notes:** Teal accent. Module 3 uses `--color-bg` (off-white). Emphasize that memory is cumulative — each session builds on the last.
