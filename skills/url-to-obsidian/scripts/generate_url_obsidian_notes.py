#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo


def env_path(*names: str, default: str) -> Path:
    for name in names:
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser()
    return Path(default).expanduser()


def local_timezone():
    for name in ("URL_TO_OBSIDIAN_TIMEZONE",):
        configured = os.environ.get(name, "").strip()
        if configured:
            try:
                return ZoneInfo(configured)
            except Exception:
                pass
    return datetime.now().astimezone().tzinfo or timezone.utc


SOURCE_JSON = env_path(
    "URL_TO_OBSIDIAN_SOURCE_JSON",
    default="~/.dev-browser/tmp/url-to-obsidian-export.json",
)
TARGET_DIR = env_path(
    "URL_TO_OBSIDIAN_TARGET_DIR",
    default="~/Obsidian/URL to Obsidian",
)
INDEX_FILE = TARGET_DIR / "000 - URL 采集索引.md"
STATE_FILE = env_path(
    "URL_TO_OBSIDIAN_STATE_FILE",
    default=str(TARGET_DIR / ".url_to_obsidian_state.json"),
)
LLM_OVERRIDES_FILE = env_path(
    "URL_TO_OBSIDIAN_LLM_OVERRIDES_FILE",
    default="~/.dev-browser/tmp/url-to-obsidian-llm-overrides.json",
)
STATE_SEQUENCE_MODE = "url-to-obsidian-v1"
LOCAL_TZ = local_timezone()

TAG_RULES = [
    (("wechat", "微信", "公众号"), "wechat"),
    (("github", "repo", "repository", "pull request", "issue"), "github"),
    (("x.com", "twitter", "tweet", "推文"), "x"),
    (("agent", "agents", "智能体"), "agents"),
    (("automation", "自动化"), "automation"),
    (("workflow", "工作流"), "workflow"),
    (("llm", "大模型"), "llm"),
    (("obsidian",), "obsidian"),
    (("browser", "浏览器"), "browser-automation"),
    (("scraping", "scraper", "爬虫"), "web-scraping"),
    (("api",), "api"),
    (("open source", "opensource", "开源"), "open-source"),
    (("tutorial", "guide", "教程"), "learning"),
    (("prompt", "提示词"), "prompts"),
    (("paper", "论文"), "papers"),
]


def iso_to_local(raw: str) -> str:
    if not raw:
        return ""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return raw


def clean_filename(name: str) -> str:
    stem, ext = (name.rsplit(".", 1) + [""])[:2]
    ext = f".{ext}" if ext else ""
    stem = re.sub(r"[\\/:*?\"<>|#\n\r]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    stem = stem[:120].rstrip(" .")
    return f"{stem}{ext}"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_llm_overrides():
    if not LLM_OVERRIDES_FILE.exists():
        return {}
    try:
        data = load_json(LLM_OVERRIDES_FILE)
    except Exception:
        return {}
    if isinstance(data, dict) and isinstance(data.get("entries"), dict):
        data = data["entries"]
    return data if isinstance(data, dict) else {}


def item_key(item: dict) -> str:
    return item.get("key") or item.get("finalUrl") or item.get("requestedUrl", "")


def item_override(item, overrides):
    return overrides.get(item_key(item), {}) if isinstance(overrides, dict) else {}


def source_type(item: dict) -> str:
    value = str(item.get("sourceType", "")).strip().lower()
    if value and value != "web":
        return value

    host = source_host(item)
    if host == "mp.weixin.qq.com" or host.endswith(".weixin.qq.com"):
        return "wechat"
    if host == "github.com" or host.endswith(".github.com"):
        return "github"
    if host == "x.com" or host.endswith(".x.com") or host == "twitter.com" or host.endswith(".twitter.com"):
        return "x"
    return value or "web"


def source_host(item: dict) -> str:
    url = item.get("finalUrl") or item.get("requestedUrl", "")
    try:
        return urlparse(url).netloc or "unknown-site"
    except Exception:
        return "unknown-site"


def pick_title(item, overrides=None) -> str:
    override = item_override(item, overrides)
    custom_title = str(override.get("title", "")).strip()
    if custom_title:
        return custom_title

    for candidate in (
        item.get("metaTitle", ""),
        item.get("title", ""),
        next(iter(item.get("headings") or []), ""),
        item.get("metaDescription", ""),
    ):
        text = " ".join(str(candidate).split()).strip()
        if text:
            return text[:90]

    host = source_host(item)
    return f"{host} 内容摘录"


def format_summary_lines(summary_lines):
    clean = []
    for line in summary_lines:
        text = str(line).strip().removeprefix("- ").strip()
        if not text or text in clean:
            continue
        clean.append(text)
        if len(clean) >= 3:
            break
    return "\n".join(f"- {part}" for part in clean)


def unique_preserving_order(values):
    seen = set()
    result = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def split_excerpt(excerpt: str) -> list[str]:
    parts = []
    for raw in re.split(r"[\n。！？!?]+", excerpt):
        text = " ".join(raw.split()).strip()
        if len(text) < 8:
            continue
        parts.append(text)
        if len(parts) >= 6:
            break
    return parts


def pick_summary(item, title, overrides=None) -> str:
    override = item_override(item, overrides)
    custom_summary = override.get("summary")
    if isinstance(custom_summary, str) and custom_summary.strip():
        formatted = format_summary_lines(custom_summary.splitlines())
        if formatted:
            return formatted
    if isinstance(custom_summary, list):
        formatted = format_summary_lines(custom_summary)
        if formatted:
            return formatted

    candidates = []
    meta_description = " ".join(str(item.get("metaDescription", "")).split())
    if meta_description:
        candidates.append(meta_description)

    for heading in item.get("headings") or []:
        text = " ".join(str(heading).split()).strip()
        if text and text != title:
            candidates.append(text)

    candidates.extend(split_excerpt(str(item.get("excerpt", "")).strip()))
    if item.get("error"):
        candidates.insert(0, f"页面抓取失败：{item['error']}")

    formatted = format_summary_lines(candidates)
    if formatted:
        return formatted
    return "- 已记录来源链接，建议打开原网页查看完整内容。"


def pick_tags(item, title, summary, overrides=None) -> list[str]:
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
            str(item.get("excerpt", "")),
            str(item.get("metaDescription", "")),
            "\n".join(item.get("headings") or []),
            "\n".join(item.get("links") or []),
        ]
    ).lower()

    tags = ["url-to-obsidian", source_type(item)]
    host = source_host(item)
    if host:
        site_tag = host.replace("www.", "").replace(".", "-")
        if site_tag not in tags:
            tags.append(site_tag)

    for keywords, tag in TAG_RULES:
        if any(keyword.lower() in text for keyword in keywords) and tag not in tags:
            tags.append(tag)
        if len(tags) >= 6:
            break

    return tags[:6]


