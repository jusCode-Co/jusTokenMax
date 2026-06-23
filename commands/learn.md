---
description: Mine this session for recurring corrections and save them to CLAUDE.md so future sessions don't repeat the mistakes (and waste tokens re-litigating them).
---

Review the current conversation for durable lessons that should persist, then
propose additions to the project's memory file (CLAUDE.md / AGENTS.md).

Look specifically for:
- Corrections the user made more than once, or had to insist on.
- Project conventions, constraints, or preferences that weren't obvious from the
  code and that you got wrong or had to discover.
- Commands / paths / gotchas that cost back-and-forth to figure out.

For each, draft a one-line, terse rule (keep code/paths/identifiers exact —
follow the `terse-output` style). Show the proposed CLAUDE.md additions as a
diff and apply them only after a quick confirmation.

Do NOT record: one-off task details, secrets, anything already in CLAUDE.md, or
facts derivable from the code. The point is to stop paying tokens to relearn the
same things every session.
