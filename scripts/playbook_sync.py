#!/usr/bin/env python3
"""Bootstrap, check and apply playbook-managed files in a project repository.

Usage (run from the target repo root):
  playbook_sync.py bootstrap --version vX.Y.Z [--profile P --package-dir DIR] [--skip-root] [--force]
  playbook_sync.py check [--enforce true|false]
  playbook_sync.py apply --version vX.Y.Z

Rules:
- managed files must equal the template, except lines containing <<FILL / <<PLAYBOOK_SHA (wildcards)
  and content inside REPO-SPECIFIC:START/END blocks; the version in the managed-by header is ignored.
- seed files are only checked for presence.
- append files: header (up to <!-- ENTRIES-START -->) is managed.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

PLAYBOOK = Path(__file__).resolve().parent.parent
TEMPLATES = PLAYBOOK / "templates"
REPO = Path.cwd()
PLACEHOLDER = re.compile(r"<<(FILL|PLAYBOOK_SHA)")
VERSION_RE = re.compile(r"agentic-playbook v\d+\.\d+\.\d+")
BLOCK_START, BLOCK_END = "REPO-SPECIFIC:START", "REPO-SPECIFIC:END"
ENTRIES = "<!-- ENTRIES-START -->"


def manifest() -> list[tuple[str, str, Path, str]]:
    rows = []
    for line in (TEMPLATES / "manifest.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        mode, scope, src, dest = line.split()
        rows.append((mode, scope, TEMPLATES / src, dest))
    return rows


def profiles() -> list[tuple[str, str]]:
    f = REPO / ".playbook-profiles"
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            prof, d = line.split(":", 1)
            out.append((prof.strip(), d.strip()))
    return out


def targets(with_scope: bool = False) -> list:
    res = []
    profs = profiles()
    for mode, scope, src, dest in manifest():
        if scope == "root":
            res.append((mode, "root", src, REPO / dest))
        else:
            want = scope.split(":", 1)[1]
            for prof, d in profs:
                if prof == want:
                    res.append((mode, scope, src, REPO / d / dest))
    return res if with_scope else [(m, s_, d) for m, _, s_, d in res]


def strip_block(lines: list[str]) -> list[str]:
    out, inside = [], False
    for ln in lines:
        if BLOCK_START in ln:
            inside = True
            out.append("<<BLOCK>>")
            continue
        if BLOCK_END in ln:
            inside = False
            continue
        if not inside:
            out.append(ln)
    return out


def norm(text: str) -> list[str]:
    return [VERSION_RE.sub("agentic-playbook vX", ln.rstrip()) for ln in text.splitlines()]


def matches(template: str, actual: str) -> tuple[bool, str]:
    t, a = strip_block(norm(template)), strip_block(norm(actual))
    if len(t) != len(a):
        return False, f"line count differs from template ({len(a)} vs {len(t)}) outside REPO-SPECIFIC blocks"
    for i, (tl, al) in enumerate(zip(t, a), 1):
        if PLACEHOLDER.search(tl):
            continue
        if tl != al:
            return False, f"line {i} differs: expected {tl!r}"
    return True, ""


def check(enforce: bool) -> int:
    problems: list[str] = []
    warnings: list[str] = []
    for mode, src, dst in targets():
        rel = dst.relative_to(REPO)
        if not dst.exists():
            problems.append(f"missing {mode} file: {rel}")
            continue
        content = dst.read_text()
        if PLACEHOLDER.search(content):
            (problems if enforce else warnings).append(f"unfilled placeholder in {rel}")
        if mode == "managed":
            ok, why = matches(src.read_text(), content)
            if not ok:
                problems.append(f"managed file edited outside REPO-SPECIFIC block: {rel}: {why}")
        elif mode == "append":
            head_t = src.read_text().split(ENTRIES)[0]
            head_a = content.split(ENTRIES)[0]
            if norm(head_t) != norm(head_a):
                problems.append(f"managed header of {rel} was edited")
    for w in warnings:
        print(f"::warning::{w}")
    for p in problems:
        print(f"::error::{p}")
    print(f"playbook check: {len(problems)} problem(s), {len(warnings)} warning(s)")
    return 1 if problems else 0


def carry_over(new_template: str, current: str) -> str:
    """Write the new template, keeping filled placeholder lines and the REPO-SPECIFIC block."""
    cur_lines = current.splitlines()
    out: list[str] = []
    for ln in new_template.splitlines():
        if PLACEHOLDER.search(ln):
            prefix = ln.split("<<", 1)[0]
            cand = [c for c in cur_lines if len(prefix.strip()) >= 3 and c.startswith(prefix) and "<<" not in c]
            out.append(cand[0] if len(cand) == 1 else ln)
        else:
            out.append(ln)
    text = "\n".join(out) + "\n"
    pat = rf"([^\n]*{BLOCK_START}[^\n]*\n)(.*?)([^\n]*{BLOCK_END})"
    m_cur = re.search(pat, current, re.S)
    m_new = re.search(pat, text, re.S)
    if m_cur and m_new:
        text = text[: m_new.start(2)] + m_cur.group(2) + text[m_new.end(2):]
    return text


def set_version(text: str, version: str) -> str:
    return VERSION_RE.sub(f"agentic-playbook {version}", text)


def apply(version: str) -> int:
    for mode, src, dst in targets():
        new = set_version(src.read_text(), version)
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(new)
            print(f"added {dst.relative_to(REPO)}")
            continue
        if mode == "managed":
            dst.write_text(carry_over(new, dst.read_text()))
            print(f"updated {dst.relative_to(REPO)}")
        elif mode == "append":
            cur = dst.read_text()
            entries = cur.split(ENTRIES, 1)[1] if ENTRIES in cur else ""
            dst.write_text(new.split(ENTRIES)[0] + ENTRIES + entries)
            print(f"updated header {dst.relative_to(REPO)}")
    (REPO / ".playbook-version").write_text(version + "\n")
    return 0


def bootstrap(version: str, profile: str | None, pkg: str | None, skip_root: bool, force: bool) -> int:
    if profile:
        if not pkg:
            sys.exit("--package-dir is required with --profile")
        pf = REPO / ".playbook-profiles"
        existing = pf.read_text() if pf.exists() else "# profile:package-dir (managed by bootstrap)\n"
        line = f"{profile}:{pkg}"
        if line not in existing.splitlines():
            pf.write_text(existing + line + "\n")
    conflicts = []
    for mode, scope, src, dst in targets(with_scope=True):
        if skip_root and scope == "root":
            continue
        new = set_version(src.read_text(), version)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not force:
            if dst.read_text() != new:
                alt = dst.with_name(dst.name + ".playbook-new")
                alt.write_text(new)
                conflicts.append(str(dst.relative_to(REPO)))
            continue
        dst.write_text(new)
        if dst.suffix == ".sh":
            dst.chmod(0o755)
    if not skip_root:
        (REPO / ".playbook-version").write_text(version + "\n")
        gi = REPO / ".gitignore"
        snippet = (TEMPLATES / "project/gitignore.snippet").read_text()
        cur = gi.read_text() if gi.exists() else ""
        if "CLAUDE.local.md" not in cur:
            gi.write_text(cur + ("\n" if cur and not cur.endswith("\n") else "") + snippet)
    if profile:
        frag = TEMPLATES / profile / ("package.scripts.json" if profile != "backend-python" else "pyproject.snippet.toml")
        shutil.copy(frag, REPO / pkg / (frag.name + ".playbook-merge"))
    print("\n== Bootstrap complete ==")
    if conflicts:
        print("Existing files differ from templates (new versions written as *.playbook-new; merge by hand):")
        for c in conflicts:
            print("  -", c)
    print("Unfilled placeholders:")
    for p in sorted(REPO.rglob("*")):
        if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts:
            try:
                if PLACEHOLDER.search(p.read_text()):
                    print("  -", p.relative_to(REPO))
            except (UnicodeDecodeError, OSError):
                pass
    print("""
