import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


def local_timezone():
    configured = os.environ.get("X_BOOKMARKS_TIMEZONE", "").strip()
    if configured:
        try:
            return ZoneInfo(configured)
        except Exception:
            pass
    return datetime.now().astimezone().tzinfo or timezone.utc


SOURCE_JSON = env_path("X_BOOKMARKS_SOURCE_JSON", "~/.dev-browser/tmp/x-bookmarks-export.json")
TARGET_DIR = env_path("X_BOOKMARKS_TARGET_DIR", "~/Obsidian/X Bookmarks")
INDEX_FILE = TARGET_DIR / "000 - X 书签索引.md"
STATE_FILE = env_path("X_BOOKMARKS_STATE_FILE", str(TARGET_DIR / ".x_bookmarks_state.json"))
STATE_SEQUENCE_MODE = "bookmark-list-order-v1"
LOCAL_TZ = local_timezone()
TWITTER_EPOCH_MS = 1288834974657

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def is_metric(line: str) -> bool:
    return bool(re.fullmatch(r"[\d,.]+[KMB]?", line))


def is_urlish(line: str) -> bool:
    return (
        line.startswith("http://")
        or line.startswith("https://")
        or line == "github.com"
        or line.endswith(".com")
        or line == "From github.com"
    )


def is_time_label(line: str) -> bool:
    return bool(
        re.fullmatch(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,\s*\d{4})?|\d+[smhd]|\d{1,2}h",
            line,
        )
    )


def parse_date(raw: str) -> str:
    now = datetime.now(LOCAL_TZ)
    raw = raw.strip()
    if not raw:
        return ""
    if re.fullmatch(r"\d+h", raw):
        hours = int(raw[:-1])
        return (now - timedelta(hours=hours)).date().isoformat()
    if re.fullmatch(r"\d+m", raw):
        minutes = int(raw[:-1])
        return (now - timedelta(minutes=minutes)).date().isoformat()
    if re.fullmatch(r"\d+s", raw):
        seconds = int(raw[:-1])
        return (now - timedelta(seconds=seconds)).date().isoformat()
    match = re.fullmatch(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:,\s*(\d{4}))?", raw)
    if match:
        month = MONTHS[match.group(1)]
        day = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else now.year
        return datetime(year, month, day).date().isoformat()
    return raw


def parse_status_datetime(status_id: str) -> datetime | None:
    if not status_id.isdigit():
        return None
    timestamp_ms = (int(status_id) >> 22) + TWITTER_EPOCH_MS
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).astimezone(LOCAL_TZ)


def content_lines(lines):
    out = []
    skip_values = {
        "·",
        "Replying to",
        "Quote",
        "Show more",
        "Article",
        "Paid partnership",
        "From github.com",
        "Translated from Japanese",
    }
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line in skip_values:
            continue
        if line.startswith("@"):
            continue
        if is_time_label(line):
            continue
        if is_metric(line):
            continue
        if is_urlish(line):
            continue
        out.append(line)
    return out


def derive_title(item):
    lines = content_lines(item.get("lines", []))
    author = item.get("author", "").strip()
    filtered = [line for line in lines if line != author]
    if not filtered:
        return f"{item.get('handle', '').lstrip('@') or author or 'X Bookmark'} 书签"
    skip_prefixes = {"GitHub：", "Github", "Github地址：", "安装地址：", "浏览查找Youtube ：", "下载Youtube视频和字幕："}
    for idx, line in enumerate(filtered):
        if line in skip_prefixes:
            continue
        if line == "好消息" and idx + 1 < len(filtered):
            return filtered[idx + 1]
        return line
    return filtered[0]


def derive_summary(item, title):
    lines = content_lines(item.get("lines", []))
    author = item.get("author", "").strip()
    filtered = [line for line in lines if line != author]
    body = [line for line in filtered if line != title]

    summary_parts = []
    skip_summary_lines = {
        "GitHub：",
        "Github",
        "Github地址：",
        "安装地址：",
        "浏览查找Youtube ：",
        "下载Youtube视频和字幕：",
        "Replying to",
        "From github.com",
        "Quote",
    }
    for line in body:
        if line in summary_parts or line in skip_summary_lines:
            continue
        if len(summary_parts) >= 3:
            break
        summary_parts.append(line)

    if not summary_parts:
        text = item.get("text", "")
        raw_lines = [segment.strip() for segment in text.split("\n") if segment.strip()]
        for line in raw_lines:
            if (
                line not in {author, item.get("handle", "").strip(), title, item.get("time", "").strip(), "·"}
                and line not in skip_summary_lines
                and not is_urlish(line)
                and not is_metric(line)
            ):
                summary_parts.append(line)
            if len(summary_parts) >= 3:
                break

    if not summary_parts:
        summary_parts = ["这条书签主要指向外部资源，核心信息请看来源链接和原文摘录。"]

    return "\n".join(f"- {part}" for part in summary_parts[:3])


