"""Generate article metadata automatically from category,visibility messages.

The message hook validates without writing. After the article commit succeeds,
the post-commit hook makes a metadata-only follow-up commit, as in the original
workflow. It uses a separate index so unrelated staged files stay untouched.
No command pushes or contacts the website.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


class MetadataError(Exception):
    pass


@dataclass(frozen=True)
class Metadata:
    category: str
    visible: int
    created: str

    def render(self) -> bytes:
        return f"{self.category}\n{self.visible}\n{self.created}\n".encode(
            "utf-8"
        )


def category_value(value: str) -> str:
    value = value.strip()
    if not value or len(value.splitlines()) != 1 or "\x00" in value:
        raise MetadataError("Category must be nonempty and fit on one line.")
    return value


def message_options(message: str) -> tuple[str, int]:
    subject = message.splitlines()[0].strip() if message.splitlines() else ""
    parts = subject.split(",")
    if len(parts) != 2 or parts[1].strip() not in {"0", "1"}:
        raise MetadataError(
            "Use category,0 or category,1 on the first message line."
        )
    return category_value(parts[0]), int(parts[1].strip())


def utc_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise MetadataError("Invalid metadata creation timestamp.") from error
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.isoformat()


def parse_metadata(data: bytes) -> Metadata:
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeError as error:
        raise MetadataError("Metadata must be UTF-8.") from error
    if len(lines) != 3 or lines[1] not in {"0", "1"}:
        raise MetadataError(
            "Metadata needs category, visibility 0 or 1, and timestamp."
        )
    return Metadata(
        category_value(lines[0]), int(lines[1]), utc_timestamp(lines[2])
    )


def new_metadata(
    category: str, visible: int, old: bytes | None = None
) -> Metadata:
    if visible not in (0, 1):
        raise MetadataError("Visibility must be 0 or 1.")
    created = (
        parse_metadata(old).created
        if old is not None
        else datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    )
    # Naive UTC matches existing files and the site's datetime sorting.
    return Metadata(category_value(category), visible, created)


def git(root: Path, *args: str, env=None) -> bytes:
    result = subprocess.run(
        ["git", "--literal-pathspecs", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if result.returncode:
        raise MetadataError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def repo_root() -> Path:
    return Path(
        os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip()
    )


def article_path(path: str) -> bool:
    p = PurePosixPath(path)
    return p.parent == PurePosixPath("briefings") and p.suffix == ".md"


def meta_path(article: str) -> str:
    return "briefings/.meta/" + PurePosixPath(article).stem + ".meta"


def index_files(root: Path) -> dict[str, tuple[str, str]]:
    result = {}
    for row in git(root, "ls-files", "--stage", "-z", "--", "briefings").split(
        b"\0"
    ):
        if not row:
            continue
        header, path = row.split(b"\t", 1)
        mode, oid, stage = header.decode("ascii").split()
        if stage != "0":
            raise MetadataError(
                "Resolve staged conflicts before preparing metadata."
            )
        result[os.fsdecode(path)] = (mode, oid)
    return result


def blob(root: Path, entry: tuple[str, str]) -> bytes:
    if entry[0] not in {"100644", "100755"}:
        raise MetadataError("Articles and metadata must be regular files.")
    return git(root, "cat-file", "blob", entry[1])


def changed_articles(root: Path) -> list[str]:
    raw = git(
        root,
        "diff",
        "--cached",
        "--name-only",
        "--no-renames",
        "-z",
        "--",
        "briefings",
    )
    return sorted(
        os.fsdecode(p)
        for p in raw.split(b"\0")
        if p and article_path(os.fsdecode(p))
    )


def validate_index(root: Path, entries: dict, subject: str = "") -> None:
    articles = {p for p in entries if article_path(p)}
    expected = {meta_path(p) for p in articles}
    for article in sorted(articles):
        blob(root, entries[article])
        name = meta_path(article)
        if name not in entries:
            raise MetadataError(
                f"Missing staged {name}. "
                "Run hooks.py prepare with your message first."
            )
        parse_metadata(blob(root, entries[name]))
    for name in entries:
        p = PurePosixPath(name)
        if (
            p.parent == PurePosixPath("briefings/.meta")
            and p.suffix == ".meta"
        ):
            if name not in expected:
                raise MetadataError(f"Orphan staged metadata: {name}")
    # Ordinary editing messages keep metadata. Explicit headers must agree.
    if re.fullmatch(r"[^,\r\n]*,\s*[+-]?\d+\s*", subject):
        category, visible = message_options(subject)
        for article in changed_articles(root):
            if article in entries:
                item = parse_metadata(blob(root, entries[meta_path(article)]))
                if (item.category, item.visible) != (category, visible):
                    raise MetadataError(
                        "Message and staged metadata disagree. "
                        "Run hooks.py prepare with that message first."
                    )


def prepare(root: Path, message: str, stage: bool = True) -> list[str]:
    category, visible = message_options(message)
    entries = index_files(root)
    changes = changed_articles(root)
    planned: dict[str, bytes | None] = {}
    for article in changes:
        name = meta_path(article)
        if article not in entries:
            if name in entries:
                planned[name] = None
            continue
        blob(root, entries[article])
        old = blob(root, entries[name]) if name in entries else None
        data = new_metadata(category, visible, old).render()
        if old != data:
            planned[name] = data
    if not planned:
        return []
    # Validate every operation before writing or staging anything.
    previous = {}
    for name in planned:
        path = root / name
        if path.is_symlink() or path.parent.is_symlink():
            raise MetadataError(
                f"Refusing a symlink metadata destination: {name}"
            )
        current = path.read_bytes() if path.exists() else None
        indexed = blob(root, entries[name]) if name in entries else None
        if current != indexed:
            raise MetadataError(
                f"Preserve unstaged metadata edits: {name}. "
                "Review and stage that file explicitly first."
            )
        previous[name] = current
    try:
        for name, data in planned.items():
            path = root / name
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if stage:
            git(root, "add", "-A", "--", *sorted(planned))
    except (OSError, MetadataError):
        for name, data in previous.items():
            path = root / name
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_bytes(data)
        raise
    return sorted(planned)


def draft(root: Path, title: str, category: str) -> Path:
    article = "briefings/" + title + ".md"
    if not article_path(article) or not (root / article).is_file():
        raise MetadataError(
            "Draft title must name a Markdown article in briefings."
        )
    path = root / meta_path(article)
    if path.is_symlink() or path.parent.is_symlink():
        raise MetadataError("Refusing a symlink metadata destination.")
    old = path.read_bytes() if path.exists() else None
    data = new_metadata(category, 0, old).render()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def parse_article_renames(raw: bytes) -> dict[str, str]:
    fields = iter(raw.split(b"\0"))
    renames = {}
    for status in fields:
        if not status:
            continue
        old = os.fsdecode(next(fields))
        new = os.fsdecode(next(fields))
        if status.startswith(b"R") and article_path(old) and article_path(new):
            renames[new] = old
    return renames


def staged_article_renames(root: Path, base: str | None = None) -> dict:
    args = [
        "diff",
        "--cached",
        "--find-renames",
        "--diff-filter=R",
        "--name-status",
        "-z",
    ]
    if base is not None:
        args.append(base)
    return parse_article_renames(git(root, *args, "--", "briefings"))


def committed_article_renames(root: Path, reference: str) -> dict:
    return parse_article_renames(
        git(
            root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--find-renames",
            "--diff-filter=R",
            "--name-status",
            "--diff-merges=first-parent",
            "-r",
            "-z",
            reference,
            "--",
            "briefings",
        )
    )


def automatic_plan(
    root: Path,
    entries: dict,
    changes: list,
    message: str,
    renames: dict | None = None,
):
    """Plan generated files using staged or committed article versions."""
    subject = message.splitlines()[0].strip() if message.splitlines() else ""
    options = None
    if re.fullmatch(r"[^,\r\n]*,\s*[+-]?\d+\s*", subject):
        options = message_options(subject)
    planned = {}
    renames = renames or {}
    articles = {p for p in entries if article_path(p)}
    expected = {meta_path(p) for p in articles}
    for article in articles:
        blob(root, entries[article])
    for article in changes:
        name = meta_path(article)
        if article not in entries:
            if name in entries:
                planned[name] = None
            continue
        origin = meta_path(renames[article]) if article in renames else None
        inherited = blob(root, entries[origin]) if origin in entries else None
        selected = options
        if selected is None:
            if inherited is not None:
                item = parse_metadata(inherited)
                selected = (item.category, item.visible)
            elif name not in entries:
                raise MetadataError(
                    "New articles need category,0 or category,1 "
                    "as the first commit-message line."
                )
            else:
                continue
        path = root / name
        if path.is_symlink() or path.parent.is_symlink():
            raise MetadataError(f"Refusing a symlink metadata path: {name}")
        indexed = blob(root, entries[name]) if name in entries else None
        # Local preview metadata is generated too. Reuse its creation date.
        old = indexed if indexed is not None else inherited
        if old is None and path.exists():
            old = path.read_bytes()
        data = new_metadata(*selected, old).render()
        if data != indexed:
            planned[name] = data
    for name in expected:
        if name not in entries and name not in planned:
            raise MetadataError(
                f"Missing metadata for unchanged article: {name}"
            )
        if name in entries:
            parse_metadata(blob(root, entries[name]))
    for name in entries:
        p = PurePosixPath(name)
        if (
            p.parent == PurePosixPath("briefings/.meta")
            and p.suffix == ".meta"
        ):
            if name not in expected and name not in planned:
                raise MetadataError(f"Orphan metadata: {name}")
    for name, data in planned.items():
        path = root / name
        if path.is_symlink() or path.parent.is_symlink():
            raise MetadataError(f"Refusing a symlink metadata path: {name}")
        current = path.read_bytes() if path.exists() else None
        indexed = blob(root, entries[name]) if name in entries else None
        if indexed is not None and current not in (None, indexed, data):
            raise MetadataError(f"Preserve local metadata edits: {name}")
    return planned


def automatic_check(root: Path, message: str) -> None:
    automatic_plan(
        root,
        index_files(root),
        changed_articles(root),
        message,
        staged_article_renames(root),
    )


def tree_files(root: Path, reference: str) -> dict:
    entries = {}
    for row in git(
        root, "ls-tree", "-r", "-z", reference, "--", "briefings"
    ).split(b"\0"):
        if row:
            header, path = row.split(b"\t", 1)
            mode, _kind, oid = header.decode("ascii").split()
            entries[os.fsdecode(path)] = (mode, oid)
    return entries


def committed_articles(root: Path, reference: str) -> list:
    raw = git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "--no-renames",
        "--diff-merges=first-parent",
        "-r",
        "-z",
        reference,
        "--",
        "briefings",
    )
    return sorted(
        os.fsdecode(p)
        for p in raw.split(b"\0")
        if p and article_path(os.fsdecode(p))
    )


def commit_message(root: Path, reference: str) -> str:
    return git(root, "show", "-s", "--format=%B", reference).decode("utf-8")


def metadata_commit(root: Path, expected_head: str, env: dict, hook_dir: Path):
    if git(root, "rev-parse", "HEAD").decode().strip() != expected_head:
        raise MetadataError(
            "HEAD changed while generating metadata. Retry auto-meta."
        )
    # Only generated metadata differs from HEAD in this private index. Disable
    # hooks for this follow-up so it cannot recurse into another post-commit.
    return git(
        root,
        "-c",
        f"core.hooksPath={hook_dir}",
        "commit",
        "-m",
        "upsert-meta",
        env=env,
    )


def automatic_metadata(root: Path, reference: str = "HEAD") -> list:
    head = git(root, "rev-parse", "--verify", reference).decode().strip()
    changes = committed_articles(root, head)
    if not changes:
        return []
    entries = tree_files(root, head)
    planned = automatic_plan(
        root,
        entries,
        changes,
        commit_message(root, head),
        committed_article_renames(root, head),
    )
    if not planned:
        return []
    primary = index_files(root)
    previous = {
        name: (root / name).read_bytes() if (root / name).exists() else None
        for name in planned
    }
    with tempfile.TemporaryDirectory(prefix="brief-metadata-") as temporary:
        temp = Path(temporary)
        hook_dir = temp / "hooks"
        hook_dir.mkdir()
        env = dict(os.environ, GIT_INDEX_FILE=str(temp / "index"))
        git(root, "read-tree", head, env=env)
        try:
            for name, data in planned.items():
                path = root / name
                if data is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
            git(root, "add", "-A", "--", *sorted(planned), env=env)
            output = metadata_commit(root, head, env, hook_dir)
        except (OSError, MetadataError):
            for name, data in previous.items():
                path = root / name
                if data is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.write_bytes(data)
            raise
    # Refresh only generated paths that had no separately staged edits.
    current = index_files(root)
    refresh = [
        name
        for name in planned
        if primary.get(name) == entries.get(name)
        and current.get(name) == primary.get(name)
    ]
    if refresh:
        git(root, "add", "-A", "--", *sorted(refresh))
    print(output.decode("utf-8", "replace"), end="")
    return sorted(planned)


LEGACY_COMMIT_HOOK = """#!/bin/sh
# brief metadata validation hook
exec python3 "$(git rev-parse --show-toplevel)/hooks.py" check "$@"
"""

COMMIT_HOOK = """#!/bin/sh
# brief automatic metadata validation hook
exec python3 "$(git rev-parse --show-toplevel)/hooks.py" auto-check "$@"
"""

POST_COMMIT_HOOK = """#!/bin/sh
# brief automatic metadata commit hook
exec python3 "$(git rev-parse --show-toplevel)/hooks.py" auto-meta
"""


def install(root: Path) -> None:
    hook_dir = Path(
        os.fsdecode(git(root, "rev-parse", "--git-path", "hooks")).strip()
    )
    if not hook_dir.is_absolute():
        hook_dir = root / hook_dir
    target = hook_dir / "commit-msg"
    if target.exists() and target.read_text() not in (
        COMMIT_HOOK,
        LEGACY_COMMIT_HOOK,
    ):
        raise MetadataError(
            "Preserve existing commit-msg hook. Integrate its check manually."
        )
    post = hook_dir / "post-commit"
    if (
        post.exists()
        and post.read_text() != POST_COMMIT_HOOK
        and "python3 hooks.py add_commit_meta" not in post.read_text()
    ):
        raise MetadataError(
            "Preserve existing post-commit hook. Integrate metadata manually."
        )
    legacy = []
    for name, marker in (
        ("prepare-commit-msg", "python3 hooks.py build_meta"),
        ("post-commit", "python3 hooks.py add_commit_meta"),
    ):
        path = hook_dir / name
        if path.exists() and marker in path.read_text():
            backup = path.with_name(name + ".brief-legacy")
            if backup.exists() and backup.read_bytes() != path.read_bytes():
                raise MetadataError(f"Preserve existing hook backup: {backup}")
            legacy.append((path, backup))
    hook_dir.mkdir(parents=True, exist_ok=True)
    for path, backup in legacy:
        if backup.exists():
            path.unlink()
        else:
            path.rename(backup)
    target.write_text(COMMIT_HOOK)
    target.chmod(0o755)
    post.write_text(POST_COMMIT_HOOK)
    post.chmod(0o755)
    print(
        "Installed automatic metadata generation from commit messages. "
        "Existing pre-commit checks are preserved."
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser(
        "prepare", help="Prepare metadata before a user commit."
    )
    group = prep.add_mutually_exclusive_group(required=True)
    group.add_argument("--message")
    group.add_argument("--message-file", type=Path)
    check = commands.add_parser(
        "check", help="Validate Git's current index without writing."
    )
    check.add_argument("message_file", type=Path)
    auto_check = commands.add_parser(
        "auto-check",
        help="Validate automatic metadata generation without writing.",
    )
    auto_check.add_argument("message_file", type=Path)
    commands.add_parser(
        "auto-meta",
        help="Create the automatic metadata-only follow-up commit.",
    )
    preview = commands.add_parser(
        "draft", help="Write hidden local metadata, without staging."
    )
    preview.add_argument("title")
    preview.add_argument("--category", required=True)
    commands.add_parser(
        "install", help="Install validation and retire the owned legacy hooks."
    )
    commands.add_parser(
        "add_commit_meta", help="Compatibility name for auto-meta."
    )
    build = commands.add_parser(
        "build_meta",
        help="Compatibility name for automatic message validation.",
    )
    build.add_argument("message_file", type=Path)
    build.add_argument("source", nargs="?")
    build.add_argument("commit", nargs="?")
    args = parser.parse_args(argv)
    try:
        root = repo_root()
        if args.command == "install":
            install(root)
        elif args.command == "draft":
            print(draft(root, args.title, args.category))
        elif args.command in {"prepare", "build_meta"}:
            message = (
                args.message
                if args.command == "prepare" and args.message is not None
                else args.message_file.read_text(encoding="utf-8")
            )
            if args.command == "build_meta":
                automatic_check(root, message)
                return 0
            paths = prepare(root, message)
            print(
                "Prepared metadata: "
                + (", ".join(paths) if paths else "no changes")
            )
        elif args.command == "auto-check":
            automatic_check(
                root, args.message_file.read_text(encoding="utf-8")
            )
        elif args.command in {"auto-meta", "add_commit_meta"}:
            try:
                automatic_metadata(root)
            except (MetadataError, OSError) as error:
                raise MetadataError(
                    "The article commit exists, but automatic metadata "
                    f"generation failed: {error} "
                    "After fixing that error, run hooks.py auto-meta."
                ) from error
        elif args.command == "check":
            lines = args.message_file.read_text(encoding="utf-8").splitlines()
            validate_index(
                root, index_files(root), lines[0].strip() if lines else ""
            )
    except (MetadataError, OSError) as error:
        print(f"brief metadata: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
