#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


REPO_DIR = Path(__file__).resolve().parents[1]
SOURCE_JSON = env_path("X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON", "~/.dev-browser/tmp/x-bookmarks-to-obsidian-export.json")
OVERRIDES_FILE = env_path("X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE", "~/.dev-browser/tmp/x-bookmarks-to-obsidian-llm-overrides.json")
MODEL = os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_LLM_MODEL", "gpt-5.4").strip() or "gpt-5.4"
BATCH_SIZE = max(1, int(os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_LLM_BATCH_SIZE", "12")))
RETRIES = max(0, int(os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_LLM_RETRIES", "2")))
RESUME = os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_LLM_RESUME", "1") == "1"

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["items"],
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "title", "summary", "tags"],
                "properties": {
                    "key": {"type": "string"},
                    "title": {"type": "string"},
                    "summary": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 4,
                        "items": {"type": "string"},
                    },
                    "tags": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 6,
                        "items": {"type": "string"},
                    },
                },
            },
        }
    },
}

PROMPT_PREFIX = """You are organizing X bookmarks into Obsidian notes.
For each bookmark JSON entry, produce a higher-signal title, summary, and tags.

Requirements:
1. Return one output item for every input item, preserving the exact key.
2. Title must be concise Chinese, filename-friendly, and should not include author, time, or metrics.
3. Prefer the core project, tool, article, or claim over mechanically copying the first visible line.
4. Summary must contain 2 to 4 Chinese bullet-style sentences with concrete signal, not filler.
5. Tags must contain 2 to 6 lowercase short labels in English or pinyin kebab-case.
6. Do not invent facts. If information is thin, summarize conservatively.
7. When a post recommends a tool, project, article, tutorial, or workflow, make the practical value explicit.
8. Output must strictly match the schema.

Input bookmark JSON list:
"""


def compact_item(item: dict) -> dict:
    links = []
    for link in item.get("links") or []:
        if link.endswith("/analytics"):
            continue
        if link not in links:
            links.append(link)

    lines = []
    for line in item.get("lines") or []:
        text = " ".join(str(line).split())
        if text:
            lines.append(text)

    return {
        "key": item.get("key") or item.get("statusLink", ""),
        "author": item.get("author", ""),
        "handle": item.get("handle", ""),
        "time": item.get("time", ""),
        "text": item.get("text", ""),
        "lines": lines,
        "links": links,
    }


def load_items() -> list[dict]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError(f"Expected a list in {SOURCE_JSON}")
    return data


def load_existing_entries() -> dict:
    if not RESUME or not OVERRIDES_FILE.exists():
        return {}
    try:
        data = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    entries = data.get("entries", data)
    return entries if isinstance(entries, dict) else {}


def run_batch(batch_items: list[dict], batch_index: int, total_batches: int, tmpdir: Path) -> list[dict]:
    schema_path = tmpdir / "schema.json"
    output_path = tmpdir / f"output-{batch_index:03d}.json"
    schema_path.write_text(json.dumps(SCHEMA, ensure_ascii=False), encoding="utf-8")

    payload = [compact_item(item) for item in batch_items]
    prompt = PROMPT_PREFIX + json.dumps(payload, ensure_ascii=False)
    expected_keys = [item.get("key") or item.get("statusLink", "") for item in batch_items]

    cmd = [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--color",
        "never",
        "-m",
        MODEL,
        "--output-schema",
        str(schema_path),
        "-C",
        str(REPO_DIR),
        "-o",
        str(output_path),
        "-",
    ]

    for attempt in range(1, RETRIES + 2):
        started = time.time()
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=900,
        )
        elapsed = time.time() - started
        if proc.returncode == 0 and output_path.exists():
            try:
                data = json.loads(output_path.read_text(encoding="utf-8"))
                items = data["items"]
                keys = [item["key"] for item in items]
                if sorted(keys) != sorted(expected_keys):
                    raise RuntimeError("returned keys did not match input keys")
                print(f"batch {batch_index + 1}/{total_batches} ok in {elapsed:.1f}s", file=sys.stderr)
                return items
            except Exception as exc:
                error = f"parse/validate failed: {exc}"
        else:
            error = f"command failed rc={proc.returncode}"

        tail = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-2000:]
        print(f"batch {batch_index + 1}/{total_batches} attempt {attempt} failed: {error}", file=sys.stderr)
        if tail.strip():
            print(tail, file=sys.stderr)
        time.sleep(2)

    raise RuntimeError(f"batch {batch_index + 1} failed after retries")


def main() -> int:
    if not SOURCE_JSON.exists():
        print(f"Missing source JSON: {SOURCE_JSON}", file=sys.stderr)
        return 1

    if shutil.which("codex") is None:
        print("codex CLI is required for standalone shell automation when X_BOOKMARKS_TO_OBSIDIAN_USE_LLM=1", file=sys.stderr)
        return 1

    items = load_items()
    source_keys = [item.get("key") or item.get("statusLink", "") for item in items]
    source_key_set = {key for key in source_keys if key}
    entries = {
        key: value
        for key, value in load_existing_entries().items()
        if key in source_key_set
    }
    pending = [item for item in items if (item.get("key") or item.get("statusLink", "")) not in entries]
    total = len(items)
    OVERRIDES_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not pending:
        OVERRIDES_FILE.write_text(
            json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps({"count": total, "overrides_file": str(OVERRIDES_FILE)}, ensure_ascii=False))
        return 0

    total_batches = (len(pending) + BATCH_SIZE - 1) // BATCH_SIZE
    with tempfile.TemporaryDirectory(prefix="x-bookmarks-to-obsidian-codex-") as raw_tmpdir:
        tmpdir = Path(raw_tmpdir)
        for batch_index in range(total_batches):
            batch = pending[batch_index * BATCH_SIZE : (batch_index + 1) * BATCH_SIZE]
            result = run_batch(batch, batch_index, total_batches, tmpdir)
            for item in result:
                entries[item["key"]] = {
                    "title": item["title"].strip(),
                    "summary": [line.strip() for line in item["summary"] if line.strip()],
                    "tags": [tag.strip().lstrip("#") for tag in item["tags"] if tag.strip()],
                }
            OVERRIDES_FILE.write_text(
                json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"checkpoint {len(entries)}/{total} saved to {OVERRIDES_FILE}", file=sys.stderr)

    resolved = sum(1 for key in source_keys if key in entries)
    if resolved != total:
        print(f"Expected {total} overrides, got {resolved}", file=sys.stderr)
        return 1

    print(json.dumps({"count": total, "overrides_file": str(OVERRIDES_FILE)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
