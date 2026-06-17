#!/usr/bin/env python3
"""
Notify Buttondown subscribers about new blog posts or now-page entries.
"""

import json
import os
import re
import sys

import requests
from dotenv import load_dotenv

POSTS_DIR = "posts"
NOW_DIR = os.path.join("content", "now")
MANIFEST_FILE = "notified.json"
BUTTONDOWN_API_URL = "https://api.buttondown.email/v1/emails"
NOW_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FRONTMATTER_TITLE_RE = re.compile(r"^title:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)


def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {"posts": [], "now": []}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def extract_title(filepath, fallback):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        match = FRONTMATTER_TITLE_RE.search(content)
        if match:
            return match.group(1).strip()
    except (IOError, OSError):
        pass
    return fallback


def send_email(api_key, subject, body):
    response = requests.post(
        BUTTONDOWN_API_URL,
        headers={
            "Authorization": f"Token {api_key}",
            "X-Buttondown-Live-Dangerously": "true",
        },
        json={"subject": subject, "body": body, "status": "about_to_send"},
        timeout=15,
    )
    response.raise_for_status()


def find_new_posts(manifest):
    notified = set(manifest.get("posts", []))
    new_posts = []
    if not os.path.isdir(POSTS_DIR):
        return new_posts
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"):
            continue
        slug = filename[:-3]
        if slug not in notified:
            new_posts.append(slug)
    return new_posts


def find_new_now_pages(manifest):
    notified = set(manifest.get("now", []))
    new_pages = []
    if not os.path.isdir(NOW_DIR):
        return new_pages
    for filename in os.listdir(NOW_DIR):
        if not filename.endswith(".md"):
            continue
        date_slug = filename[:-3]
        if NOW_DATE_PATTERN.match(date_slug) and date_slug not in notified:
            new_pages.append(date_slug)
    return new_pages


def main():
    load_dotenv()

    api_key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    site_url = os.environ.get("SITE_URL", "").strip().rstrip("/")

    if not api_key or api_key == "your_api_key_here":
        print("notify_subscribers: BUTTONDOWN_API_KEY not configured — skipping.", file=sys.stderr)
        sys.exit(0)

    if not site_url:
        print("notify_subscribers: SITE_URL not set in .env — skipping.", file=sys.stderr)
        sys.exit(0)

    manifest = load_manifest()
    new_posts = find_new_posts(manifest)
    new_now_pages = find_new_now_pages(manifest)

    if not new_posts and not new_now_pages:
        print("notify_subscribers: nothing new to announce.")
        sys.exit(0)

    errors = []

    for slug in new_posts:
        filepath = os.path.join(POSTS_DIR, f"{slug}.md")
        title = extract_title(filepath, slug.replace("-", " ").title())
        subject = f"New post: {title}"
        body = f"A new post is live.\n\nRead it here: {site_url}/{slug}/"
        try:
            send_email(api_key, subject, body)
            manifest.setdefault("posts", []).append(slug)
            print(f"notify_subscribers: sent email for post '{slug}'")
        except requests.RequestException as exc:
            errors.append(f"post '{slug}': {exc}")

    for date_slug in new_now_pages:
        subject = f"Now page updated: {date_slug}"
        body = f"A new now page entry ({date_slug}) is live.\n\nRead it here: {site_url}/now/{date_slug}/"
        try:
            send_email(api_key, subject, body)
            manifest.setdefault("now", []).append(date_slug)
            print(f"notify_subscribers: sent email for now page '{date_slug}'")
        except requests.RequestException as exc:
            errors.append(f"now page '{date_slug}': {exc}")

    save_manifest(manifest)

    if errors:
        print("notify_subscribers: some emails failed to send:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
