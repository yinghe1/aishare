# Module 3: The Turn Loop — How a Question Becomes an Answer

### Teaching Arc

- **Metaphor:** **A two-way radio (ham radio) conversation.** You press the button and speak (the prompt). The other person starts replying *while still thinking* — broadcasting word by word (streaming). You can break in anytime (input queue / cancellation). Sometimes they pause to look something up (tool call) before continuing. The call doesn't end until one of you says "over and out." (Do NOT reuse: restaurant, airport, ensemble.)
- **Opening hook:** "You ask Codex to 'fix the failing test.' Sometimes the answer arrives in 5 seconds; sometimes it grinds for 5 minutes, editing files, running commands, thinking again. Why the difference? Because under the surface, that one prompt isn't one round-trip — it's a loop."
- **Key insight:** A **turn** is a loop, not a single call. The model says something, then the loop asks: *was that final, or does the model want to run a tool?* If it wanted a tool, run it, send the result back, ask the model again. Repeat until the model says "I'm done."
- **"Why should I care?":** Every "AI is hallucinating," "AI is stuck in a bug loop," and "why is this so slow" question maps to this loop. Knowing it lets you predict and intervene: cancel mid-stream, queue a clarification, or set a turn-step limit.

### Code Snippets (pre-extracted — use verbatim)

**File: codex-rs/core/src/client_common.rs (lines ~68-87, the streaming primitive)**

```rust
pub struct ResponseStream {
    pub(crate) rx_event: mpsc::Receiver<Result<ResponseEvent>>,
    pub(crate) consumer_dropped: CancellationToken,
}

impl Stream for ResponseStream {
    type Item = Result<ResponseEvent>;
    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        self.rx_event.poll_recv(cx)
    }
}
```

**File: codex-rs/core/src/session/turn.rs (lines ~1768-1777, what happens when the radio cuts out)**

```rust
let event = match event {
    Some(Ok(event)) => event,
    Some(Err(err)) => break Err(err),
    None => {
        break Err(CodexErr::Stream(
            "stream closed before response.completed".into(),
            None,
        ));
    }
};
```

**File: codex-rs/core/src/session/turn.rs (paraphrase of the loop ~lines 216-310, for the English side of the translation)**

The sampling loop, in pseudocode:

```
loop {
  // 1. Pick up any new user input that arrived while we were thinking
  pending_input = drain_input_queue();

  // 2. Build the prompt: history + tools + personality
  prompt = build_prompt_from_history();

  // 3. Open a stream to the model and start receiving events
  stream = client.stream(prompt, model_info).await;

  // 4. Pull events one by one until the stream ends
  while let Some(event) = stream.next().await {
    handle(event);  // could be a text token, a function call, etc.
  }

  // 5. Did the model finish, or does it want to run a tool and continue?
  if !needs_follow_up { break; }
}
```

