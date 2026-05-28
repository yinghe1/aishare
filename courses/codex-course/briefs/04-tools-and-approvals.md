# Module 4: Tools — How the Agent Touches the World

### Teaching Arc

- **Metaphor:** **A locksmith with a keyring.** The model is a locksmith standing outside your house. It can't just walk in — it has to pick a key (a tool) and ask permission to use it. Some keys open anywhere (read a file). Some need a homeowner's nod (edit a file). Some doors are bolted shut and no key works (writes outside the workspace under read-only mode). (Do NOT reuse: restaurant, airport, ensemble, radio.)
- **Opening hook:** "When you ask Codex to 'rename this variable,' the model doesn't reach into your filesystem. It writes a request: *please use the `apply_patch` tool with this diff*. Then someone — you, or a policy — decides whether the key turns."
- **Key insight:** Tools are **named contracts**. Every action the model takes is one of a small list of named tools with JSON arguments. Approval is **layered**: first the permission profile decides, then the safety check decides, then maybe you decide. Three filters before a key turns.
- **"Why should I care?":** The most powerful config knob you have. Tell Codex `--ask-for-approval never` and you're handing it the keyring. Tell it `on-request` and it asks every time. Picking the right level for the task = the difference between productive and paranoid. Recognizing the `apply_patch` heredoc protocol lets you spot when an LLM is hallucinating a file edit.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/core/src/apply_patch.rs (lines ~13-31, the safety-check return type)**

```rust
pub(crate) enum InternalApplyPatchInvocation {
    /// The `apply_patch` call was handled programmatically, without any sort
    /// of sandbox, because the user explicitly approved it. This is the
    /// result to use with the `shell` function call that contained `apply_patch`.
    Output(Result<String, FunctionCallError>),

    /// The `apply_patch` call was approved, either automatically or explicitly.
    /// The runtime realizes the patch through the selected environment filesystem.
    DelegateToRuntime(ApplyPatchRuntimeInvocation),
}

#[derive(Debug)]
pub(crate) struct ApplyPatchRuntimeInvocation {
    pub(crate) action: ApplyPatchAction,
    pub(crate) auto_approved: bool,
    pub(crate) exec_approval_requirement: ExecApprovalRequirement,
}
```

**File: codex-rs/core/src/apply_patch.rs (lines ~33-74, the three-way safety check)**

```rust
match assess_patch_safety(
    &action,
    turn_context.approval_policy.value(),
    &turn_context.permission_profile(),
    file_system_sandbox_policy,
    &action.cwd,
    turn_context.windows_sandbox_level,
) {
    SafetyCheck::AutoApprove { .. } => /* run it */,
    SafetyCheck::AskUser => /* show approval card to user */,
    SafetyCheck::Reject { reason } => /* tell the model: nope, denied */,
}
```

**The apply_patch heredoc protocol (the elegant hack)** — explain in prose, not code:

The model emits a regular bash command that *embeds* a unified diff inside a heredoc:

```bash
apply_patch <<'EOF'
*** Begin Patch
*** Update File: src/parser.ts
@@
-  const valeu = config.value;
+  const value = config.value;
*** End Patch
EOF
```

Codex parses the heredoc using a real bash parser (tree-sitter), validates the patch format, and applies it atomically. Why this is elegant: (a) the model gets to reason about its edit textually, (b) it looks like a normal shell command, so the same approval pipeline handles it, (c) shell escaping does the hard quoting work.

### Interactive Elements

