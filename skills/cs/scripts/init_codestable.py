from __future__ import annotations

import argparse
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "templates" / "entities"
WORKSPACE_DIR = "codestable"
LEGACY_WORKSPACE_DIR = ".cs"

DIRS = [
    "codestable/talks",
    "codestable/vision",
    "codestable/spec",
    "codestable/issues",
    "codestable/epics",
    "codestable/notes",
    "codestable/tools",
    "codestable/tasks/active",
    "codestable/tasks/archived",
]


def ensure_path_has_no_symlink(root: Path, target: Path) -> None:
    relative_target = target.relative_to(root)
    current_path = root
    for path_component in relative_target.parts:
        current_path = current_path / path_component
        if current_path.is_symlink():
            raise ValueError(f"CodeStable workspace path contains a symlink: {current_path}")


def prepare_workspace(project: Path, migrate_legacy: bool) -> bool:
    workspace = project / WORKSPACE_DIR
    legacy_workspace = project / LEGACY_WORKSPACE_DIR

    ensure_path_has_no_symlink(project, legacy_workspace)
    if not legacy_workspace.exists():
        return False
    if not legacy_workspace.is_dir():
        raise ValueError(f"Legacy workspace path is not a directory: {legacy_workspace}")
    if workspace.exists():
        raise ValueError(
            f"Found both {legacy_workspace} and {workspace}; reconcile them manually before initializing."
        )
    if not migrate_legacy:
        raise ValueError(
            f"Found legacy workspace {legacy_workspace}. Re-run with --migrate-legacy to move it to {workspace}."
        )

    legacy_workspace.rename(workspace)
    return True


def init_codestable(project: Path, force: bool, migrate_legacy: bool) -> int:
    project = project.resolve()
    ensure_path_has_no_symlink(project, project / WORKSPACE_DIR)
    migrated_legacy = prepare_workspace(project, migrate_legacy)
    vision_template = (TEMPLATES / "vision-index.md").read_text(encoding="utf-8")
    project_spec_template = (TEMPLATES / "project-spec-index.md").read_text(encoding="utf-8")

    for rel in DIRS:
        directory_path = project / rel
        ensure_path_has_no_symlink(project, directory_path)
        directory_path.mkdir(parents=True, exist_ok=True)
        ensure_path_has_no_symlink(project, directory_path)

    managed_indexes = [
        (project / WORKSPACE_DIR / "vision" / "index.md", vision_template),
        (project / WORKSPACE_DIR / "spec" / "index.md", project_spec_template),
    ]
    created: list[str] = []
    kept: list[str] = []

    for index_path, template in managed_indexes:
        ensure_path_has_no_symlink(project, index_path)
        if index_path.exists() and not force:
            if not index_path.is_file():
                raise ValueError(f"CodeStable canonical index is not a regular file: {index_path}")
            kept.append(str(index_path))
        else:
            if index_path.exists() and not index_path.is_file():
                raise ValueError(f"CodeStable canonical index is not a regular file: {index_path}")
            index_path.write_text(template, encoding="utf-8")
            ensure_path_has_no_symlink(project, index_path)
            if not index_path.is_file():
                raise ValueError(f"CodeStable canonical index was not created safely: {index_path}")
            created.append(str(index_path))

    print(f"Initialized CodeStable workspace at {project / WORKSPACE_DIR}")
    if migrated_legacy:
        print(f"Migrated legacy workspace from {project / LEGACY_WORKSPACE_DIR}")
    print(f"Created or updated files: {len(created)}")
    for path in created:
        print(f"  + {path}")
    if kept:
        print(f"Kept existing files: {len(kept)}")
        for path in kept:
            print(f"  = {path}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a CodeStable workspace in codestable/.")
    parser.add_argument("--project", default=".", help="Project root to initialize.")
    parser.add_argument("--force", action="store_true", help="Overwrite the existing vision and project spec indexes.")
    parser.add_argument(
        "--migrate-legacy",
        action="store_true",
        help="Move an existing .cs workspace to codestable/.",
    )
    args = parser.parse_args()

    return init_codestable(Path(args.project), args.force, args.migrate_legacy)


if __name__ == "__main__":
    raise SystemExit(main())
