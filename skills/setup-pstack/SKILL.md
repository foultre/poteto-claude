---
name: setup-pstack
description: Configure which models pstack uses per role and at what reasoning budget. Writes ~/.claude/pstack-models.md, which overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/pstack-models.md`, the per-role model file every pstack skill reads before it spawns a subagent.

## Steps

### 1. Load current state

The default mapping is the shape in step 4. If `~/.claude/pstack-models.md` exists, read it and treat its `# budget` line and role values as the current choices. Drop any line whose role is not in step 4.

### 2. Ask for a budget

Use AskUserQuestion with these four options. Name the current budget when the file records one.

- `unlimited — max effort`
- `large — xhigh effort`
- `medium — high effort`
- `small — medium effort`

The budget is the Agent tool `effort` every pstack spawn starts from.

### 3. Show the roles and confirm

Show every role with its model. Valid values are the Agent tool aliases `fable`, `opus`, `sonnet`, `haiku`, plus `inherit-parent` and `auto` (both run the role on the parent chat model). Ask whether to accept or change specific roles. Panel roles (arena runners, architect runners, interrogate reviewers) take a list, one subagent per entry. `arena cross-judge pool` is a list Arena picks one value from.

### 4. Write the file

Overwrite the whole file so reruns stay idempotent. Shape:

```
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# budget: large (xhigh)
feature, refactoring: opus
bug-fix: opus
perf-issue: opus
hillclimb: opus
judgment and prose: fable
hardest tasks: fable
how explorer: sonnet
how explainer: fable
why investigators: sonnet
why synthesizer: fable
reflect tooling: opus
reflect judgment, divergent, synthesizer: fable
arena runners: fable, opus
arena cross-judge pool: fable, opus
swarm workers: sonnet
architect runners: fable, opus
interrogate reviewers: fable, opus, sonnet
```

### 5. Confirm

Tell the user the file was written. Skills read it on every spawn, so it applies right away.

### 6. Offer a verification skill (optional)

If the project has no way to drive the real app for proof (a `verify-*` skill or an existing harness), offer once to generate one with `/create-verification-skill`. On no, move on.
