from flask import Flask, redirect, render_template, request, url_for
import os
import markdown
from datetime import datetime
import re

app = Flask(__name__)

POSTS_DIR = 'posts'
CONTENT_DIR = 'content'
NOW_DIR = os.path.join(CONTENT_DIR, 'now')
NOW_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SITE_TITLE = "Terence Mahlatini"


def parse_frontmatter(content, slug):
    """Parse frontmatter from markdown content and return metadata and body."""
    title = slug.replace('-', ' ').title()
    published = None
    modified = None
    body = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
            
            for line in frontmatter.split('\n'):
                line = line.strip()
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
    
    return {
        'title': title,
        'published': published,
        'modified': modified,
        'body': body
    }


def load_markdown_file(filepath, slug):
    """Load and parse a markdown file with optional frontmatter."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
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
        'content': markdown.markdown(
            metadata['body'],
            extensions=['fenced_code', 'pymdownx.tilde']
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


@app.context_processor
def inject_now():
    """Make current date/time available to all templates"""
    return {'now': datetime.now()}


@app.context_processor
def inject_current_path():
    """Make current path available to all templates"""
    return {'current_path': request.path}


@app.route('/')
def index():
    index_content_path = os.path.join(CONTENT_DIR, 'index.md')
    index_card = load_markdown_file(index_content_path, 'index')
    recent_posts = get_posts()[:2]
    return render_template('index.html', index_card=index_card, recent_posts=recent_posts)


@app.route('/now/')
def now():
    pages = get_now_pages()
    latest = pages[0] if pages else None
    archives = pages[1:]
    return render_template('now.html', now_card=latest, archives=archives)


@app.route('/now/<date>/')
def now_archive(date):
    if not NOW_DATE_PATTERN.match(date):
        return "Invalid date", 400

    pages = get_now_pages()
    if not pages:
        return "Not found", 404

    if pages[0]['date'].strftime('%Y-%m-%d') == date:
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
    )

@app.route('/blog/')
def blog():
    posts = get_posts()
    # Group posts by year
    posts_by_year = {}
    for post in posts:
        year = post['published'].year if post['published'] else 'Unknown'
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)
    
    # Sort years: numeric years descending, then 'Unknown' at the end
    sorted_years = sorted(
        posts_by_year.keys(),
        key=lambda x: (x == 'Unknown', -x if isinstance(x, int) else 0)
    )
    return render_template('blog.html', posts_by_year=posts_by_year, sorted_years=sorted_years)

@app.route('/<slug>/')
def post(slug):
    # Security: validate slug format
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return "Invalid post slug", 400
    
    
    post = load_post_from_file(slug)
    
    if not post:
        # Fallback: search in all posts (in case file wasn't found but exists in cache)
        posts = get_posts()
        post = next((p for p in posts if p['slug'] == slug), None)
    
    if not post:
        return "Post not found", 404
    
    return render_template('post.html', post=post)

@app.route('/404/')
def page_not_found():
    """404 page for GitHub Pages"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