def clean_filename(name: str) -> str:
    stem, ext = (name.rsplit(".", 1) + [""])[:2]
    ext = f".{ext}" if ext else ""
    stem = re.sub(r"[\\/:*?\"<>|#\n\r]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    stem = stem[:120].rstrip(" .")
    return f"{stem}{ext}"


def filename_stem(item, duplicate_index: int = 0) -> str:
    title = derive_title(item)
    author = item.get("handle", "").lstrip("@") or item.get("author", "unknown")
    status_id = item.get("statusLink", "").rstrip("/").split("/")[-1]
    dt = parse_status_datetime(status_id)
    prefix = dt.strftime("%Y-%m-%d %H%M%S") if dt else (parse_date(item.get("time", "").strip()) or "unknown-date")
    short_title = title[:70].rstrip(" .")
    base = f"{short_title} - {prefix} - {author}"
    if duplicate_index:
        base = f"{base} ({duplicate_index})"
    return base


def note_filename(item, duplicate_index: int = 0) -> str:
    return clean_filename(f"{filename_stem(item, duplicate_index)}.md")


def note_content(item):
    title = derive_title(item)
    summary = derive_summary(item, title)
    source = item.get("statusLink", "")
    author = item.get("author", "").strip()
    handle = item.get("handle", "").strip()
    raw_date = item.get("time", "").strip()
    parsed_date = parse_date(raw_date)
    status_id = source.rstrip("/").split("/")[-1] if source else ""
    status_dt = parse_status_datetime(status_id)
    links = [link for link in item.get("links", []) if link and not link.endswith("/analytics")]
    raw_excerpt = item.get("text", "").strip()
    exact_time = status_dt.strftime("%Y-%m-%d %H:%M:%S %Z") if status_dt else ""

    lines = [
        "## 摘要",
        summary or "- 暂无可提取摘要",
        "",
        "## 来源",
        f"- 作者：{author} ({handle})",
        f"- 时间：{parsed_date or raw_date}",
        f"- 精确时间：{exact_time}" if exact_time else None,
        f"- 链接：{source}",
    ]
    lines = [line for line in lines if line is not None]

    if links:
        lines.extend([
            "",
            "## 相关链接",
            *[f"- {link}" for link in links[:8]],
        ])

    lines.extend([
        "",
        "## 原文摘录",
        "```text",
        raw_excerpt[:2500],
        "```",
        "",
    ])
    return "\n".join(lines)


def index_content(ordered_entries):
    total = len(ordered_entries)
    width = max(3, len(str(total))) if total else 3
    lines = [
        "# X 书签索引",
        "",
        f"- 同步时间：{datetime.now(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- 书签总数：{total}",
        "",
        "## 条目",
    ]

    for sequence, item, filename in ordered_entries:
        source = item.get("statusLink", "")
        author = item.get("author", "").strip()
        handle = item.get("handle", "").strip()
        status_id = source.rstrip("/").split("/")[-1] if source else ""
        status_dt = parse_status_datetime(status_id)
        exact_time = status_dt.strftime("%Y-%m-%d %H:%M:%S") if status_dt else (parse_date(item.get("time", "").strip()) or item.get("time", "").strip())

        lines.extend(
            [
                f"{sequence:0{width}d}. [[{Path(filename).stem}]]",
                f"   时间：{exact_time}",
                f"   作者：{author} ({handle})",
                f"   原帖：{source}",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def load_state():
    if not STATE_FILE.exists():
        return {"entries": {}}
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"entries": {}}
    if not isinstance(state, dict) or not isinstance(state.get("entries"), dict):
        return {"entries": {}}
    return state


def valid_sequence(meta):
    return isinstance(meta, dict) and str(meta.get("sequence", "")).isdigit()


def main():
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    bookmark_items = [item for item in data if item.get("statusLink")]

    state = load_state()
    previous_entries = state.get("entries", {})
    sequence_mode = state.get("sequence_mode")
    rebuild_sequences = not previous_entries or sequence_mode != STATE_SEQUENCE_MODE

    created = []
    desired_names = set()
    ordered_entries = []
    new_state_entries = {}

    assigned_sequences = {}
    if rebuild_sequences:
        for sequence, item in enumerate(reversed(bookmark_items), start=1):
            assigned_sequences[item.get("statusLink", "")] = sequence
        next_sequence = len(assigned_sequences) + 1
    else:
        existing_sequences = [
            int(meta.get("sequence"))
            for meta in previous_entries.values()
            if valid_sequence(meta)
        ]
        next_sequence = (max(existing_sequences) + 1) if existing_sequences else 1
        for item in reversed(bookmark_items):
            source = item.get("statusLink", "")
            previous = previous_entries.get(source, {})
            if valid_sequence(previous):
                assigned_sequences[source] = int(previous["sequence"])
            else:
                assigned_sequences[source] = next_sequence
                next_sequence += 1

    max_sequence = max(assigned_sequences.values(), default=0)
    width = max(3, len(str(max(max_sequence, 999))))

    for item in bookmark_items:
        source = item.get("statusLink", "")
        sequence = assigned_sequences[source]
        filename = clean_filename(f"{sequence:0{width}d} - {filename_stem(item)}.md")
        target = TARGET_DIR / filename
        target.write_text(note_content(item), encoding="utf-8")
        created.append(str(target))
        desired_names.add(filename)
        ordered_entries.append((sequence, item, filename))
        new_state_entries[source] = {
            "sequence": sequence,
            "filename": filename,
        }

    desired_names.add(INDEX_FILE.name)
    desired_names.add(STATE_FILE.name)

    for old_file in TARGET_DIR.iterdir():
        if old_file.is_file() and old_file.name not in desired_names:
            old_file.unlink()

    ordered_entries.sort(key=lambda entry: entry[0])
    INDEX_FILE.write_text(index_content(ordered_entries), encoding="utf-8")
    STATE_FILE.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(LOCAL_TZ).isoformat(),
                "count": len(bookmark_items),
                "source_json": str(SOURCE_JSON),
                "sequence_mode": STATE_SEQUENCE_MODE,
                "entries": new_state_entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(json.dumps({"count": len(created), "sample": created[:5]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
