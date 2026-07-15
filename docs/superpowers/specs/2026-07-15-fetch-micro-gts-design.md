# Design: `fetch_micro.py` — sync GoToSocial posts into the vault

**Date:** 2026-07-15
**Status:** Approved for planning

## Purpose

Automatically pull new public posts ("toots") from my GoToSocial instance and
turn each one into a micro-post Markdown file in my Obsidian vault, as part of
the site build. Replaces the old Jekyll-era `get_latest_gts_posts` Rake task
([reference](https://github.com/aonsager/aonsager.github.io/blob/f0ebb74c513f0011e03c2558d32ec3956b3e41a7/Rakefile#L126)).

## Context

- The site is Hugo. Micro-posts already live at `content/micro/{TOOT_ID}.md`.
- `build.sh` Step 1 rsyncs the Obsidian vault (`$CONTENT_SOURCE`) into
  `content/`. Writing new posts into the vault *before* Step 1 means the rsync
  copies them into the repo automatically — so the fetcher runs before Step 1
  and writes only to the vault.
- `prebuild.py` establishes conventions: stdlib only (`urllib.request`, `json`),
  no `requests`/`PyYAML`, frontmatter built as plain strings, 30s HTTP timeout.

### Existing file format (must match exactly)

```
---
date: '2025-06-08 11:58:00 +0900'
toot_id: 01JX6QK6SNPYJE1CDRQYZKT183
---
<p>This beautiful swallowtail butterfly came out of its cocoon today!</p>
<div class='gallery'><div><a href='ORIGINAL_URL'><img src='SMALL_URL' alt='DESCRIPTION'/></a></div>...</div>
```

- Filename is the bare ULID `toot_id` (no date prefix).
- Frontmatter: `date` (single-quoted, `YYYY-MM-DD HH:MM:00 +0900`) and `toot_id`.
- Body: raw `content` HTML from GTS, then a gallery div. When there are no
  attachments the gallery is still emitted as empty: `<div class='gallery'></div>`.

## Configuration

Read from environment (add secrets to the gitignored `.envrc`, already sourced):

| Var | Required | Default |
|-----|----------|---------|
| `GTS_API_TOKEN` | yes | — (error clearly if unset) |
| `GTS_HOST` | no | `https://gts.invisibleparade.com` |
| `GTS_ACCOUNT_ID` | no | `01GH6B64M32N9Y4742YPSN8KAY` |
| `CONTENT_SOURCE` | yes (existing) | — (vault micro dir = `$CONTENT_SOURCE/micro`) |

## Flow

1. **Determine `min_id`**: highest ULID among existing `*.md` filenames in
   `$CONTENT_SOURCE/micro`. ULIDs are lexicographically time-sortable, so `max()`
   of the filenames (sans `.md`) is the most recently fetched post. If the dir is
   empty or absent, omit `min_id` (fetch the most recent 100).
2. **Fetch**: `GET {GTS_HOST}/api/v1/accounts/{GTS_ACCOUNT_ID}/statuses` with
   query params `exclude_replies=true`, `exclude_reblogs=true`, `only_public=true`,
   `limit=100`, and `min_id={min_id}` (when set). Headers: `Accept: application/json`,
   `Authorization: Bearer {GTS_API_TOKEN}`. Normal TLS verification (the old code's
   `VERIFY_NONE` was a temporary hack and is dropped). 30s timeout.
3. **Iterate oldest→newest** (the API returns newest-first, so reverse).
4. **Skip filters** (ported from the old code) — skip a post if its `content`:
   - links to my own site (contains `invisibleparade.com`), or
   - contains a hashtag (`class="mention hashtag"`), or
   - contains a mention (matches regex `@\w+`).
5. **Write** kept posts to `$CONTENT_SOURCE/micro/{TOOT_ID}.md`:
   - `date` parsed from `created_at`, converted to `+09:00`.
   - Gallery: one `<div><a href='{original_url}'><img src='{small_url}' alt='{description}'/></a></div>`
     per `media_attachments` entry, wrapped in `<div class='gallery'>…</div>`;
     empty div when there are none. `attachment["url"]` = original, `attachment["preview_url"]` = small.

## Idempotency & error handling

- Re-runs never duplicate: `min_id` derives from existing files, and files are
  named by ULID. Additionally, **skip (do not overwrite)** any target path that
  already exists.
- Non-200 response: print the status/error and exit non-zero, so `set -e` in
  `build.sh` halts the build.
- Missing `GTS_API_TOKEN` or `CONTENT_SOURCE`: print a clear message and exit non-zero.
- Network timeout: 30s, matching `prebuild.py`.

## `--dry-run` flag

When passed, the script performs the fetch and filtering but prints what it
*would* write (path + a summary per post) without touching the vault.

## build.sh wiring

Insert before the current Step 1:

```bash
echo "Step 0: Fetching new micro-posts from GoToSocial..."
python3 fetch_micro.py
```

Kept as "Step 0" to avoid renumbering the existing steps.

## Testing

No automated tests (consistent with `prebuild.py`). Verification is a manual
`python3 fetch_micro.py --dry-run` against the live instance, confirming the
printed output matches the existing on-disk format.

## Out of scope (YAGNI)

- Tag generation (the old Rakefile's OpenAI tagging).
- Editing/deleting posts after they're fetched.
- Backfilling or re-fetching already-imported posts.
