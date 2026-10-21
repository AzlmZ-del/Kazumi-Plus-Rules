#!/usr/bin/env python3
"""根据仓库根目录的规则文件重新生成 index.json。

Kazumi 的规则仓库约定：
  - index.json 是一个数组，每条描述一个规则
  - 规则文件名必须等于该规则的 name 字段，即 <name>.json

本脚本只依赖标准库，扫描根目录下除 index.json 外的所有 *.json，
按 name 排序后写出 index.json，并同步刷新 README「收录的源」表格
（表格夹在 <!-- rules-table:start --> 与 <!-- rules-table:end --> 之间）。

lastUpdate 取该文件的最后一次 git 提交时间（毫秒时间戳）。
新文件尚未提交时回退到文件修改时间。这样重新 clone 仓库不会
把所有规则的时间戳一起改掉。

用法：
  python tools/gen_index.py            # 重新生成 index.json
  python tools/gen_index.py --check    # 只校验，不一致时以退出码 1 结束
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_NAME = "index.json"
README_NAME = "README.md"
META_NAME = "tools/rule_meta.json"

# README「收录的源」表格用这对标记圈起来，脚本只替换中间部分。
TABLE_START = "<!-- rules-table:start -->"
TABLE_END = "<!-- rules-table:end -->"

# 表格里的日期固定按 UTC+8 算。
# 不能用本机时区：本地是 UTC+8、GitHub Actions 跑在 UTC，
# 同一份 index.json 会算出两个不同的日期，CI 每次都要改写 README。
TABLE_UTC_OFFSET = 8 * 3600

# 规则里没有 author 字段时写进索引的作者名，改成你自己的。
DEFAULT_AUTHOR = "AzlmZ-del"

REQUIRED_FIELDS = ("name", "version")


def git_commit_ms(path: Path) -> int | None:
    """返回 path 最后一次 git 提交的时间（毫秒），取不到返回 None。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", path.name],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    stamp = out.stdout.strip()
    if not stamp.isdigit():
        return None
    return int(stamp) * 1000


def mtime_ms(path: Path) -> int:
    return int(path.stat().st_mtime * 1000)


def load_rule(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("规则文件的根必须是 JSON 对象")
    return data


def build_entry(path: Path, rule: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if field not in rule]
    if missing:
        raise ValueError("缺少字段：" + ", ".join(missing))

    name = str(rule["name"]).strip()
    if not name:
        raise ValueError("name 不能为空")
    if name != path.stem:
        raise ValueError(
            f"name 字段为 {name!r}，与文件名 {path.name!r} 不一致；"
            "Kazumi 要求文件名等于 name 字段"
        )

    anti_crawler = rule.get("antiCrawlerConfig")
    if isinstance(anti_crawler, dict):
        anti_enabled = bool(anti_crawler.get("enabled", False))
    else:
        anti_enabled = bool(rule.get("antiCrawlerEnabled", False))

    stamp = git_commit_ms(path) or mtime_ms(path)

    return {
        "name": name,
        "version": str(rule.get("version", "1.0")),
        "useNativePlayer": bool(rule.get("useNativePlayer", False)),
        "antiCrawlerEnabled": anti_enabled,
        "author": str(rule.get("author") or DEFAULT_AUTHOR),
        "lastUpdate": stamp,
    }


def collect() -> list[dict]:
    entries: list[dict] = []
    for path in sorted(REPO_ROOT.glob("*.json")):
        if path.name == INDEX_NAME:
            continue
        rule = load_rule(path)
        # 只收规则文件，跳过别的 JSON（例如包管理器的配置文件）
        if "name" not in rule or "baseURL" not in rule:
            print(f"跳过 {path.name}：不像 Kazumi 规则文件")
            continue
        entries.append(build_entry(path, rule))
    entries.sort(key=lambda item: item["name"].lower())
    return entries


def render(entries: list[dict]) -> str:
    return json.dumps(entries, ensure_ascii=False, indent=2)


def load_rule_meta() -> dict[str, dict]:
    """读 tools/rule_meta.json：人工维护的站点与模式。"""
    path = REPO_ROOT / META_NAME
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{META_NAME} 的根必须是 JSON 对象")
    return data


def rule_base_url(name: str) -> str:
    """没在 rule_meta.json 里登记时，退回规则文件自己的 baseURL。"""
    path = REPO_ROOT / f"{name}.json"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return str(json.load(handle).get("baseURL", "")).rstrip("/")
    except (OSError, ValueError):
        return ""


def render_table(entries: list[dict]) -> str:
    """README 里「收录的源」那张表，版本与日期来自 index.json。"""
    meta = load_rule_meta()
    lines = [
        "| 规则名 | 站点 | 模式 | 版本 | 最后更新 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        name = entry["name"]
        info = meta.get(name, {})
        site = str(info.get("site") or rule_base_url(name))
        site_cell = f"<{site}>" if site else ""
        mode = str(info.get("mode", ""))
        stamp = entry["lastUpdate"] / 1000 + TABLE_UTC_OFFSET
        day = time.strftime("%Y-%m-%d", time.gmtime(stamp))
        lines.append(
            f"| {name} | {site_cell} | {mode} | {entry['version']} | {day} |"
        )
    return "\n".join(lines)


def sync_readme(entries: list[dict], check_only: bool) -> int:
    """把 README 里标记之间的表格换成最新内容。返回 0 正常，1 不一致。"""
    path = REPO_ROOT / README_NAME
    if not path.exists():
        return 0

    text = path.read_text(encoding="utf-8")
    start = text.find(TABLE_START)
    end = text.find(TABLE_END)
    if start < 0 or end < 0 or end < start:
        print(f"{README_NAME} 里没找到表格标记，跳过收录的源表格同步", file=sys.stderr)
        return 0

    head = text[: start + len(TABLE_START)]
    tail = text[end:]
    updated = f"{head}\n{render_table(entries)}\n{tail}"

    if updated == text:
        return 0
    if check_only:
        print(f"{README_NAME} 的收录的源表格不是最新，请运行 python tools/gen_index.py", file=sys.stderr)
        return 1

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(updated)
    print(f"已更新 {README_NAME} 的收录的源表格")
    return 0


def main() -> int:
    check_only = "--check" in sys.argv[1:]

    try:
        entries = collect()
    except (ValueError, json.JSONDecodeError) as error:
        print(f"生成失败：{error}", file=sys.stderr)
        return 2

    if not entries:
        print("仓库里没有任何规则文件", file=sys.stderr)
        return 2

    text = render(entries)
    index_path = REPO_ROOT / INDEX_NAME

    if check_only:
        current = ""
        if index_path.exists():
            with index_path.open("r", encoding="utf-8") as handle:
                current = handle.read()
        if current != text:
            print("index.json 与规则文件不一致，请运行 python tools/gen_index.py", file=sys.stderr)
            return 1
        if sync_readme(entries, check_only=True) != 0:
            return 1
        print(f"index.json 已是最新（{len(entries)} 条规则）")
        return 0

    with index_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    sync_readme(entries, check_only=False)

    print(f"已写入 {INDEX_NAME}，共 {len(entries)} 条规则：")
    for entry in entries:
        flag = "（含验证）" if entry["antiCrawlerEnabled"] else ""
        print(f"  - {entry['name']:<12} v{entry['version']}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
