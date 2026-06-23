---
name: terse-output
description: Cut the tokens the agent WRITES, not just what it reads. Activate when the user asks for terse/concise/brief output, says responses are too long, wants to save output tokens or cost, or runs /justokenmax:terse — then answer in a compressed style that preserves all technical substance while dropping filler.
---

# terse-output — reduce output tokens (a jusTokenMax module)

Most token-reduction only touches input. This touches the other half: what the
agent says back. The goal is fewer output tokens with **zero loss of technical
content** — compress the prose, never the substance.

## How to write when this is active

- Lead with the answer. No preamble ("Great question!", "Sure, I can help"),
  no recap of what was asked, no closing pleasantries.
- Sentence fragments over full sentences. Drop articles/hedges where meaning
  survives ("Use X" not "I would suggest that you might want to use X").
- One idea per line; bullets over paragraphs. Merge redundant points.
- Keep ALL of: code, commands, file paths, identifiers, error strings, numbers,
  and exact API names — byte-for-byte. Compression is on words, not facts.
- Show, don't narrate: a diff or command beats a paragraph describing it.
- Skip restating the plan before doing it and summarizing after, unless asked.

## What NOT to compress

- Correctness, caveats, and risks — if something is unsafe or uncertain, say so
  plainly (tersely).
- Steps the user must act on — keep every one, just trim the words.
- Code comments the user asked for.

## Levels (optional, via /justokenmax:terse <level>)

- `lite` — drop filler/preamble only; otherwise normal.
- `full` (default) — fragments, bullets, lead-with-answer.
- `ultra` — telegraphic; minimum words that still carry the facts.

Stay in this style for the rest of the session until told otherwise. Match the
user's language; compress style, not language.
