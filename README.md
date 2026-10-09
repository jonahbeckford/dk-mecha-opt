# dk-mecha-opt

Coordinator's record for the dk mecha optimization harness. Agent instructions are in `AGENTS.md`
(`CLAUDE.md` imports it).

## Layout

- `AGENTS.md` - the lean agent index, loaded every session.
- `CLAUDE.md` - `@AGENTS.md`, so Claude Code loads the same index.
- `.ai-skills/` - agent skills, also the Claude Code plugin root (see `.ai-skills/README.md`).
- `.claude-plugin/marketplace.json` - the marketplace entry, `source: "./.ai-skills"`.
