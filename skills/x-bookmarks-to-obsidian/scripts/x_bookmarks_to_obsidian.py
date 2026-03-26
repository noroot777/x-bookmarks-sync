#!/usr/bin/env python3
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional


SKILL_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = Path(os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_CONFIG_FILE", str(SKILL_DIR / "x_bookmarks_to_obsidian.env"))).expanduser()
EXPORT_SCRIPT = SKILL_DIR / "scripts" / "export_x_bookmarks.devbrowser.js"
GENERATE_SCRIPT = SKILL_DIR / "scripts" / "generate_x_bookmarks_obsidian_notes.py"
MIN_SUPPORTED_CHROME_MAJOR = int(os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_MIN_CHROME_MAJOR", "144"))


def bool_env(name: str, default: str) -> bool:
    return os.environ.get(name, default).strip() == "1"


def parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        value = os.path.expandvars(value)
        value = str(Path(value).expanduser()) if value.startswith("~") else value
        values[key] = value
    return values


def load_config() -> None:
    for key, value in parse_env_file(CONFIG_FILE).items():
        os.environ[key] = value


def common_home() -> Path:
    return Path.home()


def default_target_dir() -> Path:
    return common_home() / "Obsidian" / "X Bookmarks to Obsidian"


def target_dir_configured() -> bool:
    return bool(os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR", "").strip())


def env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    if raw:
        return Path(raw).expanduser()
    return default.expanduser()


def default_devtools_candidates() -> List[Path]:
    home = common_home()
    system = platform.system()
    if system == "Darwin":
        base = home / "Library" / "Application Support" / "Google" / "Chrome"
        return [base / "DevToolsActivePort"]
    if system == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")
        candidates = []
        if local:
            candidates.append(Path(local) / "Google" / "Chrome" / "User Data" / "DevToolsActivePort")
        if roaming:
            candidates.append(Path(roaming) / "Google" / "Chrome" / "User Data" / "DevToolsActivePort")
        return candidates

    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))).expanduser()
    return [
        config_home / "google-chrome" / "DevToolsActivePort",
        config_home / "google-chrome-beta" / "DevToolsActivePort",
        config_home / "chromium" / "DevToolsActivePort",
        config_home / "chromium-browser" / "DevToolsActivePort",
    ]


def resolve_devtools_file() -> Path:
    explicit = os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_DEVTOOLS_FILE", "").strip()
    if explicit:
        return Path(explicit).expanduser()

    candidates = default_devtools_candidates()
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else Path("DevToolsActivePort")


