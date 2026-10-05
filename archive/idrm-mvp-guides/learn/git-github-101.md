# Git / GitHub 101

> *Type: Guide (101 / foundational) · Audience: complete novices → developers · Status: MVP — current · Track: Software Engineering (#10)*
> *Version control is how teams change code without overwriting each other or losing history. This guide takes
> you from "what is Git?" to making a change the IDRM way. You need only a terminal.*

---

## 1. Why version control exists

Imagine ten people editing the same document by emailing copies around — you'd lose changes and never know who
changed what. **Version control** solves this: it records every change, who made it, and why, and lets many
people work in parallel and merge safely.

- **Git** — the version-control *tool* that runs on your machine (tracks history locally).
- **GitHub** (also GitLab, etc.) — a *hosting service* where the shared copy lives online and people collaborate.

*Git is the engine; GitHub is the shared garage.*

---

## 2. The core nouns

- **Repository ("repo")** — the project folder, plus its entire history.
- **Commit** — one saved snapshot of changes, with a message explaining *why*.
- **Branch** — a parallel line of work, so your changes don't disturb the main code until ready.
- **`main`** — the primary branch (the source of truth).
- **Merge** — combining a branch's changes back into another.
- **Pull Request (PR)** — a proposal to merge your branch, where others **review** it first.

---

## 3. The everyday loop (with commands)

```bash
git clone <url>            # get the repo (once)
git checkout -b my-change  # create + switch to a new branch
# ... edit files ...
git add .                  # stage the changes you want to save
git commit -m "Explain what and why"   # save a snapshot
git push -u origin my-change           # send your branch to GitHub
# ... open a Pull Request on GitHub, get review, merge ...
git checkout main && git pull          # update your local main afterwards
```

- **stage → commit → push** is the rhythm. Commit **small and often**, with messages that say *why*, not just
  *what*.
- Keep `main` always working; do real work on branches.

---

## 4. Reading history & undoing safely

```bash
git status     # what's changed right now
git log --oneline   # the history, one line per commit
git diff       # the exact lines you've changed
```

Because every commit is saved, mistakes are recoverable — which is what makes it *safe* to experiment on a
branch.

---

## 5. The IDRM way

- Work on a **branch**, open a **PR**, get it **reviewed**, then merge — never commit straight to `main`.
- Commit messages and PRs explain the *why* (they become the project's memory, alongside the CHANGELOGs).
- The full contributor flow — clone → set up → change → test → PR — is in the
  **[Developer / Contributor guide](../30-contribute-developer-guide.md)**.

*(Note: this archive folder is documentation, not a live Git repo; the workflow above is what the real IDRM code
repo uses.)*

---

## 6. Mastery check

You've got Git/GitHub 101 when you can:

1. Explain the difference between **Git** and **GitHub**.
2. Define **repo, commit, branch, merge, pull request**.
3. Run the clone → branch → add → commit → push loop from memory.
4. Explain why you work on a branch and open a PR instead of editing `main`.
5. Say how to see what changed (`status`, `log`, `diff`).

---

## 7. Go deeper

- Pro Git (free book) — git-scm.com/book · GitHub docs — docs.github.com
- Conventional Commits — conventionalcommits.org
- IDRM contributor guide: [`../30-contribute-developer-guide.md`](../30-contribute-developer-guide.md)

---
*Next:* [REST API 101](rest-api-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
