from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from dotenv import load_dotenv


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


@dataclass(frozen=True)
class RepoQuery:
    count: int
    out: Path
    min_stars: int
    page_size: int
    max_size_mb: int | None


def _parse_args() -> RepoQuery:
    p = argparse.ArgumentParser(
        description="Collect GitHub repository URLs (JavaScript only) using GitHub GraphQL Search."
    )
    p.add_argument("--count", type=int, required=True, help="Number of repositories to collect.")
    p.add_argument("--out", type=Path, required=True, help="Output .txt file path.")
    p.add_argument("--min-stars", type=int, default=100, help="Minimum stargazers (default: 100).")
    p.add_argument("--page-size", type=int, default=20, help="GraphQL page size 1..100 (default: 20).")
    p.add_argument("--max-size-mb", type=int, default=None, help="Max repo size in MB (optional).")

    ns = p.parse_args()

    if ns.count <= 0:
        p.error("--count must be > 0")
    if ns.min_stars < 0:
        p.error("--min-stars must be >= 0")
    if ns.page_size < 1 or ns.page_size > 100:
        p.error("--page-size must be in range 1..100")
    if ns.max_size_mb is not None and ns.max_size_mb <= 0:
        p.error("--max-size-mb must be > 0")

    min_stars = max(int(ns.min_stars), 6)

    return RepoQuery(
        count=ns.count,
        out=ns.out,
        min_stars=min_stars,
        page_size=ns.page_size,
        max_size_mb=ns.max_size_mb,
    )


def _build_graphql_query(*, min_stars: int, page_size: int, after: str | None, max_size_mb: int | None) -> str:
    size_qual = f" size:<={max_size_mb * 1024}" if max_size_mb is not None else ""

    qualifiers = (
        f"stars:>={min_stars} created:>=2012-01-01 language:JavaScript fork:false{size_qual} sort:stars"
    )
    after_part = f', after: "{after}"' if after else ""

    return f"""
      query {{
        search(query: "{qualifiers}", type: REPOSITORY, first: {page_size}{after_part}) {{
          edges {{
            node {{
              ... on Repository {{
                url
                isPrivate
                isDisabled
                isLocked
                isFork
                forkCount
                stargazerCount

                # Only keep repos that have package.json at the repository root (default branch HEAD).
                packageJson: object(expression: "HEAD:package.json") {{
                  __typename
                }}

                # Language breakdown so we can require JS+TS >= 60% of code.
                languages(first: 20, orderBy: {{field: SIZE, direction: DESC}}) {{
                  totalSize
                  edges {{
                    size
                    node {{ name }}
                  }}
                }}
              }}
            }}
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
        rateLimit {{
          remaining
          resetAt
        }}
      }}
    """


def _sleep_until(iso_utc: str) -> None:
    reset = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    seconds = (reset - now).total_seconds()
    if seconds > 0:
        time.sleep(seconds + 1.5)


def _post_graphql(token: str, query: str, *, retries: int = 4) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for attempt in range(1, retries + 1):
        resp = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers, timeout=60)

        try:
            payload = resp.json()
        except ValueError:
            payload = {}

        errors = payload.get("errors") or []
        has_graphql_errors = isinstance(errors, list) and len(errors) > 0

        if resp.ok and not has_graphql_errors:
            return payload

        # Handle rate limiting / temporary blocks: wait until resetAt if present.
        if resp.status_code in (403, 429):
            reset_at = (payload.get("data", {}).get("rateLimit", {}) or {}).get("resetAt")
            if isinstance(reset_at, str) and reset_at:
                _sleep_until(reset_at)
                continue
            time.sleep(30)
            continue

        # Retry server errors
        if 500 <= resp.status_code <= 599:
            time.sleep(2 * attempt)
            continue

        raise RuntimeError(f"GitHub API error ({resp.status_code}): {payload or resp.text}")

    raise RuntimeError("GitHub API request failed after retries")


def _js_ts_ratio_at_least_60_percent(repo_node: dict) -> bool:
    langs = repo_node.get("languages")
    if not isinstance(langs, dict):
        return False

    total = langs.get("totalSize")
    if not isinstance(total, int) or total <= 0:
        return False

    edges = langs.get("edges") or []
    if not isinstance(edges, list):
        return False

    js_ts_size = 0
    for e in edges:
        if not isinstance(e, dict):
            continue
        size = e.get("size")
        node = e.get("node")
        name = node.get("name") if isinstance(node, dict) else None
        if isinstance(size, int) and name in ("JavaScript", "TypeScript"):
            js_ts_size += size

    return (js_ts_size / total) >= 0.60


def _extract_urls(payload: dict) -> tuple[list[str], bool, str | None]:
    search = (payload.get("data") or {}).get("search") or {}
    edges = search.get("edges") or []
    page_info = search.get("pageInfo") or {}

    urls: list[str] = []
    for edge in edges:
        node = (edge or {}).get("node") or {}

        if node.get("isPrivate") is True:
            continue
        if node.get("isDisabled") is True:
            continue
        if node.get("isLocked") is True:
            continue

        if node.get("isFork") is True:
            continue

        if isinstance(node.get("stargazerCount"), int) and node.get("stargazerCount") < 6:
            continue

        pkg_obj = node.get("packageJson")
        if not isinstance(pkg_obj, dict) or pkg_obj.get("__typename") != "Blob":
            continue

        if not _js_ts_ratio_at_least_60_percent(node):
            continue

        url = node.get("url")
        if isinstance(url, str) and url:
            urls.append(url)

    has_next = bool(page_info.get("hasNextPage"))
    end_cursor = page_info.get("endCursor")
    return urls, has_next, end_cursor if isinstance(end_cursor, str) and end_cursor else None


def _collect(token: str, spec: RepoQuery) -> Iterable[str]:
    seen: set[str] = set()
    cursor: str | None = None

    while len(seen) < spec.count:
        q = _build_graphql_query(
            min_stars=spec.min_stars,
            page_size=spec.page_size,
            after=cursor,
            max_size_mb=spec.max_size_mb,
        )
        payload = _post_graphql(token, q)
        urls, has_next, next_cursor = _extract_urls(payload)

        before = len(seen)
        for u in urls:
            seen.add(u)
            if len(seen) >= spec.count:
                break

        if len(seen) == before:
            break
        if not has_next or not next_cursor:
            break

        cursor = next_cursor

    return list(seen)[: spec.count]


def main() -> None:
    load_dotenv()
    spec = _parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN not found. Put it in .env or export it in your shell.")

    out_path = (Path.cwd() / spec.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    repos = list(_collect(token, spec))
    out_path.write_text("".join(f"{u}\n" for u in repos), encoding="utf-8")

    print(f"Wrote {len(repos)} repositories to {out_path}")


if __name__ == "__main__":
    main()