# Module 6: Memory — How a Conversation Survives

### Teaching Arc

- **Metaphor:** **A ship's logbook.** Every action — model said this, tool returned that, user typed something — is appended to the log in order, never erased. If the ship sinks (Codex crashes), the next captain reads the log to recover. When the log gets too long to read on every shift, an officer writes a *summary page* so the captain doesn't have to read the whole thing. (Do NOT reuse: restaurant, airport, ensemble, radio, locksmith, cleanroom.)
- **Opening hook:** "Close your terminal. Come back tomorrow. Type `codex resume` — and the conversation picks up exactly where you left it, with the agent remembering everything you discussed. That's not magic. That's a logbook."
- **Key insight:** Sessions are **append-only event logs** on disk (called rollouts). To recover, replay the log. When the log grows too large to fit in the model's context window, **compaction** runs a special turn that summarizes old turns and replaces them with the summary. The user's most recent message stays untouched — only the past gets squeezed.
- **"Why should I care?":** Understanding memory layers explains: why Codex "forgets" things after a long session (context window filled, compaction summary dropped detail), why `codex resume` works, why you can fork a thread (the log is a tree, not a single timeline), and why memories/skills survive across sessions while in-turn details don't.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/core/src/compact.rs (lines ~70-95, the compaction task)**

```rust
pub(crate) async fn run_inline_auto_compact_task(
    sess: Arc<Session>,
    turn_context: Arc<TurnContext>,
    initial_context_injection: InitialContextInjection,
    reason: CompactionReason,
    phase: CompactionPhase,
) -> CodexResult<()> {
    let prompt = turn_context.compact_prompt().to_string();
    let input = vec![UserInput::Text {
        text: prompt,
        text_elements: Vec::new(),
    }];

    run_compact_task_inner(
        sess,
        turn_context,
        input,
        initial_context_injection,
        CompactionTrigger::Auto,
        reason,
        phase,
    )
    .await?;
    Ok(())
}
```

**File: codex-rs/core/src/session/session.rs (lines ~19-40, what a Session holds)**

```rust
pub(crate) struct Session {
    pub(crate) conversation_id: ThreadId,
    pub(crate) installation_id: String,
    pub(super) tx_event: Sender<Event>,
    pub(super) agent_status: watch::Sender<AgentStatus>,
    pub(super) state: Mutex<SessionState>,
    pub(super) conversation: Arc<RealtimeConversationManager>,
    pub(crate) active_turn: Mutex<Option<ActiveTurn>>,
    pub(crate) input_queue: InputQueue,
    pub(super) goal_runtime: GoalRuntimeState,
    // ...
}
```

