# Module 2: Meet the Actors — The Cast Inside Codex

### Teaching Arc

- **Metaphor:** **A jazz ensemble.** Each musician has one instrument and one job; the conductor (the turn loop, coming in Module 3) cues them in. The whole sound comes from the interplay — no single player makes the music. (Do NOT reuse: restaurant, airport from M1, post office, factory.)
- **Opening hook:** "We walked through the chat-mode gate. Inside, five characters are doing the work — and once you know their names, the whole codebase stops looking like a wall of folders."
- **Key insight:** Codex is a **federation of crates**, not a monolith. The TUI doesn't call the model. The core doesn't draw your screen. They talk to each other through **events on a channel** — like musicians watching the conductor's baton, not whispering to each other.
- **"Why should I care?":** When something breaks, this map tells you who to blame. UI frozen but the agent kept editing? TUI's stuck, core is fine. File written but no message in chat? Core finished, event didn't reach TUI. Sandbox denied? That's the safety actor, not the model.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/tui/src/app_event.rs (lines ~136-150, the contract between UI and engine)**

```rust
#[allow(clippy::large_enum_variant)]
#[derive(Debug)]
pub(crate) enum AppEvent {
    /// Open the agent picker for switching active threads.
    OpenAgentPicker,
    /// Switch the active thread to the selected agent.
    SelectAgentThread(ThreadId),

    /// Fork the current thread into a transient side conversation.
    StartSide {
        parent_thread_id: ThreadId,
        user_message: Option<UserMessage>,
    },
    /// Submit an op to the specified thread, regardless of current focus.
    // ...
}
```

**File: codex-rs/README.md (lines 92-99, the official cast description)**

```text
core/   — the business logic for Codex (the engine)
exec/   — "headless" CLI for use in automation
tui/    — fullscreen TUI built with Ratatui
cli/    — multitool that provides the above via subcommands
```

**File: codex-rs/core/src/lib.rs (lines 1-7, the core's self-discipline)**

```rust
//! Root of the `codex-core` library.

// Prevent accidental direct writes to stdout/stderr in library code. All
// user-visible output must go through the appropriate abstraction (e.g.,
// the TUI or the tracing stack).
#![deny(clippy::print_stdout, clippy::print_stderr)]
```

(Teaching note: the `#![deny(...)]` line is gold — the core *enforces* the separation by refusing to compile if anyone tries to `println!` from inside it. That's not a guideline, it's a wall.)

### Interactive Elements

- [x] **Visual File Tree** — show `codex-rs/` with the 4 main crates: `cli/`, `tui/`, `core/`, `exec/`, plus 2-3 supporting ones: `apply-patch/`, `mcp-server/`, `linux-sandbox/`. Each gets a one-line plain-English description.
- [x] **Icon-Label Rows (the cast)** — 5 icon rows, one per actor:
  1. **The Receptionist (`cli/`)** — Reads what you typed and decides which Codex to be.
  2. **The Stage Manager (`tui/`)** — Draws the chat box, captures keystrokes, displays streamed messages. Does NOT call the model.
  3. **The Conductor (`core/`)** — Runs the turn loop, talks to the model, dispatches tool calls. Does NOT draw a single pixel.
  4. **The Stagehand (`exec/`)** — Same engine as the conductor, but pipes results to plain stdout — used by automation.
  5. **The Bouncer (sandbox crates)** — `linux-sandbox/`, `windows-sandbox-rs/`, plus seatbelt code in core. Sits between the model's commands and your operating system.
- [x] **Code↔English translation** — the `AppEvent` enum snippet. Each variant explained: "This event means: open the agent-picker UI." "This means: please run this user message as a turn." Highlight that it's a *list of every possible thing the UI can ask the engine to do.*
- [x] **Callout box** — "Aha! moment: the `#![deny(print_stdout)]` line is a hard wall. The core *cannot* print to your terminal even if someone forgets. Every word you see in the chat had to be sent as an event. Engineers call this **separation of concerns** — give each piece one job, and one job only."
- [x] **Quiz** — 3 questions, scenario style:
  1. "The agent successfully edits a file (you can see the file changed on disk), but no confirmation appears in the chat. Where do you look first?" (Correct: TUI side — the engine did its job; the message didn't render. Wrong-answer teaches the direction of the breakage.)
  2. "You want to add a new keyboard shortcut that triggers a fork into a side conversation. Which crate gets the new code?" (Correct: `tui` — keyboard input lives there. Discussion: but the shortcut emits an `AppEvent::StartSide` which `core` handles. So the wiring lives in both.)
  3. "Why does `codex-core` deny `println!`?" (Correct: so user-visible output can't sneak past the TUI. Teaches: enforced architecture > polite convention.)
- [x] **Glossary tooltips** — aggressive: `crate` (a Rust library — like a self-contained box of code other boxes can depend on), `monolith` (one giant blob of code where everything depends on everything else — the opposite of modular), `event` (a small message describing something that happened), `channel` (a queue where one part of the program writes messages and another reads them — like a conveyor belt), `enum variant` (one of the possible "shapes" an enum can take — like one face of a die), `clippy` (Rust's built-in linter — a strict editor that catches sloppy code), `lint` (a warning from a tool about code style or potential bugs), `Ratatui` (a Rust library for drawing UIs in the terminal using boxes and text), `stdout` / `stderr` (the two output streams every command-line program has — stdout for normal output, stderr for errors).

### Reference Files to Read

- `references/content-philosophy.md` → ALL
- `references/gotchas.md` → ALL
- `references/interactive-elements.md` → Visual File Tree; Icon-Label Rows; Code ↔ English Translation Blocks; Multiple-Choice Quizzes; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if needed

### Connections

- **Previous module:** Module 1 ended with "we picked the chat-mode gate." Open by saying: "Now we're inside. Let's meet the cast."
- **Next module:** Module 3 (The Turn Loop). End with: "Five actors, none of them in charge alone. So who conducts the music? That's next — the loop that drives every conversation."
- **Tone/style notes:** Keep the ensemble metaphor running throughout this module. Refer back to specific actors by their character name in later text. Vermillion accent. The icon-label rows are the visual centerpiece — make them memorable.
