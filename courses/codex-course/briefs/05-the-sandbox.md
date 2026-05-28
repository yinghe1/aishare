# Module 5: The Sandbox — Why Codex Doesn't Wreck Your Machine

### Teaching Arc

- **Metaphor:** **A glass-walled cleanroom in a chip factory.** The agent works inside the cleanroom. It can see out (read files outside the workspace), but contaminants can't leave (writes outside, network calls without permission). Each operating system has its own brand of cleanroom — Apple's, Linux's, Microsoft's — but they all do the same job. (Do NOT reuse: restaurant, airport, ensemble, radio, locksmith.)
- **Opening hook:** "Codex runs shell commands. Real ones. On your real machine. Have you ever wondered why there aren't a million horror stories of agents deleting people's home directories? Because of this layer."
- **Key insight:** The sandbox is **enforced by the operating system, not the agent**. The agent doesn't "behave well" — it literally *cannot* misbehave because the kernel refuses. Three OS-specific technologies, one unified policy abstraction in code: read-only, workspace-write, danger-full-access.
- **"Why should I care?":** This is your single most important config choice. Default workspace-write gets work done without exposing your homedir. Read-only is for "let it explore but don't let it write." Full-access is the rare break-glass option. If you don't pick deliberately, the default picks for you — and "the agent can't write here" debugging often traces back to a sandbox boundary, not a bug.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/core/src/landlock.rs (lines ~22-50, spawning a sandboxed Linux process)**

```rust
pub async fn spawn_command_under_linux_sandbox<P>(
    codex_linux_sandbox_exe: P,
    command: Vec<String>,
    command_cwd: AbsolutePathBuf,
    permission_profile: &PermissionProfile,
    sandbox_policy_cwd: &AbsolutePathBuf,
    use_legacy_landlock: bool,
    stdio_policy: StdioPolicy,
    network: Option<&NetworkProxy>,
    env: HashMap<String, String>,
) -> std::io::Result<Child> {
    let network_sandbox_policy = permission_profile.network_sandbox_policy();
    let args = create_linux_sandbox_command_args_for_permission_profile(
        command,
        command_cwd.as_path(),
        permission_profile,
        sandbox_policy_cwd,
        use_legacy_landlock,
        allow_network_for_proxy(/*enforce_managed_network*/ false),
    );
    // ... spawn the child with arg0 dispatch
}
```

**File: codex-rs/core/src/windows_sandbox.rs (lines ~30-47, picking the right Windows level)**

```rust
impl WindowsSandboxLevelExt for WindowsSandboxLevel {
    fn from_config(config: &Config) -> WindowsSandboxLevel {
        match config.permissions.windows_sandbox_mode {
            Some(WindowsSandboxModeToml::Elevated) => WindowsSandboxLevel::Elevated,
            Some(WindowsSandboxModeToml::Unelevated) => WindowsSandboxLevel::RestrictedToken,
            None => Self::from_features(&config.features),
        }
    }
}
```

**File: codex-rs/README.md (lines ~78-86, the user-facing sandbox flags)**

```text
codex --sandbox read-only           # default — explore freely, can't write
codex --sandbox workspace-write     # write inside the project, no network
codex --sandbox danger-full-access  # break glass — only inside containers
```

### Interactive Elements

- [x] **Pattern/Feature cards (the three sandbox levels)** — 3 large cards, each with an icon, color, and 2-3 line description:
  - **`read-only`** (green) — Can read any file, can't write anything, no network. Safest. Use when you want the agent to explore and propose, not act.
  - **`workspace-write`** (amber) — Can read anything; can write inside the workspace folder only; no network unless allowed. The default. Best for most coding work.
  - **`danger-full-access`** (red) — No filesystem or network restrictions. Reserve for inside Docker / VMs. The README literally calls it "Danger!"
- [x] **Pattern/Feature cards (the three sandbox technologies)** — 3 cards, one per OS:
  - **macOS — Seatbelt (`sandbox-exec`)** — Apple's macOS profile language describes what's allowed; the kernel enforces it. When a sandboxed child runs, `CODEX_SANDBOX=seatbelt` is set so test code can detect the cage.
  - **Linux — Landlock + bubblewrap** — Landlock is a Linux kernel feature that restricts which paths a process can write. A helper binary (`codex-linux-sandbox`) wraps the actual command.
  - **Windows — Restricted Token / Job Objects** — Two modes (`Elevated`, `RestrictedToken`) controlled by Windows access tokens, the OS's mechanism for "this process has fewer permissions than you do."