def default_chrome_candidates() -> List[str]:
    system = platform.system()
    if system == "Darwin":
        return ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    if system == "Windows":
        candidates: List[str] = []
        for base in (
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
        ):
            if not base:
                continue
            candidates.append(str(Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe"))
        return candidates

    discovered: List[str] = []
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        match = shutil.which(name)
        if match:
            discovered.append(match)
    discovered.extend(
        [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
    )
    return discovered


def resolve_chrome_bin() -> str:
    explicit = os.environ.get("X_BOOKMARKS_TO_OBSIDIAN_CHROME_BIN", "").strip()
    if explicit:
        return explicit

    for candidate in default_chrome_candidates():
        if candidate and Path(candidate).exists():
            return candidate
    return default_chrome_candidates()[0]


def ensure_target_dir_configured() -> None:
    if target_dir_configured():
        return
    raise SystemExit(
        "First-time setup required before syncing X bookmarks.\n"
        "Create x_bookmarks_to_obsidian.env from x_bookmarks_to_obsidian.env.example and set "
        "X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR to your Obsidian notes folder using an absolute path."
    )


def ensure_absolute_target_dir(target_dir: Path) -> None:
    if target_dir.is_absolute():
        return
    raise SystemExit(
        "X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR must be an absolute path. "
        f"Current value: {target_dir}\n"
        "Update x_bookmarks_to_obsidian.env and set X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR to an "
        "absolute path like /Users/you/Obsidian/X Bookmarks."
    )


def run_checked(cmd: List[str], env: Optional[Dict[str, str]] = None) -> None:
    subprocess.run(cmd, check=True, env=env)


def ensure_dev_browser() -> None:
    if shutil.which("dev-browser"):
        return
    if not shutil.which("npm"):
        raise SystemExit("dev-browser is not installed, and npm is not available to install it automatically.")
    print("dev-browser not found. Installing it automatically with npm...")
    run_checked(["npm", "install", "-g", "dev-browser"])


def check_chrome_version(chrome_bin: str) -> None:
    if not Path(chrome_bin).exists():
        raise SystemExit(f"Google Chrome was not found at: {chrome_bin}")

    proc = subprocess.run([chrome_bin, "--version"], capture_output=True, text=True, check=False)
    version_output = (proc.stdout or proc.stderr or "").strip()
    match = re.search(r"(\d+)\.", version_output)
    if not match:
        raise SystemExit(f"Could not determine the installed Chrome version. Output was: {version_output}")

    major = int(match.group(1))
    if major < MIN_SUPPORTED_CHROME_MAJOR:
        raise SystemExit(
            f"Chrome {major} is too old for this skill's current-session remote-debugging flow.\n"
            f"This skill expects Chrome {MIN_SUPPORTED_CHROME_MAJOR}+ with chrome://inspect#remote-debugging "
            "support for active browser sessions."
        )


def resolve_state_file(target_dir: Path) -> Path:
    state_file = env_path("X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE", target_dir / ".x_bookmarks_to_obsidian_state.json")
    legacy_state = target_dir / ".x_bookmarks_state.json"
    if not state_file.exists() and legacy_state.exists():
        state_file = legacy_state
    return state_file


def build_endpoint(devtools_file: Path) -> str:
    if not devtools_file.exists():
        raise SystemExit(
            f"Chrome remote debugging is not enabled: {devtools_file} not found\n"
            "Open chrome://inspect#remote-debugging in Chrome and enable remote debugging first."
        )

    lines = devtools_file.read_text(encoding="utf-8").splitlines()
    port = lines[0].strip() if len(lines) >= 1 else ""
    ws_path = lines[1].strip() if len(lines) >= 2 else ""
    if not port or not ws_path:
        raise SystemExit("Invalid DevToolsActivePort contents")
    return f"ws://127.0.0.1:{port}{ws_path}"


def load_known_links(state_file: Path) -> List[str]:
    if not state_file.exists():
        return []
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        entries = data.get("entries", {})
        if isinstance(entries, dict):
            return [key for key in entries.keys() if isinstance(key, str) and key]
    except Exception:
        pass
    return []


def write_known_links(path: Path, links: Iterable[str]) -> int:
    known = list(links)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
    return len(known)


def load_export_items(path: Path) -> List[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []


def incremental_items(items: Iterable[dict], known_links: Iterable[str]) -> List[dict]:
    known = {link for link in known_links if isinstance(link, str) and link}
    out: List[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        status_link = str(item.get("statusLink", "")).strip()
        if not status_link or status_link in known:
            continue
        out.append(item)
    return out


def write_json_list(path: Path, items: List[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(items)


def incremental_source_path(source_json: Path) -> Path:
    return source_json.parent / "x-bookmarks-to-obsidian-incremental.json"


def usage() -> str:
    script = Path(__file__).name
    return (
        f"Usage:\n"
        f"  python3 {script}                # export + generate\n"
        f"  python3 {script} full           # export + generate\n"
        f"  python3 {script} export         # export only\n"
        f"  python3 {script} generate       # generate only from existing JSON\n"
    )


def parse_mode(argv: List[str]) -> str:
    if not argv:
        return "full"
    mode = argv[0].strip().lower()
    if mode in {"full", "export", "generate"} and len(argv) == 1:
        return mode
    if mode in {"-h", "--help", "help"}:
        print(usage())
        raise SystemExit(0)
    raise SystemExit(f"Unsupported command: {' '.join(argv)}\n\n{usage()}")


def main(argv: List[str]) -> int:
    mode = parse_mode(argv)
    load_config()

    ensure_target_dir_configured()
    target_dir = env_path("X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR", default_target_dir())
    ensure_absolute_target_dir(target_dir)

    dev_browser_tmp = env_path("X_BOOKMARKS_TO_OBSIDIAN_DEV_BROWSER_TMP", common_home() / ".dev-browser" / "tmp")
    source_json = env_path("X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON", dev_browser_tmp / "x-bookmarks-to-obsidian-export.json")
    incremental_source_json = incremental_source_path(source_json)
    overrides_file = env_path("X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE", dev_browser_tmp / "x-bookmarks-to-obsidian-llm-overrides.json")
    known_links_file = env_path("X_BOOKMARKS_TO_OBSIDIAN_KNOWN_LINKS_FILE", dev_browser_tmp / "x-bookmarks-to-obsidian-known.json")
    state_file = resolve_state_file(target_dir)

    os.environ["X_BOOKMARKS_TO_OBSIDIAN_TARGET_DIR"] = str(target_dir)
    os.environ["X_BOOKMARKS_TO_OBSIDIAN_STATE_FILE"] = str(state_file)
    os.environ["X_BOOKMARKS_TO_OBSIDIAN_SOURCE_JSON"] = str(source_json)
    os.environ["X_BOOKMARKS_TO_OBSIDIAN_LLM_OVERRIDES_FILE"] = str(overrides_file)

    run_export = mode in {"full", "export"} and not bool_env("X_BOOKMARKS_TO_OBSIDIAN_SKIP_EXPORT", "0")
    run_generate = mode in {"full", "generate"} and not bool_env("X_BOOKMARKS_TO_OBSIDIAN_SKIP_GENERATE", "0")

    if not run_export and not run_generate:
        raise SystemExit("Nothing to do: both export and generate are disabled.")

    child_env = os.environ.copy()
    known_links = load_known_links(state_file)

    if run_export:
        ensure_dev_browser()
        chrome_bin = resolve_chrome_bin()
        check_chrome_version(chrome_bin)
        endpoint = build_endpoint(resolve_devtools_file())

        known_count = write_known_links(known_links_file, known_links)
        if state_file.exists():
            print(f"Loaded {known_count} known bookmarks from {state_file}")
        else:
            print("No prior state file found; export will scan until the end of the bookmark list")

        child_env["X_BOOKMARKS_TO_OBSIDIAN_CHROME_BIN"] = chrome_bin
        run_checked(
            [
                "dev-browser",
                "--connect",
                endpoint,
                "--timeout",
                "900",
                "run",
                str(EXPORT_SCRIPT),
            ],
            env=child_env,
        )

        exported_items = load_export_items(source_json)
        new_items = incremental_items(exported_items, known_links)
        new_count = write_json_list(incremental_source_json, new_items)
        print(f"Prepared {new_count} incremental bookmarks for agent overrides at {incremental_source_json}")

    if run_generate:
        run_checked([sys.executable, str(GENERATE_SCRIPT)], env=child_env)

    if mode == "export" or (run_export and not run_generate):
        print(f"Exported X bookmarks to {source_json}")
        print(f"Prepared incremental bookmarks at {incremental_source_json}")
        print(f"Write agent overrides to {overrides_file}")
    elif mode == "generate" or (run_generate and not run_export):
        print(f"Generated X bookmark notes into {target_dir}")
    else:
        print(f"Synced X bookmarks into {target_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
