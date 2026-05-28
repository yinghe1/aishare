# Module 1: The Prompt's Journey — When You Type `codex`

### Teaching Arc

- **Metaphor:** **An airport terminal.** The `codex` binary is one building; each subcommand (`exec`, `mcp-server`, `sandbox`, etc.) is a different gate that leads to a different destination. Same building, totally different journeys. (Do NOT use restaurant, factory, kitchen, or post office.)
- **Opening hook:** "You probably typed `codex` once and saw a chat box. But if you type `codex exec "fix the bug"` you get no chat — just answers piped to your terminal. Same word. Same binary. Completely different mode. How?"
- **Key insight:** Codex is a **polymorphic binary**: one executable that becomes whichever sub-program you ask for. The first thing it does — before anything model-related — is decide *which version of itself* to be.
- **"Why should I care?":** Knowing the subcommands gives you superpowers. Want to use Codex in a script? `codex exec`. Want to expose it to another agent? `codex mcp-server`. Want to test a command in a jail without running an AI at all? `codex sandbox`. Most vibe coders only ever discover the chat mode and miss the rest.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/cli/src/main.rs (lines ~99-130, the dispatcher enum)**

```rust
#[derive(Debug, clap::Subcommand)]
enum Subcommand {
    #[clap(visible_alias = "e")]
    Exec(ExecCli),               // non-interactive one-shot
    Mcp(McpCli),                 // MCP server management
    McpServer(McpServerCommand), // become an MCP server
    Sandbox(HostSandboxArgs),    // sandboxed exec wrapper
    Apply(ApplyCommand),         // git apply last diff
    Resume(ResumeCommand),       // reopen past thread
    // ... plus AppServer, Cloud, Debug, Plugin, Doctor, etc.
}
```

**File: codex-rs/README.md (lines 49-66, what the user sees on the surface)**

```text
codex exec PROMPT            # run Codex non-interactively in the terminal
codex mcp-server             # let *other* agents call Codex as an MCP tool
codex sandbox [COMMAND]...   # test a command inside the sandbox, no AI
codex --sandbox read-only    # run with read-only filesystem
codex --sandbox workspace-write
codex --sandbox danger-full-access
```

**File: AGENTS.md (lines 8-10, the arg0 trick)**

> You operate in a sandbox where `CODEX_SANDBOX_NETWORK_DISABLED=1` will be set whenever you use the `shell` tool... when you spawn a process using Seatbelt (`/usr/bin/sandbox-exec`), `CODEX_SANDBOX=seatbelt` will be set on the child process.

(For the course: mention that the same binary, when symlinked as `codex-linux-sandbox`, re-routes itself through the sandbox entrypoint — that's the "arg0 dispatch" trick. The CLI inspects its own name before parsing args.)

### Interactive Elements

- [x] **Code↔English translation** — the `Subcommand` enum snippet. Each line gets translated: "this variant means: when the user types `codex exec`, run the one-shot exec program." Use plain language about what each gate leads to.
- [x] **Pattern/Feature cards** — 6 cards, one per subcommand: `exec`, `mcp-server`, `sandbox`, `apply`, `resume`, default (TUI). Each card has an icon, the command, one-line plain-English purpose.
- [x] **Quiz** — 3 questions, scenario style:
  1. "You want to run Codex inside a shell script that fixes a build error and exits. Which subcommand?" (correct: `exec`. Wrong-answer feedback teaches the difference between interactive vs. headless.)
  2. "You want another AI tool (Claude Code, Cursor) to call Codex as if it were a tool. Which subcommand?" (correct: `mcp-server`. Teaches the client/server duality.)
  3. "You want to test whether a `rm -rf` command would be blocked by the sandbox — without launching a model. Which subcommand?" (correct: `sandbox`. Teaches that sandbox is separable from AI.)
- [x] **Flow Diagram (numbered steps)** — keystroke → arg0 dispatch → clap parses → subcommand routes → that subcommand's `run()` boots its own world (TUI vs. exec vs. MCP server). 4-5 steps.
- [x] **Group chat animation** — Save for module 2 or 3 if it doesn't fit naturally here. Optional for this module.
- [x] **Glossary tooltips** — be aggressive. Tooltip ALL of: `binary` (compiled program file), `subcommand` (a word after the main command that switches modes), `CLI` (command-line interface — typing into a terminal), `clap` (Rust library that parses command-line arguments — like a receptionist who reads your form), `enum` (a type that can be one of a fixed list of variants — like a multiple choice question), `polymorphic` (taking many forms — same name, different behavior), `MCP` (Model Context Protocol — a standard for one AI tool to call another), `headless` (no UI, just pipes input and output), `argv` / `arg0` (the array of arguments your program was launched with; `arg0` is the program's own name).

### Reference Files to Read

- `references/content-philosophy.md` → ALL (writing agent always needs content rules)
- `references/gotchas.md` → ALL (checklist before declaring done)
- `references/interactive-elements.md` → Code ↔ English Translation Blocks; Multiple-Choice Quizzes; Pattern/Feature Cards; Numbered Step Cards; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if specific tokens are unclear

### Connections

- **Previous module:** None — this is module 1. It must open with what Codex *is* in 2-3 sentences (an AI coding agent that runs locally, reads/edits your files, runs shell commands) before diving in.
- **Next module:** Module 2 (Meet the Actors). End this module by saying: "We picked the chat-mode gate — now let's walk inside and meet the people working in there."
- **Tone/style notes:** Vermillion accent. The narrator is warm and curious. The learner is smart but new to this codebase. Use "you" not "the user." Refer to the model as "the model" (not "GPT" or "the AI") because Codex is model-agnostic.