Next steps:
 1. Fill every <<FILL: ...>> placeholder (CI fails while any remain once PLAYBOOK_ENFORCE is true).
 2. Merge the *.playbook-merge fragment(s) into package.json scripts / pyproject.toml, then delete them.
 3. Pin actions to SHAs:  pinact run   (https://github.com/suzuki-shunsuke/pinact)
 4. Replace <<PLAYBOOK_SHA>> with the commit SHA of the playbook release tag.
 5. Set CODEOWNERS teams; install hooks: lefthook install
 6. Set repo variable PLAYBOOK_ENFORCE=false for a one-week report-only period (existing repos).
 7. Ask an org admin to apply the 'agentic-baseline' ruleset. Open the PR.""")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bootstrap")
    b.add_argument("--version", required=True)
    b.add_argument("--profile", choices=["frontend", "backend-node", "backend-python"])
    b.add_argument("--package-dir")
    b.add_argument("--skip-root", action="store_true")
    b.add_argument("--force", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("--enforce", default="true")
    a = sub.add_parser("apply")
    a.add_argument("--version", required=True)
    args = ap.parse_args()
    if args.cmd == "bootstrap":
        return bootstrap(args.version, args.profile, args.package_dir, args.skip_root, args.force)
    if args.cmd == "check":
        return check(args.enforce.lower() == "true")
    return apply(args.version)


if __name__ == "__main__":
    sys.exit(main())
