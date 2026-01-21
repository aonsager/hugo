#!/usr/bin/env python3
"""
Pre-build script for Hugo image management.

Reads from /content/, writes to /content-processed/:
1. Copies all content to /content-processed/
2. Converts posts with images to page bundles
3. Resolves images (with fuzzy matching)
4. Downloads external images to cache
5. Updates image references to relative paths
6. Converts HTML img tags to {{< image >}} shortcodes
"""

import os
import re
import shutil
import hashlib
import urllib.request
import urllib.error
from urllib.parse import urlparse
from collections import defaultdict
from pathlib import Path

# Configuration
INPUT_DIR = Path("content")
OUTPUT_DIR = Path("content-processed")
CACHE_DIR = Path(".image-cache")
MAX_WIDTH = 2400  # Auto-resize images wider than this (handled by Hugo)

# Image file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif'}

# Regex patterns
MD_IMAGE_PATTERN = re.compile(
    r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)'
)
# Clickable image: [![alt](thumb)](full)
CLICKABLE_IMAGE_PATTERN = re.compile(
    r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)'
)
# HTML img tag
HTML_IMG_PATTERN = re.compile(
    r'<img\s+([^>]*?)\s*/?>',
    re.IGNORECASE | re.DOTALL
)
# Extract attributes from img tag
ATTR_PATTERN = re.compile(r'(\w+)=["\']([^"\']*)["\']|(\w+)=(\S+?)(?:\s|>|/>)')


def build_image_index(images_dir):
    """Build {filename: [full_paths]} index for fuzzy matching."""
    index = defaultdict(list)
    if not images_dir.exists():
        return index

    for path in images_dir.rglob('*'):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            index[path.name].append(path)

    return index


def is_external_url(src):
    """Check if src is an external URL."""
    return src.startswith('http://') or src.startswith('https://')


def url_to_cache_path(url):
    """Convert URL to a cache file path."""
    # Create a hash of the URL for the filename
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    # Extract original filename if possible
    path = urlparse(url).path
    original_name = os.path.basename(path)
    if original_name and '.' in original_name:
        name, ext = os.path.splitext(original_name)
        # Sanitize the name
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:30]
        cache_name = f"{name}_{url_hash}{ext}"
    else:
        cache_name = f"image_{url_hash}.jpg"

    return CACHE_DIR / cache_name


def download_image(url, cache_path):
    """Download image from URL to cache path."""
    if cache_path.exists():
        return cache_path

    print(f"  Downloading: {url}")
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Create request with user agent
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; HugoPrebuild/1.0)'}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            with open(cache_path, 'wb') as f:
                f.write(response.read())

        print(f"  Downloaded: {cache_path.name}")
        return cache_path
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  WARNING: Failed to download {url}: {e}")
        return None


def resolve_image(src, image_index, content_dir):
    """
    Resolve image source to a local path.
    Returns (local_path, was_external) or (None, False) if not found.
    """
    if is_external_url(src):
        cache_path = url_to_cache_path(src)
        downloaded = download_image(src, cache_path)
        return (downloaded, True) if downloaded else (None, True)

    # Clean up the source path
    src_clean = src.lstrip('/')

    # Try exact path first
    exact_path = content_dir / src_clean
    if exact_path.exists():
        return (exact_path, False)

    # Fuzzy match: search by filename
    filename = os.path.basename(src)
    if filename in image_index:
        matches = image_index[filename]
        if len(matches) == 1:
            return (matches[0], False)
        elif len(matches) > 1:
            print(f"     WARNING: Multiple matches for {filename}: {[str(m) for m in matches]}")
            return (matches[0], False)

    print(f"     WARNING: Image not found: {src}")
    return (None, False)


def parse_html_img_attrs(img_tag):
    """Parse attributes from an HTML img tag."""
    attrs = {}
    # Find all attribute matches
    for match in ATTR_PATTERN.finditer(img_tag):
        if match.group(1):  # Quoted attribute
            attrs[match.group(1).lower()] = match.group(2)
        elif match.group(3):  # Unquoted attribute
            attrs[match.group(3).lower()] = match.group(4)
    return attrs


def is_image_file(path):
    """Check if path is an image file."""
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def copy_image_to_bundle(src_path, bundle_dir, original_src):
    """
    Copy image to bundle directory, handling filename collisions.
    Returns the relative filename used.
    """
    filename = src_path.name
    dest_path = bundle_dir / filename

    # Handle filename collisions by adding suffix
    counter = 1
    while dest_path.exists():
        # Check if it's the same file
        if dest_path.stat().st_size == src_path.stat().st_size:
            # Likely the same file, reuse
            return filename

        stem = src_path.stem
        suffix = src_path.suffix
        filename = f"{stem}_{counter}{suffix}"
        dest_path = bundle_dir / filename
        counter += 1

    shutil.copy2(src_path, dest_path)
    return filename


def convert_to_page_bundle(md_file):
    """
    Convert a markdown file to a page bundle.
    Returns the bundle directory path.
    """
    # Already a bundle (index.md or _index.md)
    if md_file.name in ('index.md', '_index.md'):
        return md_file.parent

    # Create bundle directory
    bundle_name = md_file.stem
    bundle_dir = md_file.parent / bundle_name
    bundle_dir.mkdir(exist_ok=True)

    # Move the markdown file
    new_md_path = bundle_dir / 'index.md'
    shutil.move(str(md_file), str(new_md_path))

    return bundle_dir


