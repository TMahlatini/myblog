from flask import Flask, render_template, request, url_for
import os
import markdown
import yaml
from datetime import datetime
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from urllib.parse import urlparse
import re

app = Flask(__name__)

POSTS_DIR = 'posts'
BOOKS_FILE = 'books.yaml'
CONTENT_DIR = 'content'
NOW_DIR = os.path.join(CONTENT_DIR, 'now')
NOW_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
SITE_TITLE = "Terence Mahlatini"
SITE_HOSTS = frozenset({'terencemahlatini.com', 'www.terencemahlatini.com'})


class ExternalLinkTreeprocessor(Treeprocessor):
    """Open off-site links in a new tab."""

    def run(self, root):
        for element in root.iter('a'):
            href = element.get('href', '')
            if not href.startswith(('http://', 'https://')):
                continue
            host = (urlparse(href).hostname or '').lower()
            if host in SITE_HOSTS:
                continue
            element.set('target', '_blank')
            element.set('rel', 'noopener noreferrer')
        return root


class ExternalLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ExternalLinkTreeprocessor(md), 'externallink', 15)


def parse_frontmatter(content, slug):
    """Parse frontmatter from markdown content and return metadata and body."""
    title = slug.replace('-', ' ').title()
    published = None
    modified = None
    tags = []
    reading = []
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            in_reading = False

            for raw_line in frontmatter.split('\n'):
                line = raw_line.strip()
                if not line:
                    continue

                if in_reading:
                    if line.startswith('- '):
                        item = line[2:].strip().strip('"\'')
                        if item:
                            reading.append(item)
                        continue
                    in_reading = False

                if line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                elif line.startswith('published:'):
                    date_str = line.split(':', 1)[1].strip().strip('"\'')
                    try:
                        published = datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                elif line.startswith('modified:'):
                    date_str = line.split(':', 1)[1].strip().strip('"\'')
                    try:
                        modified = datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                elif line.startswith('tags:') or line.startswith('tag:'):
                    value = line.split(':', 1)[1].strip().strip('"\'')
                    if value:
                        tags = [t.strip().strip('"\'') for t in value.split(',') if t.strip()]
                elif line.startswith('reading:'):
                    in_reading = True

    return {
        'title': title,
        'published': published,
        'modified': modified,
        'tags': tags,
        'reading': reading,
        'body': body
    }


def load_markdown_file(filepath, slug):
    """Load and parse a markdown file with optional frontmatter."""
    if not SLUG_PATTERN.match(slug) and not NOW_DATE_PATTERN.match(slug):
        return None

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        return None

    metadata = parse_frontmatter(content, slug)

    return {
        'title': metadata['title'],
        'published': metadata['published'],
        'modified': metadata['modified'],
        'tags': metadata['tags'],
        'reading': metadata['reading'],
        'content': markdown.markdown(
            metadata['body'],
            extensions=['fenced_code', 'pymdownx.tilde', ExternalLinkExtension()]
        )
    }


def load_post_from_file(slug):
    """Load and parse a single post file."""
    filepath = os.path.join(POSTS_DIR, f'{slug}.md')
    post = load_markdown_file(filepath, slug)

    if not post:
        return None

    return {
        'slug': slug,
        **post
    }


def get_posts():
    """Get all posts sorted by published date."""
    posts = []

    if not os.path.exists(POSTS_DIR):
        return posts

    try:
        filenames = os.listdir(POSTS_DIR)
    except (IOError, OSError):
        return posts

    for filename in filenames:
        if not filename.endswith('.md'):
            continue

        slug = filename.replace('.md', '')
        post = load_post_from_file(slug)

        if post:
            posts.append(post)

    posts.sort(key=lambda x: x['published'] or datetime.min, reverse=True)
    return posts


def get_books():
    """Get all books in catalog order."""
    books = []
    if not os.path.exists(BOOKS_FILE):
        return books
    try:
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            catalog = yaml.safe_load(f) or {}
    except (IOError, OSError, yaml.YAMLError):
        return books
    if not isinstance(catalog, dict):
        return books
    for slug, meta in catalog.items():
        if not SLUG_PATTERN.match(str(slug)) or not isinstance(meta, dict):
            continue
        books.append({
            'slug': slug,
            'title': meta.get('title') or slug.replace('-', ' ').title(),
            'author': meta.get('author') or '',
        })
    return books


def load_now_page(date_slug):
    """Load and parse a single now page snapshot."""
    if not NOW_DATE_PATTERN.match(date_slug):
        return None

    filepath = os.path.join(NOW_DIR, f'{date_slug}.md')
    page = load_markdown_file(filepath, date_slug)

    if not page:
        return None

    try:
        page_date = datetime.strptime(date_slug, '%Y-%m-%d')
    except ValueError:
        return None

    return {
        'date': page_date,
        **page,
        'modified': page_date,
    }


def get_now_pages():
    """Get all now page snapshots sorted by date descending."""
    pages = []

    if not os.path.exists(NOW_DIR):
        return pages

    try:
        filenames = os.listdir(NOW_DIR)
    except (IOError, OSError):
        return pages

    for filename in filenames:
        if not filename.endswith('.md'):
            continue

        date_slug = filename.replace('.md', '')
        if not NOW_DATE_PATTERN.match(date_slug):
            continue

        page = load_now_page(date_slug)
        if page:
            pages.append(page)

    pages.sort(key=lambda x: x['date'], reverse=True)
    return pages


def resolve_reading_books(slugs, books):
    by_slug = {b['slug']: b for b in books}
    return [by_slug[s] for s in slugs if s in by_slug]


@app.context_processor
def inject_now():
    """Make current date/time available to all templates"""
    return {'now': datetime.now()}


@app.context_processor
def inject_current_path():
    """Make current path available to all templates"""
    return {'current_path': request.path, 'site_title': SITE_TITLE}


@app.route('/')
def index():
    return render_template(
        'index.html',
        posts=get_posts(),
    )


@app.route('/about/')
def about():
    about_path = os.path.join(CONTENT_DIR, 'index.md')
    about_card = load_markdown_file(about_path, 'index')
    return render_template('about.html', about_card=about_card)


@app.route('/now/')
def now():
    pages = get_now_pages()
    latest = pages[0] if pages else None
    archives = pages[1:]
    books = get_books()
    reading_books = resolve_reading_books(latest.get('reading') or [], books) if latest else []
    return render_template(
        'now.html',
        now_card=latest,
        archives=archives,
        reading_books=reading_books,
    )


@app.route('/now/<date>/')
def now_archive(date):
    if not NOW_DATE_PATTERN.match(date):
        return "Invalid date", 400

    pages = get_now_pages()
    if not pages:
        return "Not found", 404

    if pages[0]['date'].strftime('%Y-%m-%d') == date:
        from flask import redirect
        return redirect(url_for('now'))

    now_card = load_now_page(date)
    if not now_card:
        return "Not found", 404

    archives = [p for p in pages[1:] if p['date'] != now_card['date']]
    return render_template(
        'now.html',
        now_card=now_card,
        archives=archives,
        is_archive=True,
        reading_books=[],
    )


@app.route('/<slug>/')
def entry(slug):
    if not SLUG_PATTERN.match(slug):
        return "Invalid slug", 400

    post = load_post_from_file(slug)
    if post:
        return render_template('post.html', post=post)

    return "Not found", 404


@app.route('/404.html')
def page_not_found():
    """404 page for GitHub Pages"""
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