def note_content(item, overrides=None):
    title = pick_title(item, overrides)
    summary = pick_summary(item, title, overrides)
    tags = pick_tags(item, title, summary, overrides)
    excerpt = str(item.get("excerpt", "")).strip()

    lines = [
        "---",
        "tags:",
        *[f"  - {tag}" for tag in tags],
        f"source_type: {source_type(item)}",
        f"source_host: {source_host(item)}",
        "---",
        "",
        "## 摘要",
        summary,
    ]
    lines = [line for line in lines if line is not None and str(line).strip()]

    if item.get("error"):
        lines.extend([
            "",
            "## 抓取异常",
            f"- {item['error']}",
        ])

    lines.extend([
        "",
        "## 页面摘录",
        "```text",
        excerpt[:4000] if excerpt else "(no excerpt)",
        "```",
        "",
    ])
    return "\n".join(lines)


def index_content(ordered_entries, overrides):
    total = len(ordered_entries)
    width = max(3, len(str(total))) if total else 3
    lines = [
        "# URL 采集索引",
        "",
        f"- 生成时间：{datetime.now(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- 条目总数：{total}",
        "",
        "## 条目",
    ]

    for sequence, item, filename in ordered_entries:
        lines.extend(
            [
                f"{sequence:0{width}d}. [[{Path(filename).stem}]]",
                f"   类型：{source_type(item)}",
                f"   站点：{source_host(item)}",
                f"   标题：{pick_title(item, overrides)}",
                f"   链接：{item.get('finalUrl') or item.get('requestedUrl', '')}",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def load_state():
    if not STATE_FILE.exists():
        return {"entries": {}}
    try:
        state = load_json(STATE_FILE)
    except Exception:
        return {"entries": {}}
    if not isinstance(state, dict) or not isinstance(state.get("entries"), dict):
        return {"entries": {}}
    return state


def valid_sequence(meta):
    return isinstance(meta, dict) and str(meta.get("sequence", "")).isdigit()


def note_filename(item, sequence: int, width: int, overrides) -> str:
    title = pick_title(item, overrides)[:72].rstrip(" .")
    site = source_host(item).replace("www.", "")
    return clean_filename(f"{sequence:0{width}d} - {title} - {site}.md")


def main():
    source_file = SOURCE_JSON
    data = load_json(source_file)
    if not isinstance(data, list):
        raise RuntimeError(f"Expected list data in {source_file}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    overrides = load_llm_overrides()
    state = load_state()
    previous_entries = state.get("entries", {})
    rebuild_sequences = state.get("sequence_mode") != STATE_SEQUENCE_MODE

    assigned_sequences = {}
    if rebuild_sequences:
        for sequence, item in enumerate(data, start=1):
            assigned_sequences[item_key(item)] = sequence
    else:
        existing_sequences = [
            int(meta.get("sequence"))
            for meta in previous_entries.values()
            if valid_sequence(meta)
        ]
        next_sequence = (max(existing_sequences) + 1) if existing_sequences else 1
        for item in data:
            key = item_key(item)
            previous = previous_entries.get(key, {})
            if valid_sequence(previous):
                assigned_sequences[key] = int(previous["sequence"])
            else:
                assigned_sequences[key] = next_sequence
                next_sequence += 1

    max_sequence = max(assigned_sequences.values(), default=0)
    width = max(3, len(str(max(max_sequence, 999))))
    ordered_entries = []
    new_state_entries = {}
    desired_names = {INDEX_FILE.name, STATE_FILE.name}
    created = []

    for item in data:
        key = item_key(item)
        sequence = assigned_sequences[key]
        filename = note_filename(item, sequence, width, overrides)
        target = TARGET_DIR / filename
        target.write_text(note_content(item, overrides), encoding="utf-8")
        created.append(str(target))
        desired_names.add(filename)
        ordered_entries.append((sequence, item, filename))
        new_state_entries[key] = {
            "sequence": sequence,
            "filename": filename,
            "final_url": item.get("finalUrl", ""),
        }

    for old_file in TARGET_DIR.iterdir():
        if old_file.is_file() and old_file.name not in desired_names:
            old_file.unlink()

    ordered_entries.sort(key=lambda entry: entry[0])
    INDEX_FILE.write_text(index_content(ordered_entries, overrides), encoding="utf-8")
    STATE_FILE.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(LOCAL_TZ).isoformat(),
                "count": len(data),
                "source_json": str(source_file),
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
