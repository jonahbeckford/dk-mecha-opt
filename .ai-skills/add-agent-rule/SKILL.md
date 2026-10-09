---
name: add-agent-rule
description: Add or change a durable agent instruction/rule for the dk-mecha-opt harness WITHOUT bloating AGENTS.md. Use whenever you are told to "always/never do X", "remember to do X", or to record a new convention or coordinator rule that is not already a maintainer statement or a harness amendment.
---

# Adding or changing an agent rule

`AGENTS.md` is loaded into every session, so it must stay a lean index. It
bloats when one-off fixes are appended directly to it. **Do not append rules to
AGENTS.md.** Route the rule to the right home below, and add at most one index
line for a brand-new topic.

This skill is the dk-mecha-opt clone of the dksdk-coder skill of the same name,
adapted to this repository's layout: skills live under `.ai-skills/`, and the
rule homes are this repo's root records and its skills, not a
`docs/agents/` tree.

## Route first to the skill that already owns the change

When a later skill here owns a kind of durable change (a maintainer statement, a
harness amendment, a locked decision), route the change to that skill instead of
this one, and add a row for it to this table when the skill is created.

| What it is | Where it goes |
|------------|----------------|
| (no routing skills yet) | |

Only when the change is a plain durable convention that no skill owns does it
come here.

## The budget

**500 tokens, hard, counting everything EXCEPT the `.ai-skills/<name>/SKILL.md`
paragraph.** Stay well under 32 KiB too, since some tools (for example OpenAI
Codex) silently truncate AGENTS.md at 32 KiB.

**That paragraph is exempt, and each skill description inside it must stay under
20 tokens.** A per-entry cap, not a shared pot: the skills paragraph grows with
how many skills the repo has, not with appended prose, so bounding each entry
puts the pressure where the bloat comes from.

**Twenty tokens is a trigger hint, not a summary.** Claude Code selects a skill
from that skill's own `description:` frontmatter, never from this line, so the
index entry only tells a scanning reader which one they want.

**Measure it, do not eyeball it.** From the repo root:

```sh
node -e 'const s=require("fs").readFileSync("AGENTS.md","utf8").replace(/\r\n/g,"\n"),p=s.match(/^`\.ai-skills\/<name>\/SKILL\.md`[\s\S]*?(?=\n\n)/m)?.[0]??"",t=n=>Math.round(n/4);console.log("index",t(s.length-p.length),"of 500; skills paragraph",t(p.length),"exempt");for(const m of p.matchAll(/`([\w*-]+)`\s+\(([^)]*)\)/g)){const k=t(m[2].replace(/\s+/g," ").length);if(k>=20)console.log("  OVER 20:",m[1],k)}'
```

It prints the index total against 500, the exempt paragraph's size, and every
description at or over 20 tokens.

## Decision tree — where does the new rule go?

1. **Does it fit an existing root record or skill?** Add it there. This is the
   default and covers almost every new rule.

   | Kind of rule | Destination |
   |--------------|-------------|
   | A repo-layout, script, or validator fact | `README.md` |
   | A rule that belongs to one existing skill's job | that `.ai-skills/<name>/SKILL.md` |

2. **Is it a genuinely new topic** with no home above? Create a new file:
   - A reusable, triggerable **procedure** (has a clear "use this when...")
     -> new `.ai-skills/<kebab-name>/SKILL.md` with `name:` + `description:`
     frontmatter (mirror an existing skill). `.ai-skills/` is the single
     authoritative location: this repo is a Claude Code plugin whose marketplace
     `source` is `./.ai-skills` and whose `.ai-skills/.claude-plugin/plugin.json`
     declares `"skills": ["."]`, so every `.ai-skills/<name>/SKILL.md` is
     auto-discovered with no registration step. Never copy or symlink a skill
     into `.claude/skills/` or `~/.claude/skills/`; that duplicates content and
     breaks the single-source rule.
   - Then add **exactly one** line to the AGENTS.md reference index pointing at
     the new file. Do not add more than one line per topic.

## Rules for the edit

- Prefer editing an existing record or skill over adding anything to AGENTS.md.
- Only touch AGENTS.md when introducing a brand-new topic file, and then only a
  single index line.
- Keep AGENTS.md free of `@` imports; references are plain relative paths the
  agent `Read`s on demand. An `@` import pulls content back into every session
  and re-bloats the context.
- Write the rule once, in one place. If it seems to belong in two records, put it
  in the more specific one and cross-reference by path.
- After editing, run the budget check above rather than trusting a glance. If the
  change pushes the index over 500 tokens, move content into a record or skill
  instead of growing the index; if it pushes a skill description to 20 tokens,
  shorten the description.
