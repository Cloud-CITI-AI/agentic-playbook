#!/usr/bin/env python3
"""Agent PR metrics for the quality scorecard (docs/09).

Usage:
  GITHUB_TOKEN=... agent-metrics.py --repo org/name [--repo org/other] --days 30 [--json out.json]

Metrics per repo and overall, split agent vs human:
  - PRs closed in window, merged, acceptance rate (merged / closed)
  - revert rate: merged PRs reverted within 14 days (a later merged PR whose title starts "Revert" and
    references the PR number or merge SHA)
  - median hours to first review, median review rounds (CHANGES_REQUESTED count + 1)
  - median changed lines
Agent PR = label "agent-authored" OR author type Bot (excluding renovate/dependabot/playbook-bot).
Standard library only. Approximation notes are in docs/09 §9.3.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import statistics
import sys
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
EXCLUDED_BOTS = {"renovate[bot]", "dependabot[bot]", "playbook-bot[bot]", "github-actions[bot]"}


def gh(path: str) -> list | dict:
    req = urllib.request.Request(f"{API}{path}", headers={
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def closed_prs(repo: str, since: dt.datetime) -> list[dict]:
    out, page = [], 1
    while True:
        batch = gh(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}")
        if not batch:
            break
        for pr in batch:
            closed = dt.datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00"))
            if closed >= since:
                out.append(pr)
        last = dt.datetime.fromisoformat(batch[-1]["updated_at"].replace("Z", "+00:00"))
        if last < since or page >= 20:
            break
        page += 1
    return out


def is_agent(pr: dict) -> bool:
    labels = {l["name"] for l in pr.get("labels", [])}
    u = pr["user"]
    return "agent-authored" in labels or (u.get("type") == "Bot" and u["login"] not in EXCLUDED_BOTS)


def is_dependency_bot(pr: dict) -> bool:
    return pr["user"]["login"] in EXCLUDED_BOTS


def hours(a: str, b: str) -> float:
    pa = dt.datetime.fromisoformat(a.replace("Z", "+00:00"))
    pb = dt.datetime.fromisoformat(b.replace("Z", "+00:00"))
    return (pb - pa).total_seconds() / 3600


def med(xs: list[float]) -> float | None:
    return round(statistics.median(xs), 1) if xs else None


def analyse(repo: str, days: int) -> dict:
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days + 14)
    prs = [p for p in closed_prs(repo, since) if not is_dependency_bot(p)]
    window_start = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    reverts = [p for p in prs if p.get("merged_at") and p["title"].lower().startswith("revert")]
    res: dict = {}
    for kind in ("agent", "human"):
        sel = [p for p in prs if (is_agent(p) == (kind == "agent"))
               and dt.datetime.fromisoformat(p["closed_at"].replace("Z", "+00:00")) >= window_start]
        merged = [p for p in sel if p.get("merged_at")]
        reverted = 0
        first_review, rounds, sizes = [], [], []
        for p in merged:
            num, sha = f"#{p['number']}", p.get("merge_commit_sha") or ""
            for r in reverts:
                body = (r.get("body") or "") + r["title"]
                if (num in body or (sha and sha[:7] in body)) and 0 <= hours(p["merged_at"], r["merged_at"]) <= 14 * 24:
                    reverted += 1
                    break
            reviews = gh(f"/repos/{repo}/pulls/{p['number']}/reviews?per_page=100")
            human_reviews = [rv for rv in reviews if rv["user"] and rv["user"].get("type") != "Bot" and rv.get("submitted_at")]
            if human_reviews:
                first_review.append(hours(p["created_at"], min(rv["submitted_at"] for rv in human_reviews)))
            rounds.append(1 + sum(1 for rv in human_reviews if rv["state"] == "CHANGES_REQUESTED"))
            detail = gh(f"/repos/{repo}/pulls/{p['number']}")
            sizes.append(detail.get("additions", 0) + detail.get("deletions", 0))
        res[kind] = {
            "closed": len(sel), "merged": len(merged),
            "acceptance_rate": round(len(merged) / len(sel), 3) if sel else None,
            "revert_rate_14d": round(reverted / len(merged), 3) if merged else None,
            "median_hours_to_first_human_review": med(first_review),
            "median_review_rounds": med(rounds),
            "median_changed_lines": med(sizes),
        }
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", action="append", required=True)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--json")
    a = ap.parse_args()
    if "GITHUB_TOKEN" not in os.environ:
        sys.exit("GITHUB_TOKEN (read-only, metadata + pull requests) required")
    report = {r: analyse(r, a.days) for r in a.repo}
    print(f"# Agent metrics — last {a.days} days\n")
    print("| repo | kind | closed | merged | acceptance | revert 14d | h to 1st review | review rounds | median lines |")
    print("|---|---|---|---|---|---|---|---|---|")
    for repo, kinds in report.items():
        for kind, m in kinds.items():
            print(f"| {repo} | {kind} | {m['closed']} | {m['merged']} | {m['acceptance_rate']} | {m['revert_rate_14d']} | "
                  f"{m['median_hours_to_first_human_review']} | {m['median_review_rounds']} | {m['median_changed_lines']} |")
    if a.json:
        json.dump(report, open(a.json, "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
