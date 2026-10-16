#!/usr/bin/env python3
"""Regenerate this Claude Code plugin from cursor/plugins' pstack.

Usage: python3 port/port.py [path-to-cursor-plugins-clone]
Without a path, clones https://github.com/cursor/plugins into a temp dir.
Rewrites skills/, agents/, docs/, LICENSE, README.md, .claude-plugin/ and UPSTREAM. Safe to rerun.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERLAYS = Path(__file__).resolve().parent / "overlays"
PLUGIN = "pstack"
CLAUDE_REVISION = 1

TOKEN_MAP = [
    (r"`?~/\.cursor/rules/pstack-models\.mdc`?", "`~/.claude/pstack-models.md`"),
    (r"the `pstack-models\.mdc` rule", "`~/.claude/pstack-models.md`"),
    (r"claude-opus-\d+(?:-\d+)?-[a-z]+(?:-fast)?", "fable"),
    (r"grok-\d+(?:\.\d+)?-[a-z]+-fast", "opus"),
    (r"generalPurpose", "general-purpose"),
    (r'subagent_type: "poteto-agent"', f'subagent_type: "{PLUGIN}:poteto-agent"'),
    (r'subagent_type: "comment-sicko"', f'subagent_type: "{PLUGIN}:comment-sicko"'),
    (r"^is_background: true$", "background: true"),
]

MODEL_PARAGRAPH = (
    "**Match the model to the job.** Start from the role's line or default alias "
    "(`fable`, `opus`, `sonnet`, `haiku`) and pass the Agent tool's `effort` from the "
    "`# budget` line of `~/.claude/pstack-models.md` (`xhigh` when absent). Raise it one "
    "step, up to `max`, for the hardest or subtlest work. Lower it one step for judgment "
    "and two or more steps for routine work. Verification stays on the `swarm workers` "
    "model. Keep the alias the role names, so a diverse panel stays diverse. A role on "
    "`auto` or `inherit-parent` stays on the parent model."
)

PATCHES = {
    "skills/poteto-mode/SKILL.md": [
        (r"^disable-model-invocation: true\n", ""),
        (r"^\*\*Match the model to the job\.\*\*.*$", MODEL_PARAGRAPH),
    ],
}

LEFTOVERS = [
    r"claude-opus-\d", r"grok-\d", r"gpt-5", r"pstack-models\.mdc",
    r"generalPurpose", r"is_background",
]


def upstream_dir(arg):
    if arg:
        return Path(arg).resolve()
    tmp = Path(tempfile.mkdtemp(prefix="cursor-plugins-"))
    subprocess.run(["git", "clone", "-q", "--depth", "1",
                    "https://github.com/cursor/plugins.git", str(tmp)], check=True)
    return tmp


def rewrite(path, rules, strict=False):
    text = path.read_text()
    for pattern, repl in rules:
        new, n = re.subn(pattern, lambda _: repl, text, flags=re.M)
        if strict and n == 0:
            sys.exit(f"patch anchor not found in {path}: {pattern}")
        text = new
    path.write_text(text)


def main():
    upstream = upstream_dir(sys.argv[1] if len(sys.argv) > 1 else None)
    src = upstream / "pstack"
    commit = subprocess.run(["git", "-C", str(upstream), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()

    for name in ("skills", "agents", "docs"):
        shutil.rmtree(ROOT / name, ignore_errors=True)
        shutil.copytree(src / name, ROOT / name,
                        ignore=shutil.ignore_patterns("node_modules"))
    for name in ("LICENSE", "README.md"):
        shutil.copy(src / name, ROOT / name)
    shutil.copytree(OVERLAYS, ROOT, dirs_exist_ok=True)

    for f in [ROOT / "README.md", *(p for d in ("skills", "agents", "docs") for p in (ROOT / d).rglob("*.md"))]:
        rewrite(f, TOKEN_MAP)
    for rel, rules in PATCHES.items():
        rewrite(ROOT / rel, rules, strict=True)

    meta = json.loads((src / "plugin.json").read_text())
    manifest = ROOT / ".claude-plugin"
    manifest.mkdir(exist_ok=True)
    (manifest / "plugin.json").write_text(json.dumps({
        "name": PLUGIN,
        "version": f"{meta['version']}-claude.{CLAUDE_REVISION}",
        "description": meta["description"] + " Ported to Claude Code.",
        "author": meta["author"],
        "homepage": meta["homepage"],
        "license": meta["license"],
        "keywords": meta["keywords"],
    }, indent=2, ensure_ascii=False) + "\n")
    (manifest / "marketplace.json").write_text(json.dumps({
        "name": f"{PLUGIN}-claude",
        "description": "pstack ported from Cursor to Claude Code.",
        "owner": {"name": "Rémi Foult"},
        "plugins": [{"name": PLUGIN, "source": "./", "description": meta["description"]}],
    }, indent=2, ensure_ascii=False) + "\n")
    (ROOT / "UPSTREAM").write_text(f"https://github.com/cursor/plugins/tree/{commit}/pstack\n")

    leftovers = subprocess.run(
        ["grep", "-rnE", "|".join(LEFTOVERS), "skills", "agents", "docs", "README.md",
         "--include=*.md"], cwd=ROOT, capture_output=True, text=True).stdout
    if leftovers:
        sys.exit("unported model ids or Cursor paths:\n" + leftovers)
    broken = [f"{md.relative_to(ROOT)} -> {link}"
              for md in (ROOT / "skills").rglob("*.md")
              for link in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", md.read_text())
              if link != "url" and not (md.parent / link).exists()]
    if broken:
        sys.exit("broken relative links:\n" + "\n".join(broken))
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        head = skill.read_text().split("---")[1]
        if not re.search(r"^name: ", head, re.M) or not re.search(r"^description: ", head, re.M):
            sys.exit(f"missing name or description: {skill}")
    print(f"ported pstack {meta['version']} @ {commit[:7]}")


if __name__ == "__main__":
    main()