(Notice: a Session bundles the conversation ID, the event channel, the current turn, the input queue. It's the in-memory shape of one conversation.)

**Rollout file shape — for plain-English illustration (not actual code):**

```text
~/.codex/threads/2026-05-27/{thread_id}/rollout.jsonl

{"type":"TurnStarted","timestamp":...}
{"type":"UserMessage","text":"fix the failing test"}
{"type":"AgentMessage","text":"Looking at the test file first..."}
{"type":"FunctionCall","tool":"shell","args":{"cmd":"pnpm test"}}
{"type":"FunctionResult","output":"error in src/parser.ts line 47..."}
{"type":"FunctionCall","tool":"apply_patch","args":{...}}
{"type":"FunctionResult","output":"patch applied"}
{"type":"AgentMessage","text":"Done. The typo was on line 47."}
{"type":"TurnEnded","timestamp":...}
```

Each line is one event. Append-only. Easy to read, easy to resume.

### Interactive Elements

- [x] **Numbered Step Cards (the lifecycle of a session)** — 5 step cards:
  1. **Session starts** — A `ThreadId` is minted; a new `rollout.jsonl` file is opened on disk.
  2. **Each turn appends events** — User message, model output, function calls, function results — every event is written to disk as it happens.
  3. **Context window fills up** — Token counter detects the prompt is getting close to the model's limit.
  4. **Compaction kicks in** — A special turn runs: "summarize the old history." The summary replaces those old turns in the prompt; the rollout file still has the raw events.
  5. **Resume later** — `codex resume` reads the rollout file, rebuilds the session in memory, and you continue.
- [x] **Code↔English translation (first)** — the `Session` struct snippet. Each field translated: "conversation_id: a unique ID for this chat — like a file name." "tx_event: the wire that carries events out to the UI." "active_turn: the in-progress turn if there is one, otherwise nothing." Emphasize: *this is everything one conversation needs to be itself.*
- [x] **Code↔English translation (second)** — the `run_inline_auto_compact_task` function. Plain English: "Build a prompt that says: 'summarize everything above this point.' Run it as a special turn — same machinery as any other turn, but the answer is the summary itself. Inject the summary into the conversation history. Resume the original task."
- [x] **Message Flow / Data Flow Animation** — Actors: `flow-actor-1` Memory (rollout file on disk), `flow-actor-2` Session (in-memory state), `flow-actor-3` Compactor, `flow-actor-4` Context Window (the model's mouth — how much it can swallow). NO apostrophes in labels — use "lots of turns" not "lots of turns."

  Steps:
  1. `{"highlight":"flow-actor-2","label":"Each new turn appends events to the session"}`
  2. `{"highlight":"flow-actor-1","label":"Events also append to the rollout file on disk","packet":true,"from":"actor-2","to":"actor-1"}`
  3. `{"highlight":"flow-actor-2","label":"Many turns later — history is large"}`
  4. `{"highlight":"flow-actor-4","label":"Context window is near full — the model cannot swallow more","packet":true,"from":"actor-2","to":"actor-4"}`
  5. `{"highlight":"flow-actor-3","label":"Compactor runs — asks the model to summarize old turns","packet":true,"from":"actor-2","to":"actor-3"}`
  6. `{"highlight":"flow-actor-2","label":"Summary replaces the old turns in the in-memory history","packet":true,"from":"actor-3","to":"actor-2"}`
  7. `{"highlight":"flow-actor-1","label":"Original rollout on disk is untouched — full history preserved"}`
  8. `{"highlight":"flow-actor-2","label":"Conversation continues — model has room again"}`
- [x] **Callout box (1)** — "Aha! moment: **the disk log and the model's view are two different things**. The rollout file always has the complete history. The model sees a smaller view that fits its context window. Compaction is what bridges the gap. This is why you can `codex resume` and find perfect recall — even when the model itself only remembers a summary."
- [x] **Callout box (2)** — "Aha! moment: **append-only is a superpower**. Because the log only grows (never edits or deletes), you can fork it (start a side thread from any point), replay it (debug what happened), or rebuild from it (recover from a crash). Engineers call this **event sourcing** — and it's the same trick git uses for your commits."
- [x] **Pattern/Feature cards (the three layers of memory)** — 3 cards:
  - **In-turn (live)** — The active turn's tool outputs, model tokens, current input queue. Disappears when the turn ends if not promoted.
  - **In-session (rollout)** — Everything in the current conversation, on disk as `rollout.jsonl`. Survives crashes. Resumable via `codex resume`.
  - **Across sessions (memories / skills)** — Long-term notes the agent writes to `~/.codex/memories/` and skills configured in user / project scope. Survive across all sessions.
- [x] **Quiz** — 3 questions, scenario / decision style:
  1. "You had a 3-hour session yesterday. Today you `codex resume` and ask 'what did we decide about the database schema?' Codex answers correctly. Did the model 'remember' three hours of conversation directly?" (Correct: No — it replayed the rollout file and re-built its view. The model itself has no persistent memory; the system around it does. Teaches the disk-vs-context distinction.)
  2. "You notice that mid-way through a long conversation, the agent suddenly forgets a detail you mentioned an hour ago. What probably happened?" (Correct: compaction summarized that section of history and the summary dropped the specific detail. Suggested fix: lift the detail into a memory or into the latest user message. Teaches: compaction is lossy.)
  3. "You want to test a risky idea without polluting your main conversation. What does the system give you?" (Correct: fork into a side thread — same rollout history up to a point, then a new branch. Teaches: append-only logs naturally support branching.)
- [x] **Glossary tooltips** — aggressive: `rollout` (in Codex terms, the persisted append-only event log for one session — a JSONL file on disk), `JSONL` (JSON Lines — a file format where each line is its own JSON object — easy to append, easy to stream), `append-only` (a data structure you can only add to, never edit or delete in place), `compaction` (replacing a long stretch of history with a shorter summary so it still fits the context window), `context window` (the maximum amount of text a model can read in one go — like the model's working memory), `thread` / `ThreadId` (in Codex, a conversation; the ID is the conversation's unique name), `fork` (start a new conversation that shares history with an existing one up to a branching point), `event sourcing` (storing state as a sequence of events instead of as a current snapshot), `mutex` (a lock that lets only one piece of code touch shared data at a time — like a "do not disturb" sign).

### Reference Files to Read

- `references/content-philosophy.md` → ALL
- `references/gotchas.md` → ALL (especially: NO apostrophes in `data-steps` JSON!)
- `references/interactive-elements.md` → Numbered Step Cards; Code ↔ English Translation Blocks; Message Flow / Data Flow Animation; Pattern/Feature Cards; Multiple-Choice Quizzes; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if needed

### Connections

- **Previous module:** Module 5 ended with: "How does Codex remember? Last module." Open by answering it.
- **Next module:** None — this is the finale. End with a short capstone paragraph that walks the learner back through the journey: gate → cast → turn loop → tools → sandbox → memory. Then invite them to fire up `codex` and notice the parts they now know are there.
- **Tone/style notes:** This is the warmest, most reflective module. End on a confident note: "you can now read this codebase. You can also direct AI tools that work the same way (Claude Code, Cursor). The shape is the shape." Vermillion accent.
