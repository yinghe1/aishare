# Module 6: Design Lens — Why It's Built This Way

### Teaching Arc
- **Metaphor:** Evaluating software design is like reading an architect's blueprints before the building is finished. Every decision — where to put the load-bearing walls, which rooms get windows — reflects trade-offs. Understanding those trade-offs means you can advocate for changes or spot when the building is leaning.
- **Opening hook:** "Now that you understand how Hermes works, let's ask the harder question: why is it built this way? What design decisions make it uniquely powerful — and what did the engineers give up to get there? This is the module that turns you from a user into a technical partner."
- **Key insight:** Every design decision in Hermes involves a trade-off. The open model system gives flexibility but adds complexity. The learning loop gives memory but raises security risks. The terminal backend abstraction gives portability but adds latency. Knowing the trade-offs helps you make better decisions about how to use and extend Hermes.
- **"Why should I care?":** When you can articulate *why* a design is good or bad, you become a much better collaborator with AI coding agents. You can steer them toward better architectural choices — not just tell them what to build, but how.

### Screens (6)

1. **Design Win #1: Provider Agnosticism** — Why it's better: you're never locked into one AI company. You can switch from OpenAI to Claude to a local model with one command. How it's achieved: every model gets translated into the same message format (OpenAI-compatible API). Trade-off: some model-specific features (structured outputs, reasoning tokens) require special handling (`api_mode` detection). Limitation: the translation layer can fail silently when a new model has incompatible behavior.

2. **Design Win #2: The Closed Learning Loop** — Why it's better: most AI tools are stateless — every session starts from zero. Hermes compounds its knowledge. How it's achieved: Skills (SKILL.md files) + Memory (MEMORY.md/USER.md) + FTS5 session search. Trade-off: the learning loop requires active maintenance. Skills can go stale. Memory can accumulate wrong information. Limitation: there's no automatic quality control — bad memories persist unless manually removed.

3. **Design Win #3: Separation of UI from Logic** — Why it's better: the TUI (TypeScript/Ink), the Gateway (Python), and the AIAgent (Python) are fully decoupled. The agent doesn't care how it's accessed. How it's achieved: the TUI communicates via a protocol layer; the Gateway runs as a separate process. Trade-off: this separation adds complexity — three different codebases to understand and debug. Limitation: the TUI and the agent can get out of sync when one is updated without the other.

4. **Limitations Worth Knowing** — Visual callout boxes for each major limitation: (1) Memory has no automatic quality control. (2) The approval system for dangerous commands can be annoying in automated workflows. (3) Context window compression loses information — the summarized version is always less faithful than the original. (4) Skills need to be kept up to date manually. (5) Multi-modal support (vision, voice) requires optional dependencies that may not work on all platforms.

5. **Opportunities for Improvement** — What could make Hermes better? Four concrete ideas: (1) Automatic skill deprecation — detect when a skill is outdated and flag it. (2) Memory scoring — track which memories have been useful and prune ones that haven't. (3) Richer debugging tools — show the full reasoning trace, not just tool calls. (4) Declarative toolset composition — define custom toolsets in a config file without editing Python. Pattern cards showing each opportunity.

6. **The Big Picture: What It Got Right** — Step back. Hermes built something genuinely hard: a self-improving, platform-agnostic, multi-modal AI agent that runs anywhere and gets smarter over time. The design decisions reinforce each other: provider agnosticism requires the same message format, which enables the same skill system to work with any model. Security requires approval patterns, which requires knowing what tools exist, which requires the toolset system. It's a coherent design — not perfect, but coherent. Quiz.

### Code Snippets (pre-extracted)

File: agent/context_compressor.py (lines 28-53) — the compressor design philosophy
```python
SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted "
    "into the summary below. This is a handoff from a previous context "
    "window — treat it as background reference, NOT as active instructions. "
    "Do NOT answer questions or fulfill requests mentioned in this summary; "
    "they were already addressed. "
    "Your current task is identified in the '## Active Task' section of the "
    "summary — resume exactly from there. "
    "Respond ONLY to the latest user message "
    "that appears AFTER this summary."
)
```

File: hermes_cli/runtime_provider.py (lines 37-48)
```python
def _detect_api_mode_for_url(base_url: str) -> Optional[str]:
    """Auto-detect api_mode from the resolved base URL.

    Direct api.openai.com endpoints need the Responses API for GPT-5.x
    tool calls with reasoning (chat/completions returns 400).
    """
    normalized = (base_url or "").strip().lower().rstrip("/")
    if "api.x.ai" in normalized:
        return "codex_responses"
    if "api.openai.com" in normalized and "openrouter" not in normalized:
        return "codex_responses"
    return None
```

File: tools/memory_tool.py (lines 35-50) — injection scanning
```python
_MEMORY_THREAT_PATTERNS = [
    # Prompt injection
    (r'ignore\s+(previous|all|above|prior)\s+instructions', "prompt_injection"),
    (r'you\s+are\s+now\s+', "role_hijack"),
    (r'do\s+not\s+tell\s+the\s+user', "deception_hide"),
    (r'system\s+prompt\s+override', "sys_prompt_override"),
    # Exfiltration via curl/wget with secrets
    (r'curl\s+[^\n]*\$\{?\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|API)', "exfil_curl"),
    (r'cat\s+[^\n]*(\.env|credentials|\.netrc|\.pgpass)', "read_secrets"),
]
```

### Interactive Elements

- [x] **Code↔English translation** — Use the SUMMARY_PREFIX snippet. Right side: "This text is prepended to every compressed conversation summary. Notice how carefully it's worded: 'background reference, NOT active instructions' prevents the AI from re-executing old tasks. 'Do NOT answer questions mentioned in this summary' prevents ghost responses. Every word is chosen to prevent a specific failure mode."
- [x] **Quiz** — 4 questions. Q1: "You want to use a new AI model that just came out. Hermes doesn't support it yet in its model list. What's the fastest path to try it?" Q2: "Your Hermes installation has accumulated 200 memory entries over 6 months. Some are outdated. What's the limitation in how Hermes handles this?" Q3: "You're building a similar AI agent for your company. The Hermes team chose to keep Skills as plain markdown files rather than a database. What's the trade-off they made?" Q4: "Hermes compresses old conversation turns into a summary when the context fills up. What information is definitively lost in this process?"
- [x] **Pattern cards** — 4 "Opportunity" cards: 🏷️ "Skill Freshness Scoring — detect stale skills automatically", 🧹 "Memory Pruning — learn which memories actually get used", 🔍 "Reasoning Traces — expose the full thought process, not just tool calls", ⚙️ "Declarative Toolsets — define custom toolsets in config, not code"
- [x] **Glossary tooltips** — context window compression, prompt injection, provider agnosticism, API compatibility layer, declarative configuration, stateless, latency, deprecation

### Reference Files to Read
- `references/content-philosophy.md` → full file
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Code↔English Translation Blocks", "Multiple-Choice Quizzes", "Pattern Cards", "Callout Boxes"

### Connections
- **Previous module:** "40+ Powers" — cataloged the toolkit. This module explains WHY it was built that way.
- **Next module:** None — this is the final module. End with a strong call to action: "Now go build something."
- **Tone/style notes:** Teal accent. Module 6 uses `--color-bg-warm`. This module should feel like the capstone — thoughtful, honest about limitations, optimistic about opportunities. Avoid being preachy about the "right" design choices. Show trade-offs as genuinely hard decisions, not obvious mistakes.
