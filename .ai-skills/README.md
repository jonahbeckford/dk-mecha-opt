# `.ai-skills/`

This directory holds the coordinator's agent skills. It is deliberately BOTH an open-standard skills
collection and a Claude Code plugin root, in one place. This note records why the layout is the way it
is, so a later reader does not undo it.

## The open-standard layout

Skills follow the Agent Skills open standard (agentskills.io). A skill is a directory with a `SKILL.md`
file at its root, plus optional `scripts/`, `references/` and `assets/` subdirectories:

```
.ai-skills/
  <skill-name>/
    SKILL.md          # YAML frontmatter (name, description) + Markdown instructions
    scripts/          # optional
    references/       # optional
    assets/           # optional
```

The standard defines the skill FORMAT and the per-skill directory shape. It does NOT prescribe a
top-level directory name; each tool picks its own (Claude Code uses `.claude/skills/`, Cursor
`.cursor/`, and so on). `.ai-skills/` is a vendor-neutral name chosen here on purpose: it reads as
"AI skills" for any tool, not one vendor's.

## The Claude Code plugin, and why size and privacy drove this

The same directory is a Claude Code plugin root. `.ai-skills/.claude-plugin/plugin.json` carries
`"skills": ["."]`, which tells Claude's loader to scan this directory for `<name>/SKILL.md` folders
directly. The marketplace entry points its `source` at `./.ai-skills`, not `./`.

That `source` choice is the whole point, for two reasons:

- **Size.** `claude plugin update` copies the plugin `source` directory verbatim into the plugin cache
  (`~/.claude/plugins/cache/<marketplace>/<plugin>/<commit>/`). It honours no include, exclude,
  `.claudeignore` or `.gitignore`. With `source: "./"` the whole repository root is copied, coordinator
  records and all; in the sibling dk-engine-opt that was 36 MB of records against 0.26 MB of skills.
  Pointing `source` at `./.ai-skills` caches only the skills.
- **Privacy.** A `source: "./"` in a repository that holds private source copies all of it into the
  plugin cache on every snapshot (about 249 MB for dksdk-coder). Narrowing every plugin `source` to its
  own `.ai-skills/` is what keeps that source out of the cache.

## Why AGENTS.md is still needed

The open standard defines how a skill is written, not where a tool goes looking. Tools auto-discover
skills from their own locations (`.claude/skills/`, `~/.claude/skills/`), not from `.ai-skills/`. So a
skill placed here is not automatically found by every context.

`AGENTS.md` is the bridge. It is loaded every session and it tells the agent that these skills exist,
where they live, and the conventions that govern them: the reference index, the lean-index budget, and
the routing in `add-agent-rule` that decides where a new rule or skill goes. When a skill moves here,
its entry in `AGENTS.md` is updated to point at `.ai-skills/<name>/`. Keep `AGENTS.md` in step with
this directory; a skill that lives here but is absent from `AGENTS.md` is a skill the coordinator will
not reliably reach.
