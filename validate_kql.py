#!/usr/bin/env python3
"""Structural sanity check for the KQL query pack.

KQL can only be truly validated against a live Log Analytics / Sentinel
workspace, so this checker verifies what CAN be checked offline:
  - balanced (), {}, []
  - file opens with the required documentation header (// Query: ...)
  - contains at least one pipeline operator (|)
  - does not end with a dangling pipe

It does NOT validate table names, column names, or function signatures —
see docs/lab-setup.md for running the queries for real.

Usage: python3 validate_kql.py [--dir queries]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PAIRS = {"(": ")", "{": "}", "[": "]"}


def strip_line_comments(text: str) -> str:
    """Remove // comments, respecting quoted strings."""
    out_lines = []
    for line in text.splitlines():
        buf, in_str, instr, i = [], False, "", 0
        while i < len(line):
            ch = line[i]
            if in_str:
                buf.append(ch)
                if ch == instr and (i == 0 or line[i - 1] != "\\"):
                    in_str = False
            elif ch in ("'", '"'):
                in_str, instr = True, ch
                buf.append(ch)
            elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break  # rest of the line is a comment
            else:
                buf.append(ch)
            i += 1
        out_lines.append("".join(buf))
    return "\n".join(out_lines)


def check_balanced(text: str) -> list[str]:
    errors, stack = [], []
    in_str, instr, line = False, "", 1
    i = 0
    text = strip_line_comments(text)
    while i < len(text):
        ch = text[i]
        if ch == "\n":
            line += 1
        if in_str:
            if ch == instr and text[i - 1] != "\\":
                in_str = False
        elif ch in ("'", '"'):
            in_str, instr = True, ch
        elif ch in PAIRS:
            stack.append((ch, line))
        elif ch in PAIRS.values():
            if not stack:
                errors.append(f"line {line}: unmatched closing {ch!r}")
            else:
                op, ol = stack.pop()
                if PAIRS[op] != ch:
                    errors.append(
                        f"line {line}: {ch!r} closes {op!r} opened on line {ol}")
        i += 1
    for op, ol in stack:
        errors.append(f"line {ol}: unclosed {op!r}")
    return errors


def check_file(path: Path) -> list[str]:
    text = path.read_text()
    errors = check_balanced(text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    head = lines[:6]
    if not any(ln.startswith("// Query:") for ln in head):
        errors.append("missing documentation header ('// Query: ...')")
    if not any(ln.lstrip().startswith("// Purpose:") for ln in lines):
        errors.append("missing '// Purpose:' line in header")
    if "|" not in text:
        errors.append("no pipeline operator '|' found")
    if lines and lines[-1].rstrip().endswith("|"):
        errors.append("file ends with a dangling pipe")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="queries")
    args = ap.parse_args()
    ok, failed = 0, 0
    for path in sorted(Path(args.dir).glob("*.kql")):
        errors = check_file(path)
        if errors:
            failed += 1
            print(f"[FAIL] {path.name}")
            for e in errors:
                print(f"       - {e}")
        else:
            ok += 1
            print(f"[ OK ] {path.name}")
    print(f"\n{ok} passed, {failed} failed "
          f"(structural check only — run against a live workspace per docs/lab-setup.md)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