(For the writing agent: format this as a code↔English block. Don't try to use the verbatim 200-line implementation — this distilled view of the loop *is* the teaching artifact, paired with the English on the right.)

### Interactive Elements

- [x] **Message Flow / Data Flow Animation (REQUIRED)** — this module is the natural home. Actors: `flow-actor-1` You (the user), `flow-actor-2` TUI, `flow-actor-3` Core (turn loop), `flow-actor-4` OpenAI model, `flow-actor-5` Tools.

  Steps (use `data-steps='[...]'` with NO apostrophes in labels — write "user input" not "user's input"):
  1. `{"highlight":"flow-actor-1","label":"You type Fix the failing test and press Enter"}`
  2. `{"highlight":"flow-actor-2","label":"TUI captures the keystroke, wraps it in an AppEvent","packet":true,"from":"actor-1","to":"actor-2"}`
  3. `{"highlight":"flow-actor-3","label":"Core builds the prompt: history plus tools plus personality","packet":true,"from":"actor-2","to":"actor-3"}`
  4. `{"highlight":"flow-actor-4","label":"Core opens a stream to the model","packet":true,"from":"actor-3","to":"actor-4"}`
  5. `{"highlight":"flow-actor-3","label":"Model streams text tokens back, one at a time","packet":true,"from":"actor-4","to":"actor-3"}`
  6. `{"highlight":"flow-actor-2","label":"TUI shows each token as it arrives — you see typing, not waiting","packet":true,"from":"actor-3","to":"actor-2"}`
  7. `{"highlight":"flow-actor-4","label":"Model decides it needs to read a file — emits a function call"}`
  8. `{"highlight":"flow-actor-5","label":"Core dispatches the tool call to the tools runtime","packet":true,"from":"actor-3","to":"actor-5"}`
  9. `{"highlight":"flow-actor-3","label":"Tool result goes back into the conversation","packet":true,"from":"actor-5","to":"actor-3"}`
  10. `{"highlight":"flow-actor-4","label":"Loop continues — model gets the result and responds again","packet":true,"from":"actor-3","to":"actor-4"}`
  11. `{"highlight":"flow-actor-1","label":"Model says I am done — loop exits — answer is final"}`

- [x] **Group Chat Animation (REQUIRED)** — this is the natural module for the chat too, because the conversation between Core and the Model literally is a chat. Actors: **Core** and **Model**. Use `var(--color-actor-1)` for Core, `var(--color-actor-2)` for Model. Messages (no apostrophes — replace "let's" with "lets" or rephrase):

  1. Core → Model: "Here is the conversation so far plus the new user message: Fix the failing test."
  2. Model → Core: "I need to look at the test file first." *(emits function call: shell)*
  3. Core → Model: "Output of `pnpm test`: error in src/parser.ts line 47, undefined variable."
  4. Model → Core: "Now I want to read src/parser.ts." *(function call: shell with cat)*
  5. Core → Model: "Here are the contents." *(file contents)*
  6. Model → Core: "Applying this patch to fix the typo." *(function call: apply_patch)*
  7. Core → Model: "Patch applied. Tests re-ran — all passing."
  8. Model → Core: "Done. The typo on line 47 was the cause."

- [x] **Code↔English translation** — use the pseudo-code loop block above (Step 5 of the snippets). Each numbered comment on the right side. Plain English emphasizes "this is a *loop* — most users think it is one call."
- [x] **Callout box (1)** — "Aha! moment: **streaming**. You see text appearing letter by letter not because of an animation. The model is *literally* sending tokens one at a time over a network connection, and the TUI is rendering each one the moment it arrives. The 'typing' effect is real — and you can interrupt mid-stream."
- [x] **Callout box (2)** — "Aha! moment: **the loop ends when the model says so**. There is no hard-coded turn limit. The model decides when its answer is final. That is why a complex task can run for many round-trips — and why setting a max-turns config matters when you want to bound runaway behavior."
- [x] **Quiz** — 3 questions, scenario / debugging style:
  1. "You ask Codex 'rename `foo` to `bar` across the project.' It edits 17 files over 4 minutes. How many times did the model actually get called?" (Correct: roughly once per tool round — many times, not one. Explanation teaches the loop.)
  2. "Mid-stream, you press Ctrl-C. What design feature makes this work cleanly?" (Correct: the cancellation token attached to `ResponseStream` — when the consumer drops, the stream signals the mapper to stop. Teaches: streams are cancellable by design.)
  3. "The model returns malformed JSON for a tool call. What happens — does Codex crash?" (Correct: the parser returns `InvalidArguments` and that error becomes the *tool output* the model sees, so the model can self-correct on the next round. Teaches: errors flow back into the loop as feedback, not bombs.)
- [x] **Glossary tooltips** — aggressive: `prompt` (the full text packet sent to the model — history plus instructions plus tools), `token` (a chunk of text the model emits or consumes — roughly 4 characters), `stream` (a sequence of events delivered one by one over time, not all at once), `mpsc` (multi-producer single-consumer — a type of channel where many writers feed one reader), `CancellationToken` (a flag you can wave to politely ask running tasks to stop), `function call` / `tool call` (the model saying "please run this tool with these arguments" instead of just text), `Tokio` (Rust's most popular library for running many tasks at once — like a kitchen with multiple cooks), `SSE` (Server-Sent Events — one common way to stream data from a server), `polling` (asking "anything new yet?" over and over).

### Reference Files to Read

- `references/content-philosophy.md` → ALL
- `references/gotchas.md` → ALL (especially: NO apostrophes in `data-steps`!)
- `references/interactive-elements.md` → Message Flow / Data Flow Animation; Group Chat Animation; Code ↔ English Translation Blocks; Multiple-Choice Quizzes; Callout Boxes; Glossary Tooltips
- `references/design-system.md` → only if needed

### Connections

- **Previous module:** Module 2 introduced the cast. Open with: "We met the actors. Now meet the music — the loop that drives every turn."
- **Next module:** Module 4 (Tools & Approvals). End with: "We saw the model 'call a tool.' But what *is* a tool, and why isn't it terrifying that a model can run shell commands on your machine? Next module."
- **Tone/style notes:** This is the densest module conceptually. Lean hard on the flow animation and the group chat. **CRITICAL:** the `data-steps` JSON attribute breaks if you put apostrophes inside labels — always replace `'s` and contractions, or use double-quote delimiters with escaped inner quotes. Vermillion accent.
