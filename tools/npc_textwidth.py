#!/usr/bin/env python3
"""Count the dialog lines the client renders for NPC 'mes' text.

The 2019-06-05 client wraps NPC dialog text at a fixed 34 visible
characters per line, greedy by word, hard-cutting words longer than
the limit and dropping the space where a line breaks. Color codes
(^RRGGBB) and <INFO>...</INFO> data are not rendered and do not count.
The wrap is independent of the dialog window width.

Examples:
  python3 tools/npc_textwidth.py npc/custom/ozro/warps/yuno.txt
  python3 tools/npc_textwidth.py npc/custom/ozro/warps
  python3 tools/npc_textwidth.py --text "Cool Event Corp fue designada para operar."
"""

from __future__ import annotations

import argparse
import os
import re
import sys

LINE_LIMIT = 34

COLOR_CODE_RE = re.compile(r"\^[0-9A-Fa-f]{6}")
INFO_RE = re.compile(r"<INFO>.*?</INFO>", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
NPC_START_RE = re.compile(
    r"^\s*(?:-|[^,\s]+,\s*-?\d+,\s*-?\d+(?:,\s*-?\d+)?)\s+(?:script|shop|etc)\b",
    re.IGNORECASE,
)
MES_RE = re.compile(r"\bmes\b(.*?);", re.IGNORECASE | re.DOTALL)
STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def visible_text(raw: str) -> str:
    """Return the characters the client counts for line wrapping."""
    text = COLOR_CODE_RE.sub("", raw)
    text = INFO_RE.sub("", text)
    text = TAG_RE.sub("", text)
    return text


def wrap_lines(text: str, limit: int = LINE_LIMIT) -> list[str]:
    """Greedy word wrap with the client's hard cut for overlong words."""
    if not text:
        return [""]
    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        while len(word) > limit:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:limit])
            word = word[limit:]
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= limit:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def parse_blocks(source: str) -> list[tuple[str, list[list[str]]]]:
    """Return (npc label, pages) where each page is a list of mes strings."""
    blocks: list[tuple[str, list[list[str]]]] = []
    label = ""
    pages: list[list[str]] = [[]]
    for line in source.splitlines():
        if NPC_START_RE.match(line):
            tokens = line.split()
            kind = next((i for i, t in enumerate(tokens) if t in ("script", "shop", "etc")), None)
            label = " ".join(tokens[kind + 1 : -1]) if kind is not None else ""
            pages = [[]]
            blocks.append((label, pages))
            continue
        if not blocks:
            continue
        stripped = line.strip()
        if stripped.startswith(("next;", "close;", "close2;", "menu ", "select(", "end;")) and pages[-1]:
            pages.append([])
        for match in MES_RE.finditer(line):
            args = match.group(1)
            parts = STRING_RE.findall(args)
            if not parts:
                continue
            if STRING_RE.sub("", args).replace(",", "").strip():
                parts.append("<dynamic>")
            pages[-1].extend(p.replace("\\n", "\n") for p in parts)
    for _, pages in blocks:
        while pages and not pages[-1]:
            pages.pop()
    return [(l, p) for l, p in blocks if p]


def report(path: str, limit: int) -> int:
    with open(path, "r", encoding="latin-1", errors="replace") as handle:
        source = handle.read()
    blocks = parse_blocks(source)
    if not blocks:
        return 0
    print(f"{path}")
    for label, pages in blocks:
        print(f"  {label}")
        for index, mes_list in enumerate(pages, 1):
            total = 0
            details = []
            for mes in mes_list:
                for segment in mes.split("\n"):
                    lines = wrap_lines(visible_text(segment), limit)
                    total += len(lines)
                    details.append((len(visible_text(segment)), len(lines), segment))
            print(f"    pagina {index}: {total} lineas")
            for chars, count, segment in details:
                flag = "  <-- dinamico" if segment == "<dynamic>" else ""
                print(f"      {count} lineas  {chars:3d} chars  {segment}{flag}")
    return len(blocks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="script files or directories")
    parser.add_argument("--text", help="wrap a single string instead of files")
    parser.add_argument("--limit", type=int, default=LINE_LIMIT, help="visible chars per line (default 34)")
    args = parser.parse_args()

    if args.text:
        for line in wrap_lines(visible_text(args.text), args.limit):
            print(line)
        return 0

    files: list[str] = []
    for path in args.paths:
        if os.path.isdir(path):
            for root, _, names in os.walk(path):
                files.extend(os.path.join(root, n) for n in names if n.endswith(".txt"))
        else:
            files.append(path)
    if not files:
        parser.error("no script files given")

    blocks = sum(report(path, args.limit) for path in sorted(files))
    print(f"\n{blocks} NPCs revisados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
