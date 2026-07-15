# fetch_micro.py (GoToSocial sync) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fetch new public GoToSocial posts and write each as a micro-post Markdown file into the Obsidian vault, run as Step 0 of `build.sh` before the rsync.

**Architecture:** A single stdlib-only Python script (`fetch_micro.py`) with small pure helper functions (ULID scan, skip-filter, HTML rendering) plus a thin HTTP fetch and an orchestrating `main()`. It writes only to the vault (`$CONTENT_SOURCE/micro`); build.sh Step 1's rsync copies files into `content/`. Idempotent via `min_id` derived from existing ULID filenames and a skip-if-exists guard.

**Tech Stack:** Python 3 standard library only (`urllib.request`, `json`, `argparse`, `datetime`, `pathlib`, `re`) — matching `prebuild.py`. No `requests`, no `PyYAML`, no test framework.

## Global Constraints

- stdlib only — no third-party imports (matches `prebuild.py`).
- Output file format must match existing files byte-for-format: filename `{TOOT_ID}.md`; frontmatter `date: '%Y-%m-%d %H:%M:00 %z'` (single-quoted, JST `+0900`, seconds literal `00`) and `toot_id: <ULID>`; body = raw `content` HTML then `<div class='gallery'>…</div>` (empty div when no media), each on its own line, trailing newline.
- Gallery item: `<div><a href='{original_url}'><img src='{small_url}' alt='{description}'/></a></div>` where `url`=original, `preview_url`=small.
- Skip filters (post is skipped if `content`): contains `invisibleparade.com`, OR contains `class="mention hashtag"`, OR matches regex `@\w+`.
- HTTP timeout 30s. Normal TLS verification.
- Secrets via env (added to gitignored `.envrc`): `GTS_API_TOKEN` (required). Defaults: `GTS_HOST=https://gts.invisibleparade.com`, `GTS_ACCOUNT_ID=01GH6B64M32N9Y4742YPSN8KAY`. `CONTENT_SOURCE` already exists.
- Non-200 / unreachable / missing required env → print clear message, exit non-zero (so build.sh `set -e` halts).

---

### Task 1: Pure helpers + module scaffold

**Files:**
- Create: `fetch_micro.py`

**Interfaces:**
- Produces:
  - `latest_toot_id(micro_dir: Path) -> str | None` — highest ULID stem among `*.md`, or `None`.
  - `should_skip(content: str) -> bool` — skip-filter.
  - `render_gallery(media_attachments: list) -> str` — gallery div (empty div when list empty).
  - `render_post(post: dict) -> tuple[str, str]` — `(toot_id, file_text)`.
  - Constants: `DEFAULT_HOST`, `DEFAULT_ACCOUNT_ID`, `JST`, `ULID_RE`, `HTTP_TIMEOUT`.

- [ ] **Step 1: Create the file with imports, constants, and pure helpers**

```python
#!/usr/bin/env python3
"""
Fetch new GoToSocial micro-posts and write them into the Obsidian vault.

Runs as Step 0 of build.sh, before the rsync. For each new public post it
writes one Markdown file to $CONTENT_SOURCE/micro/{TOOT_ID}.md, matching the
existing micro-post format. build.sh Step 1's rsync then copies them into
content/. stdlib only, matching prebuild.py conventions.
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode

DEFAULT_HOST = "https://gts.invisibleparade.com"
DEFAULT_ACCOUNT_ID = "01GH6B64M32N9Y4742YPSN8KAY"
JST = timezone(timedelta(hours=9))
ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")  # Crockford base32, 26 chars
HTTP_TIMEOUT = 30


def latest_toot_id(micro_dir):
    """Highest ULID among {ULID}.md files in micro_dir, or None if empty/absent.

    ULIDs are lexicographically time-sortable, so max() is the most recent.
    """
    if not micro_dir.is_dir():
        return None
    ids = [p.stem for p in micro_dir.glob("*.md") if ULID_RE.match(p.stem)]
    return max(ids) if ids else None


def should_skip(content):
    """Skip self-links, hashtags, and mentions (ported from the old Rakefile)."""
    if "invisibleparade.com" in content:
        return True
    if 'class="mention hashtag"' in content:
        return True
    if re.search(r"@\w+", content):
        return True
    return False


def render_gallery(media_attachments):
    """Render the gallery div. Empty div when there are no attachments."""
    inner = ""
    for a in media_attachments:
        alt = a.get("description") or ""
        inner += (
            f"<div><a href='{a['url']}'>"
            f"<img src='{a['preview_url']}' alt='{alt}'/>"
            f"</a></div>"
        )
    return f"<div class='gallery'>{inner}</div>"


def render_post(post):
    """Return (toot_id, file_text) for a GoToSocial status dict."""
    toot_id = post["id"]
    created = post["created_at"].replace("Z", "+00:00")
    dt = datetime.fromisoformat(created).astimezone(JST)
    date_str = dt.strftime("%Y-%m-%d %H:%M:00 %z")
    text = (
        "---\n"
        f"date: '{date_str}'\n"
        f"toot_id: {toot_id}\n"
        "---\n"
        f"{post['content']}\n"
        f"{render_gallery(post.get('media_attachments', []))}\n"
    )
    return toot_id, text
```