- [x] **Code↔English translation (first)** — the `InternalApplyPatchInvocation` enum. Each variant explained: "Variant 1: we already ran it ourselves and here is the output." "Variant 2: hand it to the runtime, which will use the right sandbox."
- [x] **Code↔English translation (second)** — the `match assess_patch_safety(...)` block. Three arms, three English lines: "Auto-approve: just do it." "Ask the user: show them the approval card." "Reject: send a denial back to the model so it can adjust."
- [x] **Pattern/Feature cards** — the tools available to the model (4-6 cards):
  - **`shell`** — Run a command in the workspace.
  - **`apply_patch`** — Edit one or more files atomically via a unified diff.
  - **`read_file`** — Get the contents of a file. (May be combined with shell `cat` in practice.)
  - **`web_search`** — Look something up on the open internet.
  - **MCP tools** — Tools provided by external MCP servers you wired up (custom integrations).
  - **(optional)** — image generation, codebase search, etc.
- [x] **Permission/Config Badges** — the three approval policies:
  - `never` — auto-approve everything; the model can run anything matching its sandbox policy.
  - `on-request` — every tool call shows you a card; you click Allow/Deny.
  - `unless-trusted` — auto-approve if the command's "shape" is on a trusted list; otherwise ask.
- [x] **Group Chat Animation (optional but encouraged)** — Actors: Model, Safety Checker, You (the user). Show one approval round:
  1. Model → Safety Checker: "Please run `rm -rf node_modules`."
  2. Safety Checker → You: "The model wants to delete node_modules. Allow?"
  3. You → Safety Checker: "Allow this once."
  4. Safety Checker → Model: "OK. Output: removed 1,247 files."
  (Avoid apostrophes if used inside data-steps; this is a chat block so HTML, not JSON — apostrophes are fine here.)
- [x] **Quiz** — 3 questions, debugging / decision style:
  1. "You set approval policy to `never` and Codex still refuses to write outside your project folder. What is blocking it?" (Correct: the sandbox filesystem policy — a separate layer below approval. Teaches: approval and sandbox are two filters, not one.)
  2. "The model emits an `apply_patch` heredoc that fails to parse. What does Codex do?" (Correct: returns a parse-error string as the tool output, the model sees it on the next loop iteration and can retry. Wrong-answer teaches that errors are *feedback*, not crashes.)
  3. "You want your AI assistant to fix a TypeScript build error fully autonomously without prompting you 14 times. Which approval policy?" (Correct: `never` (paired with a tight sandbox). Discussion: never doesn't mean "no safety" — the sandbox still constrains the agent.)
- [x] **Callout box** — "Aha! moment: **errors flow back as feedback**. When a tool fails, Codex doesn't crash or panic. It hands the error string to the model as the next 'tool output.' The model reads it like any other piece of context and figures out what to do next. Engineers call this **failing forward** — every error is information."
- [x] **Glossary tooltips** — aggressive: `tool` (a named action the model is allowed to ask for — like a verb the model can use), `function call` (the model emitting a JSON object asking for a tool), `heredoc` (a bash trick for embedding multi-line text inside a single command — the `<<EOF ... EOF` thing), `unified diff` (the standard format for describing edits — minus lines for removed, plus lines for added), `atomic` (all-or-nothing — either every change applies or none of them do), `tree-sitter` (a fast, robust parser library used to understand code structure), `MCP` (Model Context Protocol — the standard for plugging tools into AI agents), `sandbox policy` (rules about which files and network the agent is allowed to touch), `approval policy` (rules about when the agent has to ask you before acting).

### Reference Files to Read

- `references/content-philosophy.md` → ALL
- `references/gotchas.md` → ALL
- `references/interactive-elements.md` → Code ↔ English Translation Blocks; Pattern/Feature Cards; Permission/Config Badges; Group Chat Animation; Multiple-Choice Quizzes; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if needed

### Connections

- **Previous module:** Module 3 ended with: "The model 'called a tool.' What does that even mean?" Open by answering it.
- **Next module:** Module 5 (The Sandbox). End with: "Approval is one filter. But what if the model — or a bug in a tool — tries to do something even the policy missed? That's where the sandbox steps in. Next module."
- **Tone/style notes:** Lean on the locksmith metaphor. The heredoc explanation is the showpiece — give it room. Vermillion accent.
