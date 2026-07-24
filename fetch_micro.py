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
import html
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
USER_AGENT = "invisibleparade-build/1.0"


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
        url = html.escape(a["url"], quote=True)
        preview = html.escape(a["preview_url"], quote=True)
        alt = html.escape(a.get("description") or "", quote=True)
        inner += (
            f"<div><a href='{url}'>"
            f"<img src='{preview}' alt='{alt}'/>"
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


def fetch_statuses(host, account_id, token, min_id):
    """GET public statuses newer than min_id (newest-first). Raises on non-200."""
    params = {
        "exclude_replies": "true",
        "exclude_reblogs": "true",
        "only_public": "true",
        "limit": "100",  # single window; >100 new public posts between builds would need pagination
    }
    if min_id:
        params["min_id"] = min_id
    url = f"{host.rstrip('/')}/api/v1/accounts/{account_id}/statuses?{urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        },
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
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
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
