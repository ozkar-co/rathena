#!/usr/bin/env python3
"""Download NPC sprite previews for the OzRo encyclopedia.

Sprites are sourced from https://nn.ai4rei.net/dev/npclist/ and cached
locally. The script is a one-shot job: it reads the generated inventory,
resolves numeric sprite IDs and sprite names, downloads the GIFs, and
writes a small index for the web frontend.

The site loads only the index once and then one NPC/map JSON at a time;
images use native lazy loading. No bulk JSON is fetched by the browser.

Please keep the default delays. The upstream site allows moderate use but
asks not to hammer it; this script caches every query and every image.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

BASE = "https://nn.ai4rei.net/dev/npclist/"
SEARCH_URL = BASE + "?{query}"
DEFAULT_UA = "OzRo-NPC-Directory/1.0 (private Ragnarok server; low-volume, cached)"
INVISIBLE = {"-1", "HIDDEN_WARP_NPC", "WARPNPC", "CLEAR_NPC", "INVISIBLE", ""}

IMG_RE = re.compile(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>')
NAME_RE = re.compile(r"<br>([^<]+)<span")
ID_RE = re.compile(r"ID:\s*(\d+)")
WIDTH_RE = re.compile(r'width="(\d+)"')
HEIGHT_RE = re.compile(r'height="(\d+)"')


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_filename(key: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", key).strip("._-")
    return base or "sprite"


def parse_entries(page: str) -> list[dict]:
    entries: list[dict] = []
    for chunk in page.split('<div class="npc-brdr">')[1:]:
        image = IMG_RE.search(chunk)
        if not image:
            continue
        name_match = NAME_RE.search(chunk)
        id_match = ID_RE.search(chunk)
        if not id_match:
            continue
        width_match = WIDTH_RE.search(chunk)
        height_match = HEIGHT_RE.search(chunk)
        entries.append(
            {
                "id": int(id_match.group(1)),
                "name": html.unescape(name_match.group(1)).strip() if name_match else "",
                "image": image.group(1),
                "alt": html.unescape(image.group(2)).strip(),
                "width": int(width_match.group(1)) if width_match else None,
                "height": int(height_match.group(1)) if height_match else None,
            }
        )
    return entries


class Fetcher:
    def __init__(self, cache_dir: str, user_agent: str, timeout: int = 30):
        self.cache_dir = cache_dir
        self.user_agent = user_agent
        self.timeout = timeout
        os.makedirs(cache_dir, exist_ok=True)

    def _cache_path(self, namespace: str, key: str) -> str:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{namespace}-{digest}")

    def _request(self, url: str, headers: dict[str, str]) -> tuple[bytes, str]:
        for attempt in range(3):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.read(), response.headers.get_content_type()
            except urllib.error.HTTPError as error:
                if error.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise
            except urllib.error.URLError:
                if attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise
        raise OSError("request failed")

    def search(self, query: str, refresh: bool = False) -> str:
        path = self._cache_path("search", query)
        if os.path.isfile(path) and not refresh:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read()
        url = BASE + "?" + urllib.parse.urlencode(
            {"q": query, "qq": "search", "s": "kro"}
        )
        data, _ = self._request(
            url,
            {
                "User-Agent": self.user_agent,
                "Accept": "text/html,image/*;q=0.9,*/*;q=0.8",
            },
        )
        page = data.decode("utf-8", errors="replace")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(page)
        return page

    def image(self, relative_url: str, refresh: bool = False) -> tuple[bytes, str] | None:
        path = self._cache_path("image", relative_url)
        type_path = path + ".type"
        if os.path.isfile(path) and not refresh:
            with open(path, "rb") as handle:
                data = handle.read()
            extension = ".gif"
            if os.path.isfile(type_path):
                with open(type_path, "r", encoding="ascii") as handle:
                    extension = handle.read().strip() or extension
            else:
                extension = os.path.splitext(relative_url)[1] or extension
            return data, extension
        url = urllib.parse.urljoin(BASE, relative_url)
        try:
            data, content_type = self._request(
                url,
                {
                    "User-Agent": self.user_agent,
                    "Accept": "image/*",
                    # The upstream image handler requires a same-site referer.
                    "Referer": BASE,
                },
            )
        except OSError:
            return None
        if not content_type.startswith("image/"):
            return None
        extension = {
            "image/gif": ".gif",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/jpeg": ".jpg",
        }.get(content_type, os.path.splitext(relative_url)[1] or ".gif")
        with open(path, "wb") as handle:
            handle.write(data)
        with open(type_path, "w", encoding="ascii") as handle:
            handle.write(extension)
        return data, extension


def load_keys(inventory_path: str) -> list[str]:
    with open(inventory_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    keys: set[str] = set()
    for npc in payload.get("npcs", []):
        sprite = str(npc.get("sprite") or "").strip()
        if sprite and sprite not in INVISIBLE:
            keys.add(sprite)
    return sorted(keys, key=lambda value: (not value.isdigit(), value))


def write_index(path: str, sprites: dict, missing: list[dict], counts: dict) -> None:
    payload = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "source": BASE,
        "attribution": "Sprites © Gravity Co., Ltd. — datos de sprite: nn.ai4rei.net/dev/npclist/",
        "counts": counts,
        "sprites": sprites,
        "missing": missing,
    }
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")
    os.replace(temp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory",
        default="/tmp/ozro-npc-inventory/inventory.json",
        help="F1 inventory JSON",
    )
    parser.add_argument(
        "--out",
        default="/tmp/ozro-npc-inventory/web/sprites",
        help="sprite output directory",
    )
    parser.add_argument(
        "--cache",
        default="/tmp/ozro-npc-sprite-cache",
        help="raw HTTP cache",
    )
    parser.add_argument("--delay", type=float, default=1.5, help="seconds between searches")
    parser.add_argument(
        "--image-delay", type=float, default=0.5, help="seconds between image downloads"
    )
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument("--user-agent", default=DEFAULT_UA, help="HTTP User-Agent")
    parser.add_argument("--limit", type=int, default=0, help="only process N keys (testing)")
    parser.add_argument("--only", default="", help="comma-separated sprite keys (testing)")
    parser.add_argument("--refresh", action="store_true", help="ignore caches")
    parser.add_argument("--retry-missing", action="store_true", help="retry previously missing")
    args = parser.parse_args()

    if not os.path.isfile(args.inventory):
        print(f"error: no existe {args.inventory}", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    index_path = os.path.join(args.out, "index.json")

    existing: dict = {}
    missing: list[dict] = []
    if os.path.isfile(index_path) and not args.refresh:
        with open(index_path, "r", encoding="utf-8") as handle:
            previous = json.load(handle)
        existing = previous.get("sprites", {})
        missing = previous.get("missing", [])
    existing_missing = {item.get("key") for item in missing}

    all_keys = load_keys(args.inventory)
    key_set = set(all_keys)
    existing = {key: value for key, value in existing.items() if key in key_set}
    missing = [item for item in missing if item.get("key") in key_set]

    keys = all_keys
    if args.only:
        wanted = {value.strip() for value in args.only.split(",") if value.strip()}
        keys = [key for key in keys if key in wanted]
    if args.limit > 0:
        keys = keys[: args.limit]

    def already_done(key: str) -> bool:
        if key in existing:
            file_path = os.path.join(args.out, existing[key]["file"])
            if os.path.isfile(file_path):
                return True
        if key in existing_missing and not args.retry_missing:
            return True
        return False

    pending = [key for key in keys if not already_done(key)]
    numeric = [key for key in pending if key.isdigit()]
    named = [key for key in pending if not key.isdigit()]

    print(f"claves: {len(keys)} | pendientes: {len(pending)} ({len(numeric)} ids, {len(named)} nombres)")

    fetcher = Fetcher(args.cache, args.user_agent, args.timeout)
    assigned: dict[str, str] = {}
    for key, item in existing.items():
        assigned.setdefault(item["file"].casefold(), key)

    def assign_file(key: str, extension: str) -> str:
        base = safe_filename(key)
        candidate = base + extension
        if candidate.casefold() in assigned and assigned[candidate.casefold()] != key:
            candidate = f"{base}-{hashlib.sha1(key.encode()).hexdigest()[:6]}{extension}"
        assigned[candidate.casefold()] = key
        return candidate

    def resolve_and_store(key: str, entry: dict) -> bool:
        image = fetcher.image(entry["image"], refresh=args.refresh)
        if image is None:
            missing.append({"key": key, "reason": "image download failed", "image": entry["image"]})
            return False
        data, extension = image
        filename = assign_file(key, extension)
        with open(os.path.join(args.out, filename), "wb") as handle:
            handle.write(data)
        existing[key] = {
            "file": filename,
            "w": entry.get("width"),
            "h": entry.get("height"),
            "id": entry.get("id"),
            "name": entry.get("name") or entry.get("alt"),
        }
        missing[:] = [item for item in missing if item.get("key") != key]
        return True

    def save_progress() -> None:
        counts = {
            "keys": len(all_keys),
            "sprites": len(existing),
            "missing": len(missing),
        }
        write_index(index_path, existing, missing, counts)

    # Numeric IDs support batched searches (id;id;id), which keeps requests low.
    batch_size = 40
    for start in range(0, len(numeric), batch_size):
        batch = numeric[start : start + batch_size]
        query = ";".join(batch)
        page = fetcher.search(query, refresh=args.refresh)
        by_id = {entry["id"]: entry for entry in parse_entries(page)}
        for key in batch:
            entry = by_id.get(int(key))
            if entry is None:
                missing.append({"key": key, "reason": "id not found"})
                continue
            resolve_and_store(key, entry)
            time.sleep(args.image_delay)
        save_progress()
        print(f"  ids {start + len(batch)}/{len(numeric)}")
        time.sleep(args.delay)

    for position, key in enumerate(named, 1):
        page = fetcher.search(key, refresh=args.refresh)
        entries = parse_entries(page)
        match = next(
            (
                entry
                for entry in entries
                if entry["name"].casefold() == key.casefold()
                or entry["alt"].casefold() == key.casefold()
            ),
            None,
        )
        if match is None:
            missing.append({"key": key, "reason": "sprite name not found"})
        else:
            resolve_and_store(key, match)
            time.sleep(args.image_delay)
        if position % 25 == 0:
            save_progress()
            print(f"  nombres {position}/{len(named)}")
        time.sleep(args.delay)

    save_progress()
    print(f"sprites: {len(existing)} | missing: {len(missing)}")
    print(f"index:   {index_path}")
    print(f"archivos:{args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