- [x] **Code↔English translation** — the Windows sandbox `match` snippet (or the Linux spawn function, but the Windows one is shorter and more legible). Each line in English: "Config says Elevated? Use the elevated cage. Config says Unelevated? Use the restricted-token cage. No config? Pick based on feature flags." Emphasize: *the abstraction layer hides the OS — the rest of Codex just says 'spawn this command sandboxed.'*
- [x] **Group Chat Animation** — Actors: Model, Core, Sandbox (Linux/Mac/Windows pick one), Kernel. Show a denied operation:
  1. Model → Core: "Run this shell: `rm -rf ~`."
  2. Core → Sandbox: "Approved by policy. Spawn under workspace-write."
  3. Sandbox → Kernel: "Run rm with these path restrictions."
  4. Kernel → Sandbox: "Denied — write attempt outside allowed paths."
  5. Sandbox → Core: "Process exited with error: permission denied."
  6. Core → Model: "Output: rm: cannot remove ... — permission denied."
  7. Model → Core: "Acknowledged. Trying a safer approach."
- [x] **Callout box** — "Aha! moment: the sandbox does not trust the agent — it trusts the **operating system**. Even if the model is malicious or buggy, even if the tool runtime has a bug, the kernel still refuses the syscall. The safety isn't a check the agent runs; it's a wall it can't see through. This is called **defense in depth**."
- [x] **Permission/Config Badges** — small visual list of sandbox-relevant env vars and flags:
  - `CODEX_SANDBOX=seatbelt` — Set inside Seatbelt'd processes. Test code uses this to skip tests that need to spawn a sandbox (you can't nest Seatbelt).
  - `CODEX_SANDBOX_NETWORK_DISABLED=1` — Set when network is blocked. Tests use this to skip network calls.
  - `--sandbox <level>` — CLI flag overriding the configured default.
  - `[permissions]` in `config.toml` — The persistent way to set the default level per machine or per project.
- [x] **Quiz** — 3 questions, scenario / debugging style:
  1. "Codex says it edited a file, the message in the chat looks normal, but you check the file on disk and it didn't change. What is most likely?" (Correct: a sandbox denial that wasn't surfaced — check sandbox logs or the agent's recent tool outputs. Wrong-answer teaches that "the model lying" is rarely the issue; usually a deeper layer said no.)
  2. "You run Codex inside a Docker container that is itself the security boundary. Should you use `read-only`, `workspace-write`, or `danger-full-access`?" (Correct: `danger-full-access` is reasonable here because the container is the cage; layering Codex's sandbox inside is mostly friction with little added safety. Discussion teaches *defense in depth vs. friction*.)
  3. "Why does Codex set `CODEX_SANDBOX=seatbelt` on child processes?" (Correct: so code running *inside* the sandbox can detect that it's caged — useful for tests that need to skip operations the sandbox would block. Teaches: introspectable sandboxing.)
- [x] **Glossary tooltips** — aggressive: `kernel` (the deepest layer of an operating system — the part that actually talks to hardware and decides which programs can do what), `syscall` (a request a program makes to the kernel — like "open this file" or "send this network packet"), `Seatbelt` (Apple's macOS sandbox; the underlying binary is `sandbox-exec`), `Landlock` (a Linux kernel feature for restricting filesystem access per-process), `bubblewrap` (a Linux tool that runs commands in tight namespaces), `restricted token` (a Windows access token with fewer permissions than the user normally has), `permission profile` (Codex's internal data structure describing what a session is allowed to do), `defense in depth` (security strategy where multiple independent layers each block bad behavior — if one fails, the next still holds), `env var` (an environment variable — a setting that lives in the process's environment, not in any file), `Docker container` (a sandboxed Linux environment that looks like its own little computer).

### Reference Files to Read

- `references/content-philosophy.md` → ALL
- `references/gotchas.md` → ALL
- `references/interactive-elements.md` → Pattern/Feature Cards; Code ↔ English Translation Blocks; Group Chat Animation; Permission/Config Badges; Multiple-Choice Quizzes; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if needed

### Connections

- **Previous module:** Module 4 ended with: "Approval is one filter. What about the sandbox?" Open by answering it.
- **Next module:** Module 6 (Memory & Sessions). End with: "We have an agent, a turn loop, tools, and a sandbox. But conversations are long — and the model's memory is finite. How does Codex remember? Last module."
- **Tone/style notes:** This is a confidence-building module — the learner should walk away feeling "OK, even if the AI goes haywire, the OS stops it." Don't downplay the danger — but emphasize that the protection is real and enforced. The cleanroom metaphor is the centerpiece. Vermillion accent.
