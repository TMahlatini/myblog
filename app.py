from flask import Flask, render_template, request
import os
import markdown
from datetime import datetime
import re

app = Flask(__name__)

POSTS_DIR = 'posts'
CONTENT_DIR = 'content'
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
    return render_template('index.html')


@app.route('/now/')
def now():
    now_content_path = os.path.join(CONTENT_DIR, 'now.md')
    now_card = load_markdown_file(now_content_path, 'now')
    return render_template('now.html', now_card=now_card)

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