- [ ] **Step 2: Verify the pure helpers against sample data and the real vault**

Run:
```bash
python3 - <<'PY'
from pathlib import Path
import os, fetch_micro as m

# render_post matches the existing on-disk format
post = {
    "id": "01JX6QK6SNPYJE1CDRQYZKT183",
    "created_at": "2025-06-08T02:58:00.000Z",
    "content": "<p>hello</p>",
    "media_attachments": [
        {"url": "http://o/1.jpg", "preview_url": "http://s/1.jpg", "description": "a cat"},
    ],
}
tid, text = m.render_post(post)
assert tid == "01JX6QK6SNPYJE1CDRQYZKT183", tid
assert "date: '2025-06-08 11:58:00 +0900'" in text, text   # UTC 02:58 -> JST 11:58
assert "toot_id: 01JX6QK6SNPYJE1CDRQYZKT183" in text
assert "<div class='gallery'><div><a href='http://o/1.jpg'><img src='http://s/1.jpg' alt='a cat'/></a></div></div>" in text

# empty gallery
assert m.render_gallery([]) == "<div class='gallery'></div>"

# skip filters
assert m.should_skip("<p>see invisibleparade.com</p>") is True
assert m.should_skip('<p><a class="mention hashtag">#x</a></p>') is True
assert m.should_skip("<p>hi @bob</p>") is True
assert m.should_skip("<p>just a normal post</p>") is False

# latest_toot_id against the live vault (read-only)
micro = Path(os.environ["CONTENT_SOURCE"]) / "micro"
print("latest_toot_id:", m.latest_toot_id(micro))
print("ALL PURE-HELPER CHECKS PASSED")
PY
```
Expected: prints a real ULID (e.g. `01KDMF1VF30W93P18H2PB846BW`) then `ALL PURE-HELPER CHECKS PASSED`, exit 0.

- [ ] **Step 3: Commit**

```bash
git add fetch_micro.py
git commit -m "feat: add pure helpers for GoToSocial micro-post rendering"
```

---

### Task 2: HTTP fetch + main orchestration + --dry-run

**Files:**
- Modify: `fetch_micro.py` (append `fetch_statuses`, `main`, `__main__` guard)
- Modify: `.envrc` (add `GTS_API_TOKEN` — local secret, NOT committed)

**Interfaces:**
- Consumes: `latest_toot_id`, `should_skip`, `render_post`, constants from Task 1.
- Produces: `fetch_statuses(host, account_id, token, min_id) -> list`; `main()`.

- [ ] **Step 1: Add the local API token to `.envrc`**

Append to `.envrc` (this file is gitignored — the token is never committed):
```bash
export GTS_API_TOKEN="<paste-your-gotosocial-access-token>"
```
Then reload the environment (`direnv allow`, or `source .envrc`).

- [ ] **Step 2: Append `fetch_statuses`, `main`, and the entrypoint to `fetch_micro.py`**

