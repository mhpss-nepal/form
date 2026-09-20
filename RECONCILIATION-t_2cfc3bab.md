# Worktree reconciliation — task `t_2cfc3bab`

MHPSS Nepal · 20 Sep 2026 · scope-revised run (parent correction after two
equivalent failures: run 22 blocked on a provider glitch, run 34 exhausted its
150-iteration budget).

The parent's correction was that this task bundled **keying + safety
classification + multi-translator translation + back-translation + terminology
lock + native-speaker proofread across three forms** under one goal, which
cannot converge in one run. This document is the reconciliation the revised
scope names first, so the next worker is not confused by two trees carrying the
same commit subject.

**Canonical trees for this task**

| repo | worktree | branch | base | head | role |
|---|---|---|---|---|---|
| form | `/root/mhpss-nepal-work/form-translation` | `task/t_2cfc3bab` | `9032bb7` | `138ecf0` | **CANONICAL** — the keyed pages |
| hub | `/root/mhpss-nepal-work/hub-translation` | `task/t_2cfc3bab-i18n` | `ff2d4e2` | `3b82f12` | **CANONICAL** — the shared dictionary |

Everything else in this section is a copy or another task's lane.

## 1. The "two trees, same commit subject" trap

The same commit subject
(*"Key up referral.html, phq9.html and contact.html for translation, and draft
the Nepali for the translatable part of them."*)
appears twice. **This is not a duplicated commit.** It is one change set across
two repositories, committed once in each:

```
form-translation   138ecf0  keying + tests + evidence   (form repo)
hub-translation    3b82f12  dictionary + apply script   (hub repo)
```

The trees are disjoint — `form-translation` holds the three page files and the
keying test, `hub-translation` holds `assets/i18n-strings.js` and
`tools/i18n_apply.py`. Neither contains the other's files. A future worker who
sees the same subject twice and "reconciles" one into the other will delete a
real change set. **Keep both. There is no duplicate to remove.**

Mechanically verified above: the form worktree's HEAD `138ecf0` shares its
`9032bb7` base with the *form* repo, and the hub worktree's HEAD `3b82f12`
shares its `ff2d4e2` base with the *hub* repo; `hub-translation/.git` is
`gitdir: /root/mhpss-nepal-work/hub-real/.git/worktrees/hub-translation`.

## 2. The duplicate that WAS real, and why the gate disagreed with itself

`tools/i18n-check.py` reads the shared dictionary from a **sibling** `hub/`
directory, because in the deployed layout `form/` and `hub/` really are
siblings:

```python
STRINGS = os.path.join(ROOT, "..", "hub", "assets", "i18n-strings.js")
```

On this host `../hub/` is an **untracked staging copy**, not a git worktree. It
was still at the pre-keying revision `2026-09-16` (725 EN keys) while the three
pages were keyed against the new dictionary (971 EN keys). The gate therefore:

* failed `referral.html`, `phq9.html` and `contact.html` with *"keys used here
  with no English string"* — reading the wrong file, not a bad page; **and**
* reported the six `professionalOnly` prefixes as *"match no key yet"* — i.e. it
  appeared to reproduce the historic **0 of 204** dead-prefix bug at exactly the
  moment the bug was actually fixed.

Both readings are the opposite of the truth, and both come from one cause: a
gate that never says which file it read. Fixed three ways:

1. **`tools/i18n-dictionary-sync-check.py`** (new) compares the gate's
   dictionary against the canonical one by sha256 and exits 1 on drift. Run it
   before trusting any gate count.
2. **`tools/i18n-check.py`** now prints the dictionary path, its sha256, and a
   warning when that file is not under version control — so a count is never
   printed without the artifact it was counted from.
3. The staging copy was made **byte-identical** to the canonical dictionary
   (sha256 `6ef1aa00…40fa`), so the deployed sibling layout and this host agree.

This is a genuine defect in the verification apparatus, not book-keeping: it is
the same class of bug as the historic one — a protection being *claimed* while
nothing is protected. It is recorded rather than quietly fixed.

## 3. Which tree is canonical for the dictionary — and why

**`/root/mhpss-nepal-work/hub-translation/assets/i18n-strings.js`** (branch
`task/t_2cfc3bab-i18n`, HEAD `3b82f12`). It is:

* **tracked** (a git worktree of `hub-real/.git`), so it is reviewable and
  diffable; the `../hub/` copy is not;
* the only tree containing the **246 new EN keys** the three pages need;
* on the hub repo's own base `ff2d4e2`, one commit ahead, with the diff being
  `assets/i18n-strings.js +638` and `tools/i18n_apply.py` and nothing else.

**Not canonical, do not use as the dictionary source:**

| tree | why not |
|---|---|
| `/root/mhpss-nepal-work/hub/` | untracked staging copy, now kept in sync but still not reviewable |
| `/root/mhpss-nepal-work/hub-real/assets/` | **another task's lane** (`task/t_46e4cb25-hub-trial-scope`), deliberately left at the production dictionary `ff2d4e2`; the trial-scope work lives in the hub HTML and `assets/qr.js`, and the parent task's own evidence asserts `hub_paths_touched` semantics for `assets/` — leave it alone |

`hub-real` and `hub-translation` are worktrees of the **same git repository**
(`hub-real/.git`), which is why the two tasks sharing one path was a real
collision. They are serialised: `t_46e4cb25` is done.

## 4. Production refs unchanged

public `68bf197` · form `9032bb7` · hub `ff2d4e2`. No push, PR, merge or deploy.
The staging copy under `../hub/` is untracked and outside every repository, so
syncing it changes nothing that can be released.

## 5. Reproduce the reconciliation

```
python3 tools/i18n-dictionary-sync-check.py     # in form-translation; exit 0 = in sync
python3 tools/i18n-check.py                     # names the dictionary + sha256
```
