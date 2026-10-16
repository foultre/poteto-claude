# Claude Code port

Everything outside `port/` is generated from upstream. Edit `port/` only.

Sync with upstream:

```sh
python3 port/port.py            # clones cursor/plugins into a temp dir
python3 port/port.py ~/src/plugins   # or use an existing clone
```

The script copies `pstack/` at upstream HEAD, rewrites Cursor model slugs and paths to Claude Code equivalents (`TOKEN_MAP`), applies anchored patches (`PATCHES`), lays `overlays/` on top, and writes `.claude-plugin/`. It fails on any leftover Cursor slug or path, a broken relative link, or a patch anchor that no longer matches. `UPSTREAM` records the ported commit.

Model mapping: upstream's judgment family (`claude-opus-*`) becomes `fable`, its code family (`grok-*-fast`) becomes `opus`. Per-role overrides live in `~/.claude/pstack-models.md` (`/pstack:setup-pstack`).

Install:

```sh
claude plugin marketplace add <path-to-this-repo or owner/repo>
claude plugin install pstack@pstack-claude
```

Known gaps: skills still name Cursor-only tools (`cursor-team-kit` `deslop` / `control-ui` / `control-cli`, Cursor cloud agents) and read transcripts from `~/.cursor/projects/` (`recall`, `reflect`, `session-pickup`, `eval`, `worktree-audit.sh`).
