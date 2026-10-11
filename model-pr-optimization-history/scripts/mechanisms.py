#!/usr/bin/env python3
"""Build/query a provisional mechanism index from local English PR cards.

Standard library only. Does not fetch GitHub or infer performance evidence.
Run from any directory; paths in generated records are history-root relative.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REPOS = {
    "sglang": "sgl-project/sglang",
    "vllm": "vllm-project/vllm",
    "tensorrt_llm": "NVIDIA/TensorRT-LLM",
    "tokenspeed": "lightseekorg/tokenspeed",
}
LABELS = {
    "compute": "计算方法与算子执行",
    "overlap": "依赖与执行重叠",
    "scheduling": "调度与执行粒度",
    "data": "数据驻留、布局与复用",
    "host": "CPU 控制与提交开销",
    "distributed": "分布式与资源分配",
}
# These narrow title matches produce discovery hints, not audited classifications.
# In particular, bare 'scheduler', 'CPU', 'metadata', and 'pipeline' do not match.
RULES = {
    "compute": r"\b(fus(?:e|ed|ion|ing)|unfuse|gemm|gemv|kernel|quantiz\w*|speculative decoding|spec decoding|split[- ]k|sparse attention|fp[48]|int[48])\b",
    "overlap": r"\b(overlap\w*|dual[-_ ]stream|multi[-_ ]stream|two streams|pipelined transfer|partial[-_ ]start|async(?:hronous)? (?:copy|transfer))\b",
    "scheduling": r"\b(continuous batching|dynamic batching|chunked[- ]prefill|chunked prefix|micro[- ]batch\w*|batching|co[- ]batching|batch vision|batch vision encoder|admission|preempt\w*|head[- ]of[- ]line|starvation|fairness|request schedul\w*|priority schedul\w*|num_scheduler_steps)\b",
    "data": r"\b(offload\w*|prefetch\w*|hicache|radix[-_ ]?cache|prefix cach\w*|kv[- ]cache|kvcache|cache (?:reuse|eviction)|memory pool|allocator|layout|strid\w*|contiguous|zero[- ]copy|concat\w*|paged cache|page allocation)\b",
    "host": r"\b(cuda[-_ ]?graphs?|launch overhead|host synchron\w*|implicit.*sync\w*|device[- ]scalar sync\w*|D2H|CPU overhead|CPU bottleneck|python overhead|recompil\w*|pre[- ]compil\w*|metadata (?:cach\w*|reus\w*|precomput\w*)|metadata to init time)\b",
    "distributed": r"\b(disagg\w*|EPLB|load balanc\w*|all[-_ ]reduce|all[-_ ]gather|all[-_ ]to[-_ ]all|tensor parallel\w*|pipeline parallel\w*|expert parallel\w*|context parallel\w*|sequence parallel\w*|communication|PD support|PD serving)\b",
}
KIND_RULES = {
    "revert": r"\brevert\w*\b",
    "fix": r"\b(bugfix|bug fix|fix|hotfix)\b",
    "support": r"\b(feat|feature|support|enable)\b",
    "performance": r"\b(perf|performance|optimi[sz]\w*|speedup|speed up)\b",
    "refactor": r"\b(refactor|cleanup|clean up|dedup\w*)\b",
    "test-docs-ci": r"\b(test|tests|testing|ci|doc|docs|documentation|cookbook|benchmark)\b",
}
# Human-read *local excerpts*, not full-diff reviews. The linked guide states
# observations separately from hypothesized costs and proposed experiments.
SEEDS = {
    "vllm:21116": ("compute", ["compute", "data"]),
    "sglang:5977": ("overlap", ["overlap"]),
    "vllm:43169": ("scheduling", ["scheduling"]),
    "sglang:39928": ("data", ["data"]),
    "tensorrt_llm:16734": ("host", ["host", "data"]),
    "sglang:19290": ("distributed", ["distributed"]),
    "sglang:21932": ("overlap", ["overlap", "data"]),
}
HEADER = re.compile(r"^### PR #(\d+) - (.+)$", re.MULTILINE)


def hints(titles: list[str], rules: dict[str, str]) -> dict[str, list[str]]:
    return {
        category: sorted({m.group(0) for title in titles
                          for m in re.finditer(pattern, title, re.IGNORECASE)})
        for category, pattern in rules.items()
        if any(re.search(pattern, title, re.IGNORECASE) for title in titles)
    }


def collect(root: Path) -> tuple[list[dict], dict]:
    records: dict[str, dict] = {}
    inputs = []
    for framework, repo in REPOS.items():
        for path in sorted((root / framework).glob("*/README.en.md")):
            raw = path.read_bytes()
            text = raw.decode("utf-8")
            rel = path.relative_to(root).as_posix()
            inputs.append({"path": rel, "sha256": hashlib.sha256(raw).hexdigest()})
            headings = list(HEADER.finditer(text))
            for index, heading in enumerate(headings):
                number, title = heading.groups()
                end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
                card = text[heading.end():end]
                url = f"https://github.com/{repo}/pull/{number}"
                link = re.search(r"^- Link: (\S+)", card, re.MULTILINE)
                if not link or link.group(1).rstrip("/") != url:
                    raise ValueError(f"Missing or mismatched PR link: {rel} #{number}")
                status = re.search(r"^- Status/date: (.+)$", card, re.MULTILINE)
                key = f"{framework}:{number}"
                row = records.setdefault(key, {
                    "id": key, "framework": framework, "number": int(number),
                    "url": url, "titles": [], "model_dossiers": [], "sources": [],
                })
                if title not in row["titles"]:
                    row["titles"].append(title)
                if path.parent.name not in row["model_dossiers"]:
                    row["model_dossiers"].append(path.parent.name)
                row["sources"].append({
                    "path": rel, "line": text.count("\n", 0, heading.start()) + 1,
                    "archived_status_date": status.group(1) if status else "unknown",
                    "card_type": "generated_inventory" if "not a manual audit" in card
                    else "legacy_card_review_not_revalidated",
                })
    rows = sorted(records.values(), key=lambda row: (row["framework"], row["number"]))
    for row in rows:
        matches = hints(row["titles"], RULES)
        row["matched_title_terms"] = matches
        row["mechanism_candidates"] = list(matches)
        row["primary_candidate"] = next(iter(matches)) if len(matches) == 1 else None
        row["classification_basis"] = "title_heuristic"
        if row["id"] in SEEDS:
            primary, categories = SEEDS[row["id"]]
            row.update(primary_candidate=primary, mechanism_candidates=categories,
                       classification_basis="local_excerpt_read")
        row["work_kind_hints"] = list(hints(row["titles"], KIND_RULES)) or ["unclassified"]
        row["evidence"] = {
            "source": "local_history_only",
            "full_diff_review": "not_done_in_this_index",
            "measurement": "not_assessed",
            "applicability": "not_established",
        }
    manifest = {
        "schema_version": 1,
        "scope": "English per-PR cards only; Chinese counterparts and timeline-only entries are not separately indexed",
        "source_documents": len(inputs),
        "source_cards": sum(len(row["sources"]) for row in rows),
        "unique_prs": len(rows),
        "framework_counts": dict(sorted(Counter(row["framework"] for row in rows).items())),
        "candidate_counts": {c: sum(c in row["mechanism_candidates"] for row in rows) for c in LABELS},
        "unclassified": sum(not row["mechanism_candidates"] for row in rows),
        "multiple_candidates": sum(len(row["mechanism_candidates"]) > 1 for row in rows),
        "inputs": inputs,
    }
    return rows, manifest


def select(rows: list[dict], category: str | None = None,
           framework: str | None = None, kind: str | None = None,
           terms: tuple[str, ...] = ()) -> list[dict]:
    return [row for row in rows
            if (framework is None or row["framework"] == framework)
            and (category is None or (not row["mechanism_candidates"] if category == "unclassified"
                                     else category in row["mechanism_candidates"]))
            and (kind is None or kind in row["work_kind_hints"])
            and all(term.casefold() in " ".join([row["id"], *row["titles"],
                                               *row["model_dossiers"]]).casefold()
                    for term in terms)]


def summary(rows: list[dict], manifest: dict) -> str:
    lines = ["# 初步分类统计与条目预览", "",
             "由 `scripts/mechanisms.py --rebuild` 从本地历史生成；这是检索线索，不是源码审核或收益证明。",
             "分类可交叉，数量不能相加；功能支持、修复、测试和文档也可能命中。", "",
             f"覆盖 {manifest['source_documents']} 份英文模型档案、{manifest['source_cards']} 张卡片，按框架和 PR 编号去重后 {manifest['unique_prs']} 个 PR。",
             f"其中 {manifest['unclassified']} 个没有可靠的标题匹配，{manifest['multiple_candidates']} 个具有多个候选机制。", "",
             "| 方向 | 候选 PR 数 |", "| --- | ---: |"]
    for category, label in LABELS.items():
        lines.append(f"| {label} (`{category}`) | {manifest['candidate_counts'][category]} |")
    lines += ["", "完整条目见 [index.jsonl](index.jsonl)，来源哈希见 [manifest.json](manifest.json)。",
              "下方每类仅按框架和编号展示前 6 项，不表示优先级或代表性；四格代表案例从分类入口单独链接。"]
    for category, label in {**LABELS, "unclassified": "待分类"}.items():
        found = select(rows, category)
        lines += ["", f"## {label}", "", "| PR | 标题 | 工作性质线索 |", "| --- | --- | --- |"]
        for row in found[:6]:
            title = row['titles'][0].replace('|', '\\|')
            lines.append(f"| [{row['id']}]({row['url']}) | {title} | {', '.join(row['work_kind_hints'])} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="*")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--rebuild", action="store_true", help="Regenerate local index and provenance")
    parser.add_argument("--check", action="store_true", help="Check generated files against current cards")
    parser.add_argument("--category", choices=[*LABELS, "unclassified"])
    parser.add_argument("--framework", choices=REPOS)
    parser.add_argument("--kind", choices=[*KIND_RULES, "unclassified"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Print matching JSONL rows")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.rebuild and args.check:
        parser.error("choose --rebuild or --check")
    destination = args.root / "mechanisms"
    if args.rebuild or args.check:
        rows, manifest = collect(args.root)
        outputs = {
            "index.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "summary.md": summary(rows, manifest),
        }
        for name, content in outputs.items():
            path = destination / name
            if args.check:
                if not path.exists() or path.read_text() != content:
                    raise SystemExit(f"Stale index: {path}; run --rebuild")
            else:
                destination.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        print(json.dumps({k: v for k, v in manifest.items() if k != "inputs"}, ensure_ascii=False, indent=2))
        return 0
    path = destination / "index.jsonl"
    if not path.exists():
        parser.error("index missing; run --rebuild")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    found = select(rows, args.category, args.framework, args.kind, tuple(args.terms))
    if not args.json:
        print(f"{len(found)} provisional matches; showing up to {args.limit}. Not performance evidence.")
    for row in found[:args.limit]:
        if args.json:
            print(json.dumps(row, ensure_ascii=False))
        else:
            print(f"\n{row['id']} {row['titles'][0]}\n  {row['url']}")
            print(f"  candidates={','.join(row['mechanism_candidates']) or 'unclassified'}; "
                  f"kind={','.join(row['work_kind_hints'])}; basis={row['classification_basis']}")
            source = row["sources"][0]
            print(f"  Read: {source['path']}:{source['line']}; measurements not assessed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
