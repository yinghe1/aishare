# Module 2: The Agent Brain

### Teaching Arc
- **Metaphor:** The agent loop is like a chess grandmaster's thinking process: look at the board (read context), decide the best move (choose a tool), make the move (run the tool), look at the new board (read result), decide again — repeat until checkmate (task complete).
- **Opening hook:** "When you ask Hermes to 'find the five fastest Python web frameworks,' it doesn't just answer from memory. It *does things* — browses, reads, compares — and the whole loop happens in seconds. Here's the engine behind that."
- **Key insight:** Modern AI agents work through a loop: think → use a tool → see the result → think again. The AI never sees the code run — it only sees text outputs. That loop is *all* the intelligence.
- **"Why should I care?":** When Hermes gets stuck in a loop or keeps calling the wrong tool, you'll know exactly where to intervene. You'll also know what kinds of tasks it can and can't do.

### Screens (5)

1. **The Loop, Demystified** — The core think→tool→result→think cycle. Animated flow diagram showing: User Message → AIAgent (think) → Tool Call → Tool Result → AIAgent (think again) → ... → Final Answer.
2. **Parallel Tool Calls** — Hermes can call multiple tools at once (like web_search + read_file simultaneously). Code shows `_PARALLEL_SAFE_TOOLS`. Explain why some tools can't run in parallel (clarify = needs user input).
3. **The Iteration Budget** — Agents have a cap (default 90 iterations). Why? Prevents infinite loops. The IterationBudget class. Subagents get their own budget (50). Code↔English translation.
4. **The Model Provider Puzzle** — Hermes works with 200+ AI models. It doesn't know or care which model you're using — it sends the same message format either way. How `runtime_provider.py` resolves which API to call.
5. **When the Loop Ends** — Three ways a conversation ends: (1) AI decides it's done, (2) iteration budget exhausted, (3) user interrupts. What to do when Hermes gets stuck.

### Code Snippets (pre-extracted)

File: run_agent.py (lines 218-231)
```python
# Tools that must never run concurrently (interactive / user-facing).
# When any of these appear in a batch, we fall back to sequential execution.
_NEVER_PARALLEL_TOOLS = frozenset({"clarify"})

# Read-only tools with no shared mutable session state.
_PARALLEL_SAFE_TOOLS = frozenset({
    "ha_get_state",
    "ha_list_entities",
    "ha_list_services",
    "read_file",
    "search_files",
    "session_search",
    "skill_view",
    "skills_list",
    "vision_analyze",
    "web_extract",
    "web_search",
})
```

File: run_agent.py (lines 185-212) — IterationBudget class
```python
class IterationBudget:
    """Thread-safe iteration counter for an agent.

    Each agent (parent or subagent) gets its own ``IterationBudget``.
    The parent's budget is capped at ``max_iterations`` (default 90).
    Each subagent gets an independent budget capped at
    ``delegation.max_iterations`` (default 50) — this means total
    iterations across parent + subagents can exceed the parent's cap.
    """

    def __init__(self, max_total: int):
        self.max_total = max_total
        self._used = 0
        self._lock = threading.Lock()

    def consume(self) -> bool:
        """Try to consume one iteration.  Returns True if allowed."""
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True
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

### Interactive Elements

- [x] **Data flow animation** — Actors: User, AIAgent, ToolRunner, Model API. Steps: (1) User sends "Find top 5 Python frameworks" → AIAgent highlighted; (2) AIAgent sends to Model API → packet animates; (3) Model API returns tool_call: web_search → packet back to AIAgent; (4) AIAgent → ToolRunner highlighted → web_search runs; (5) Result returns to AIAgent; (6) AIAgent sends result to Model API again; (7) Model produces final answer → User.
- [x] **Code↔English translation** — Use the IterationBudget snippet. Right side: "This is the agent's energy meter. Once it hits the limit, it stops even if it's mid-task. You can raise or lower this in config."
- [x] **Group chat animation** — Chat between AIAgent and Model API showing the back-and-forth of a tool-calling loop. AIAgent: "User wants top frameworks." ModelAPI: "I'll search the web — call web_search('fastest Python frameworks')." AIAgent: "Ran it. Results: [...]." ModelAPI: "Call web_search again for benchmarks." AIAgent: "Done. Here's what I found." ModelAPI: "Now I can answer: The top 5 are..."
- [x] **Quiz** — 3 questions. Q1: "Hermes has been trying to fix a bug for 45 minutes and keeps making the same mistake. What's happening and how do you fix it?" Q2: "You want Hermes to search the web and read a file at the same time. Can it? How do you know?" Q3: "The agent stops mid-task with 'iteration budget exhausted.' What does this mean and what do you tell Hermes next?"
- [x] **Glossary tooltips** — iteration, parallel execution, thread-safe, API mode, context window, tool call, provider, inference

### Reference Files to Read
- `references/content-philosophy.md` → full file
- `references/gotchas.md` → full file
- `references/interactive-elements.md` → "Data Flow Animation", "Group Chat Animation", "Code↔English Translation Blocks", "Multiple-Choice Quizzes"

### Connections
- **Previous module:** "Meet Hermes" — introduced the 6 actors. Module 2 zooms into AIAgent's inner loop.
- **Next module:** "Never Forget" — will explain how Skills and Memory feed into the loop at session start.
- **Tone/style notes:** Teal accent. Module 2 uses `--color-bg-warm` (slightly warmer off-white). The chess metaphor should be mentioned once and not overused.
