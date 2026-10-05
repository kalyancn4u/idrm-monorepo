# ⚠️ FROZEN SNAPSHOT — not a living mirror

This folder, `archive/idrm-mvp-code/`, is a **one-time, point-in-time snapshot** of the MVP application
code taken on **2026-08-22** (Session 6). It is a frozen reference for history/comparison only.

- **The living source of truth is [`../../code/`](../../code/).** Make all code changes there.
- This snapshot is **NOT kept in sync** with `code/` and is **deliberately excluded from rule C3**
  (base↔archive doc mirroring) and from the §15 verification/parity pass. Do **not** "fix" drift between
  this folder and `code/` — divergence over time is expected and fine; `code/` always wins.
- It was created by copying the 159 git-tracked files under `code/` verbatim (working tree, so it includes
  the 2026-08-22 public-surface docstring pass). At creation it was byte-identical to `code/`, compiled
  clean (`compileall`), and passed `ruff check app`.

> Decision trail: the user first considered a *living* mirror, then chose a **one-time snapshot** (lower
> maintenance — no permanent double-edit obligation). See `archive/instructions.txt` §17 and the code
> CHANGELOG entry dated 2026-08-22. If a *living* mirror is ever wanted instead, re-copy from `code/` and
> add the C3 + §15 parity wiring at that time.
