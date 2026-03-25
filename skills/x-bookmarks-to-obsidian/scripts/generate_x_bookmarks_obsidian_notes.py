import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo


def env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


def local_timezone():
    configured = os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_TIMEZONE", "").strip()
    if configured:
        try:
            return ZoneInfo(configured)
        except Exception:
            pass
    return datetime.now().astimezone().tzinfo or timezone.utc


SOURCE_JSON = env_path("X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON", "~/.dev-browser/tmp/x-bookmarks-to-obsidian-export.json")
TARGET_DIR = env_path("X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR", "~/Obsidian/X Bookmarks to Obsidian")
INDEX_FILE = TARGET_DIR / "000 - X 书签索引.md"
STATE_FILE = env_path("X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE", str(TARGET_DIR / ".x_bookmarks_to_obsidian_state.json"))
LLM_OVERRIDES_FILE = env_path("X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE", "~/.dev-browser/tmp/x-bookmarks-to-obsidian-llm-overrides.json")
STATE_SEQUENCE_MODE = "x-bookmarks-to-obsidian-v1"
COMPATIBLE_SEQUENCE_MODES = {STATE_SEQUENCE_MODE, "bookmark-list-order-v1"}
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

TAG_RULES = [
    (("skill", "skills", "技能"), "skills"),
    (("agent", "agents", "智能体", "代理"), "agents"),
    (("automation", "自动化"), "automation"),
    (("workflow", "工作流"), "workflow"),
    (("llm", "大模型"), "llm"),
    (("claude",), "claude"),
    (("codex",), "codex"),
    (("cursor",), "cursor"),
    (("gemini",), "gemini"),
    (("openclaw",), "openclaw"),
    (("mem9", "记忆", "memory"), "memory"),
    (("playwright",), "playwright"),
    (("browser", "浏览器"), "browser-automation"),
    (("爬虫", "scraping", "scraper"), "web-scraping"),
    (("test", "testing", "测试"), "testing"),
    (("github", "开源", "open source", "opensource"), "open-source"),
    (("mac", "macos"), "macos"),
    (("ios", "xcode", "app store"), "ios"),
    (("obsidian",), "obsidian"),
    (("video", "视频"), "video"),
    (("design", "设计"), "design"),
    (("search", "检索"), "search"),
    (("tutorial", "教程", "学习"), "learning"),
    (("cli",), "cli"),
    (("telegram",), "telegram"),
    (("discord",), "discord"),
    (("飞书", "feishu"), "feishu"),
    (("api",), "api"),
    (("paper", "论文"), "papers"),
    (("document", "文档", "pandoc"), "documents"),
    (("ui", "界面"), "ui"),
    (("desktop", "桌面"), "desktop"),
    (("prompt", "提示词"), "prompts"),
]


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


def parse_status_datetime(status_id: str) -> Optional[datetime]:
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