Add at the end of the file (after `render_post`):
```python
def fetch_statuses(host, account_id, token, min_id):
    """GET public statuses newer than min_id (newest-first). Raises on non-200."""
    params = {
        "exclude_replies": "true",
        "exclude_reblogs": "true",
        "only_public": "true",
        "limit": "100",
    }
    if min_id:
        params["min_id"] = min_id
    url = f"{host}/api/v1/accounts/{account_id}/statuses?{urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch new GoToSocial micro-posts into the Obsidian vault."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without touching the vault.",
    )
    args = parser.parse_args()

    token = os.environ.get("GTS_API_TOKEN")
    if not token:
        sys.exit("Error: GTS_API_TOKEN is not set.")
    content_source = os.environ.get("CONTENT_SOURCE")
    if not content_source:
        sys.exit("Error: CONTENT_SOURCE is not set.")
    host = os.environ.get("GTS_HOST", DEFAULT_HOST)
    account_id = os.environ.get("GTS_ACCOUNT_ID", DEFAULT_ACCOUNT_ID)

    micro_dir = Path(content_source) / "micro"
    min_id = latest_toot_id(micro_dir)

    try:
        statuses = fetch_statuses(host, account_id, token, min_id)
    except urllib.error.HTTPError as e:
        sys.exit(f"Error: GTS API returned {e.code} {e.reason}")
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Error: could not reach GTS: {e}")

    created = 0
    # API returns newest-first; write oldest-first so filenames land in order.
    for post in reversed(statuses):
        if should_skip(post["content"]):
            print(f"Skipping {post['id']} (self-link/mention/hashtag)")
            continue
        toot_id, text = render_post(post)
        dest = micro_dir / f"{toot_id}.md"
        if dest.exists():
            print(f"Skipping {toot_id} (already exists)")
            continue
        if args.dry_run:
            media = len(post.get("media_attachments", []))
            print(f"[dry-run] would write {dest} ({media} media)")
        else:
            micro_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            print(f"Created {dest}")
        created += 1

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {created} post(s).")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify the missing-token error path**

Run:
```bash
env -u GTS_API_TOKEN python3 fetch_micro.py --dry-run; echo "exit=$?"
```
Expected: prints `Error: GTS_API_TOKEN is not set.` and `exit=1`.

- [ ] **Step 4: Verify end-to-end dry run against the live instance**

Run (env loaded so `GTS_API_TOKEN` and `CONTENT_SOURCE` are set):
```bash
python3 fetch_micro.py --dry-run
```
Expected: exit 0, ends with `Would create N post(s).`, and no new files appear in the vault:
```bash
git -C "$CONTENT_SOURCE" status --porcelain 2>/dev/null | grep micro || echo "no vault changes (dry run OK)"
```
(If the vault isn't a git repo, instead confirm the printed `[dry-run] would write …` paths do not exist on disk.)

- [ ] **Step 5: Commit** (script only — `.envrc` is gitignored)

```bash
git add fetch_micro.py
git commit -m "feat: fetch GoToSocial statuses and write micro-posts to the vault"
```

---

### Task 3: Wire into build.sh as Step 0

**Files:**
- Modify: `build.sh` (insert Step 0 before the current Step 1)

**Interfaces:**
- Consumes: `fetch_micro.py` `main()` via `python3 fetch_micro.py`.

- [ ] **Step 1: Insert Step 0 before the rsync**

In `build.sh`, immediately after the `set -e` line and before `# Step 1: Sync…`, insert:
```bash

# Step 0: Fetch new micro-posts from GoToSocial into the vault
echo "Step 0: Fetching new micro-posts from GoToSocial..."
python3 fetch_micro.py
```

- [ ] **Step 2: Verify build.sh ordering**

Run:
```bash
grep -n "Step 0\|python3 fetch_micro.py\|Step 1: Sync\|rsync" build.sh
```
Expected: `Step 0` and `python3 fetch_micro.py` lines appear **before** the `Step 1: Sync` and `rsync` lines.

- [ ] **Step 3: Commit**

```bash
git add build.sh
git commit -m "build: fetch GoToSocial micro-posts before syncing the vault"
```

---

## Self-Review Notes

- **Spec coverage:** config/env (Task 2 Step 1 + main), min_id from highest ULID (`latest_toot_id`, Task 1), fetch params + auth + TLS + timeout (`fetch_statuses`, Task 2), oldest→newest iteration (Task 2 main), skip filters (`should_skip`, Task 1), exact file format (`render_post`/`render_gallery`, Task 1 verified in Step 2), idempotency via min_id + skip-if-exists (Task 2 main), error handling/exit codes (Task 2 main + Step 3), `--dry-run` (Task 2), build.sh Step 0 wiring (Task 3), vault-only writes (main writes only under `$CONTENT_SOURCE/micro`). No gaps.
- **Placeholders:** none — the only `<paste-your-…-token>` is a genuine user secret, by design not committed.
- **Type consistency:** helper names/signatures used in Task 2's `main` match those defined in Task 1 (`latest_toot_id`, `should_skip`, `render_post`, `render_gallery`, `fetch_statuses`).