def process_content_file(md_file, image_index, content_dir):
    """Process a single content file, converting images and paths."""
    content = md_file.read_text(encoding='utf-8')

    # Track images found
    images_found = []

    # Find clickable images first (to avoid double-matching)
    clickable_matches = list(CLICKABLE_IMAGE_PATTERN.finditer(content))

    # Find regular markdown images (excluding clickable ones)
    md_matches = []
    for match in MD_IMAGE_PATTERN.finditer(content):
        # Check if this match is part of a clickable image
        is_part_of_clickable = False
        for cm in clickable_matches:
            if cm.start() <= match.start() <= cm.end():
                is_part_of_clickable = True
                break
        if not is_part_of_clickable:
            md_matches.append(match)

    # Find HTML img tags
    html_matches = list(HTML_IMG_PATTERN.finditer(content))

    # Check if we need to process this file
    has_processable_images = False

    for match in clickable_matches:
        thumb_src = match.group(2)
        full_src = match.group(3)
        if is_image_file(thumb_src) or is_external_url(thumb_src):
            images_found.append(('clickable', match, thumb_src, full_src))
            has_processable_images = True

    for match in md_matches:
        src = match.group(2)
        if is_image_file(src) or is_external_url(src):
            images_found.append(('markdown', match, src, None))
            has_processable_images = True

    for match in html_matches:
        attrs = parse_html_img_attrs(match.group(0))
        src = attrs.get('src', '')
        if src and (is_image_file(src) or is_external_url(src)):
            images_found.append(('html', match, src, attrs))
            has_processable_images = True

    if not has_processable_images:
        return False  # No changes needed

    # Convert to page bundle
    bundle_dir = convert_to_page_bundle(md_file)

    # Update md_file path if it was moved
    if md_file.name not in ('index.md', '_index.md'):
        md_file = bundle_dir / 'index.md'
        content = md_file.read_text(encoding='utf-8')

    # Process images and update content (work backwards to preserve positions)
    replacements = []

    for img_type, match, src, extra in images_found:
        if img_type == 'clickable':
            thumb_src = src
            full_src = extra
            alt = match.group(1)

            # Resolve both images
            thumb_path, _ = resolve_image(thumb_src, image_index, content_dir)
            full_path, _ = resolve_image(full_src, image_index, content_dir)

            if thumb_path and full_path:
                thumb_name = copy_image_to_bundle(thumb_path, bundle_dir, thumb_src)
                full_name = copy_image_to_bundle(full_path, bundle_dir, full_src)

                # Create shortcode for clickable image
                new_markup = f'{{{{< image src="{full_name}" thumb="{thumb_name}" alt="{alt}" >}}}}'
                replacements.append((match.start(), match.end(), new_markup))
            elif thumb_path:
                thumb_name = copy_image_to_bundle(thumb_path, bundle_dir, thumb_src)
                new_markup = f'![{alt}]({thumb_name})'
                replacements.append((match.start(), match.end(), new_markup))

        elif img_type == 'markdown':
            alt = match.group(1)
            title = match.group(3) or ''

            local_path, _ = resolve_image(src, image_index, content_dir)

            if local_path:
                filename = copy_image_to_bundle(local_path, bundle_dir, src)
                title_part = f' "{title}"' if title else ''
                new_markup = f'![{alt}]({filename}{title_part})'
                replacements.append((match.start(), match.end(), new_markup))

        elif img_type == 'html':
            attrs = extra
            src = attrs.get('src', '')

            local_path, _ = resolve_image(src, image_index, content_dir)

            if local_path:
                filename = copy_image_to_bundle(local_path, bundle_dir, src)

                # Build shortcode with relevant attributes
                shortcode_parts = [f'src="{filename}"']

                if attrs.get('alt'):
                    shortcode_parts.append(f'alt="{attrs["alt"]}"')
                if attrs.get('title'):
                    shortcode_parts.append(f'title="{attrs["title"]}"')
                if attrs.get('width'):
                    shortcode_parts.append(f'width="{attrs["width"]}"')
                if attrs.get('height'):
                    shortcode_parts.append(f'height="{attrs["height"]}"')
                if attrs.get('class'):
                    shortcode_parts.append(f'class="{attrs["class"]}"')
                if attrs.get('style'):
                    shortcode_parts.append(f'style="{attrs["style"]}"')

                new_markup = '{{< image ' + ' '.join(shortcode_parts) + ' >}}'
                replacements.append((match.start(), match.end(), new_markup))

    # Apply replacements in reverse order
    replacements.sort(key=lambda x: x[0], reverse=True)
    for start, end, new_text in replacements:
        content = content[:start] + new_text + content[end:]

    # Write updated content
    md_file.write_text(content, encoding='utf-8')

    return True


def main():
    # Clean and copy content to output dir
    print(f"  1. Preparing output directory: {OUTPUT_DIR}")
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    shutil.copytree(INPUT_DIR, OUTPUT_DIR)
    print(f"     Copied {INPUT_DIR} -> {OUTPUT_DIR}")

    # Build image index for fuzzy matching
    print(f"  2. Building image index from {INPUT_DIR / 'images'}")
    image_index = build_image_index(INPUT_DIR / 'images')
    print(f"     Found {sum(len(v) for v in image_index.values())} images")

    # Find all content files
    processed_count = 0
    skipped_count = 0

    for md_file in sorted(OUTPUT_DIR.rglob('*.md')):
        # Skip the images directory
        if 'images' in md_file.parts:
            continue

        relative_path = md_file.relative_to(OUTPUT_DIR)
        try:
            if process_content_file(md_file, image_index, INPUT_DIR):
                processed_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"   ERROR: {e}")
            print(f"    -> {relative_path}")
            import traceback
            traceback.print_exc()

    # Remove the images directory from processed output
    # (images are now in page bundles)
    images_dir = OUTPUT_DIR / 'images'
    if images_dir.exists():
        print("  3. Removing processed images directory")
        shutil.rmtree(images_dir)

    print(f"  Done: Processed {processed_count} files, skipped {skipped_count}")


if __name__ == '__main__':
    main()
