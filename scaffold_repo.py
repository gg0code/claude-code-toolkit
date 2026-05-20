"""
scaffold_repo.py
-----------------
Builds the directory structure for the `effective-claude-code` repo.

Run this from inside the cloned repo directory:

    cd effective-claude-code
    python scaffold_repo.py

It creates the category folders, adds a placeholder README inside each one
(so they're not empty when you push to GitHub), and creates the folder for
the session-health-diagnostic-advisor skill.

Safe to run multiple times — it won't overwrite existing files.
"""

from pathlib import Path


# Define the category folders and their descriptions.
# Edit these descriptions if you want different wording in the placeholder READMEs.
CATEGORIES = {
    "session-management": "Meta-skills about how you use Claude Code — monitoring sessions, managing context, tracking spend.",
    "project-setup": "Skills for starting projects right — scaffolding, CLAUDE.md generation, conventions setup.",
    "code-quality": "Skills that enforce or check quality — linting rules, SRS compliance, code review helpers.",
    "workflow-automation": "Skills that automate repetitive workflows — commit messages, PR descriptions, changelog generation.",
    "documentation": "Skills for docs, SRS, READMEs — generating, extracting, or maintaining documentation.",
    "domain-specific": "Skills tied to particular industries or technology stacks.",
}

# Skills to scaffold inside specific categories.
# Format: { category_folder: [list of skill folder names] }
SKILLS = {
    "session-management": ["session-health-diagnostic-advisor"],
}


def create_category_readme(category: str, description: str) -> str:
    """Generate the placeholder README content for a category folder."""
    return f"""# {category}

{description}

## Skills in this category

_None yet._ Skills will be listed here as they land.

Each skill lives in its own subfolder containing a `SKILL.md`, a packaged `.skill` file,
and a short user-facing `README.md`.
"""


def create_skill_placeholder_readme(skill_name: str) -> str:
    """Generate a placeholder README for an individual skill folder."""
    return f"""# {skill_name}

_Drop the SKILL.md and the packaged `.skill` file into this folder._

This README is a placeholder. Replace it with a short user-facing description of:

- What the skill does
- When it triggers
- How to install it
- A small example of it in action
"""


def write_if_absent(path: Path, content: str) -> None:
    """Write the file only if it does not already exist — never overwrite."""
    if path.exists():
        print(f"  skipped (exists): {path}")
        return
    path.write_text(content, encoding="utf-8")
    print(f"  created:          {path}")


def main() -> None:
    repo_root = Path.cwd()
    print(f"Scaffolding repo structure under: {repo_root}\n")

    # 1. Create category folders + placeholder READMEs
    for category, description in CATEGORIES.items():
        category_path = repo_root / category
        category_path.mkdir(exist_ok=True)
        readme_path = category_path / "README.md"
        write_if_absent(readme_path, create_category_readme(category, description))

    # 2. Create skill folders + placeholder READMEs inside their categories
    for category, skill_list in SKILLS.items():
        for skill in skill_list:
            skill_path = repo_root / category / skill
            skill_path.mkdir(parents=True, exist_ok=True)
            readme_path = skill_path / "README.md"
            write_if_absent(readme_path, create_skill_placeholder_readme(skill))

    # 3. Friendly summary
    print("\nDone.")
    print("\nNext steps:")
    print("  1. Drop SKILL.md and the .skill file into")
    print("     session-management/session-health-diagnostic-advisor/")
    print("  2. Replace the placeholder README in that folder with a real one.")
    print("  3. git add . && git commit -m 'Scaffold repo structure' && git push")


if __name__ == "__main__":
    main()