def load_llm_overrides():
    if not LLM_OVERRIDES_FILE.exists():
        return {}
    try:
        data = json.loads(LLM_OVERRIDES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if isinstance(data, dict) and isinstance(data.get("entries"), dict):
        data = data["entries"]
    return data if isinstance(data, dict) else {}


def item_override(item, overrides):
    if not isinstance(overrides, dict):
        return {}
    return overrides.get(item.get("statusLink", ""), {})


def derive_title(item, overrides=None):
    override = item_override(item, overrides)
    custom_title = str(override.get("title", "")).strip()
    if custom_title:
        return custom_title

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


def format_summary_lines(summary_lines):
    clean = []
    for line in summary_lines:
        text = str(line).strip()
        if not text:
            continue
        clean.append(text.removeprefix("- ").strip())
        if len(clean) >= 3:
            break
    return "\n".join(f"- {part}" for part in clean)


def derive_tags(item, title, summary, overrides=None):
    override = item_override(item, overrides)
    custom_tags = override.get("tags")
    if isinstance(custom_tags, str) and custom_tags.strip():
        tags = [part.strip().lstrip("#") for part in re.split(r"[,\n]+", custom_tags) if part.strip()]
        if tags:
            return tags[:6]
    if isinstance(custom_tags, list):
        tags = [str(part).strip().lstrip("#") for part in custom_tags if str(part).strip()]
        if tags:
            return tags[:6]

    text = "\n".join(
        [
            title,
            summary.replace("- ", ""),
            item.get("text", ""),
            "\n".join(item.get("links", [])),
        ]
    ).lower()

    tags = ["x-bookmarks-to-obsidian"]
    for keywords, tag in TAG_RULES:
        if any(keyword.lower() in text for keyword in keywords):
            tags.append(tag)
        if len(tags) >= 6:
            break
    return list(dict.fromkeys(tags))


def derive_summary(item, title, overrides=None):
    override = item_override(item, overrides)
    custom_summary = override.get("summary")
    if isinstance(custom_summary, str) and custom_summary.strip():
        lines = [line.strip() for line in custom_summary.splitlines() if line.strip()]
        formatted = format_summary_lines(lines)
        if formatted:
            return formatted
    if isinstance(custom_summary, list):
        formatted = format_summary_lines(custom_summary)
        if formatted:
            return formatted

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


def filename_stem(item, duplicate_index: int = 0, overrides=None) -> str:
    title = derive_title(item, overrides)
    author = item.get("handle", "").lstrip("@") or item.get("author", "unknown")
    status_id = item.get("statusLink", "").rstrip("/").split("/")[-1]
    dt = parse_status_datetime(status_id)
    prefix = dt.strftime("%Y-%m-%d %H%M%S") if dt else (parse_date(item.get("time", "").strip()) or "unknown-date")
    short_title = title[:70].rstrip(" .")
    base = f"{short_title} - {prefix} - {author}"
    if duplicate_index:
        base = f"{base} ({duplicate_index})"
    return base


def note_filename(item, duplicate_index: int = 0, overrides=None) -> str:
    return clean_filename(f"{filename_stem(item, duplicate_index, overrides)}.md")


def note_content(item, overrides=None):
    title = derive_title(item, overrides)
    summary = derive_summary(item, title, overrides)
    tags = derive_tags(item, title, summary, overrides)
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
        "---",
        "tags:",
        *[f"  - {tag}" for tag in tags],
        "---",
        "",
        "## 摘要",
        summary or "- 暂无可提取摘要",
        "",
        "## 标签",
        " ".join(f"#{tag}" for tag in tags),
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


def existing_item_from_note(source: str, meta: dict):
    filename = str(meta.get("filename", "")).strip()
    if not filename:
        return None
    path = TARGET_DIR / filename
    if not path.exists():
        return None

    author = ""
    handle = ""
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line.startswith("- 作者："):
                continue
            payload = line.removeprefix("- 作者：").strip()
            match = re.fullmatch(r"(.+?) \((@[^)]+)\)", payload)
            if match:
                author = match.group(1).strip()
                handle = match.group(2).strip()
            else:
                author = payload
            break
    except Exception:
        return None

    return {
        "statusLink": source,
        "author": author,
        "handle": handle,
        "time": "",
    }


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
    overrides = load_llm_overrides()

    state = load_state()
    previous_entries = state.get("entries", {})
    sequence_mode = state.get("sequence_mode")
    rebuild_sequences = not previous_entries or sequence_mode not in COMPATIBLE_SEQUENCE_MODES

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
        filename = clean_filename(f"{sequence:0{width}d} - {filename_stem(item, overrides=overrides)}.md")
        target = TARGET_DIR / filename
        target.write_text(note_content(item, overrides), encoding="utf-8")
        created.append(str(target))
        desired_names.add(filename)
        ordered_entries.append((sequence, item, filename))
        new_state_entries[source] = {
            "sequence": sequence,
            "filename": filename,
        }

    if not rebuild_sequences:
        for source, previous in previous_entries.items():
            if source in new_state_entries or not valid_sequence(previous):
                continue
            filename = str(previous.get("filename", "")).strip()
            if not filename:
                continue
            existing_item = existing_item_from_note(source, previous)
            if existing_item is None:
                continue
            desired_names.add(filename)
            ordered_entries.append((int(previous["sequence"]), existing_item, filename))
            new_state_entries[source] = {
                "sequence": int(previous["sequence"]),
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
                "count": len(new_state_entries),
                "source_json": str(SOURCE_JSON),
                "llm_overrides_file": str(LLM_OVERRIDES_FILE) if LLM_OVERRIDES_FILE.exists() else "",
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
