# ParseClipmate — Clipboard Ingestion and Processing Pipeline

**Zgent Status:** zgent (in-process toward Zgent certification)
**Role:** Consumer — clipboard content ingestion and processing
**Bead Prefix:** `pc`

## STOP — Beads Gate (Read This First)

**This repo is beads-first. You MUST authorize work before doing it.**

Before making ANY substantive changes (creating/modifying files, installing deps, changing config), do this:

```bash
bd ready                    # See if there is already an open bead for this work
bd create -t "Short title"  # Create one if not — YOU own this, do not ask the user
bd update <id> --status in_progress  # Claim it
```

When done:
```bash
bd close <id>               # Mark complete
bd sync                     # Sync with git
```

Reference the bead ID in your commit messages: `[pc-xxx] description`.

**No bead = no work.** Minor housekeeping (typos, status fields) is exempt. Everything else gets a bead. If in doubt, create one — it is cheap. See `.claude/rules/beads-first.md` for the full rule.

**This is not optional. This is not a Gas Town thing. This is how THIS repo works, every session, every instance.**

## What This Is

ParseClipmate is the enterprise clipboard ingestion zgent. It captures, parses, and processes clipboard content for use across the Gas City enterprise.

<!-- PLACEHOLDER: Steve to review SOI and advisory voice during walkthrough -->

> **Recovery**: Run `bd ready` after compaction, clear, or new session. Use `bd prime` for full context.

## What Every Claude Instance Must Understand

1. **Beads-first is non-negotiable.** Read the gate at the top of this file. Use `bd` commands. No exceptions.
2. **Consumer permissions.** Standard zgent access — read enterprise, write own repo. See `.claude/rules/zgent-permissions.md`.

## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Graduation Status

- **Standard artifacts deployed** — beads-first, zgent-permissions, settings.json, .gitattributes

## Conventions

- Beads-first: self-bead for non-trivial work, reference bead ID in commits
- Enterprise permissions: read sibling repos, write only own path
