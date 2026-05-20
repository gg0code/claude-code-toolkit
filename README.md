# Effective Claude Code

A small, opinionated collection of skills and best practices for getting more out of Claude Code — built from real project work, not bulk-generated.

## What's inside

| Skill | Category | What it does |
|---|---|---|
| [session-health-diagnostic-advisor](session-management/session-health-diagnostic-advisor/) | Session management | Monitors token spend and context bloat during long sessions. Tells you when to run `/cost`, `/compact`, or `/clear`. |

More skills coming as I build them. Each one is project-tested before it lands here.

## Install a skill

Download the `.skill` file from the skill's folder and import it into Claude Code, or use the plugin marketplace:

```
/plugin marketplace add <your-github-username>/effective-claude-code
/plugin install <skill-name>@effective-claude-code
```

## Repo layout

```
session-management/    → meta-skills about how you use Claude Code
project-setup/         → starting projects right
code-quality/          → enforce and check quality
workflow-automation/   → automate repetitive workflows
documentation/         → docs, SRS, READMEs
domain-specific/       → skills tied to particular industries or stacks
```

Each skill lives in its own folder with a `SKILL.md`, a packaged `.skill` file, and a short README.

## Contributing

PRs welcome. Keep skills focused — one purpose per skill — and include a brief README explaining when to use it. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — use freely, modify freely, attribution appreciated.
