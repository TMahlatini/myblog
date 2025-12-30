from flask import Flask, render_template, make_response, request, url_for
import os
import markdown
from datetime import datetime
from html import escape
import re

app = Flask(__name__)

POSTS_DIR = 'posts'
SITE_TITLE = "Terence Mahlatini"
SITE_DESCRIPTION = ""


def parse_frontmatter(content, slug):
    """Parse frontmatter from markdown content and return metadata and body."""
    title = slug.replace('-', ' ').title()
    date = None
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
                elif line.startswith('date:'):
                    date_str = line.split(':', 1)[1].strip().strip('"\'')
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
    
    return {
        'title': title,
        'date': date,
        'body': body
    }


def load_post_from_file(slug):
    """Load and parse a single post file."""
    # Security: prevent path traversal
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return None
    
    filepath = os.path.join(POSTS_DIR, f'{slug}.md')
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        return None
    
    metadata = parse_frontmatter(content, slug)
    
    return {
        'slug': slug,
        'title': metadata['title'],
        'date': metadata['date'],
        'content': markdown.markdown(metadata['body']),
        'excerpt': (metadata['body'].split('\n')[0][:150] + '...' 
                   if len(metadata['body']) > 150 else metadata['body'])
    }


def get_posts():
    """Get all posts sorted by date."""
    posts = []
    
    if not os.path.exists(POSTS_DIR):
        return posts
    
    try:
        filenames = sorted(os.listdir(POSTS_DIR), reverse=True)
    except (IOError, OSError):
        return posts
    
    for filename in filenames:
        if not filename.endswith('.md'):
            continue
        
        slug = filename.replace('.md', '')
        post = load_post_from_file(slug)
        
        if post:
            posts.append(post)
    
    posts.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
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


@app.route('/now')
def now():
    return render_template('now.html')

@app.route('/blog')
def blog():
    posts = get_posts()
    # Group posts by year
    posts_by_year = {}
    for post in posts:
        year = post['date'].year if post['date'] else 'Unknown'
        if year not in posts_by_year:
            posts_by_year[year] = []
        posts_by_year[year].append(post)
    
    sorted_years = sorted(posts_by_year.keys(), reverse=True)
    return render_template('blog.html', posts_by_year=posts_by_year, sorted_years=sorted_years)

@app.route('/<slug>')
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

@app.route('/feed.xml')
def feed():
    """Generate RSS feed"""
    posts = get_posts()[:10]  # Last 10 posts
    
    # Use url_for to generate proper URLs
    base_url = request.url_root.rstrip('/')
    
    # Format date for RSS (RFC 822 format)
    now = datetime.now()
    last_build_date = now.strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{escape(SITE_TITLE)}</title>
        <description>{escape(SITE_DESCRIPTION)}</description>
        <link>{base_url}</link>
        <lastBuildDate>{last_build_date}</lastBuildDate>
'''
    
    for post in posts:
        if post['date']:
            pub_date = post['date'].strftime('%a, %d %b %Y %H:%M:%S +0000')
        else:
            pub_date = last_build_date
        
        post_url = f"{base_url}{url_for('post', slug=post['slug'])}"
        post_title = escape(post['title'])
        post_excerpt = escape(post.get('excerpt', ''))
        
        rss += f'''        <item>
            <title>{post_title}</title>
            <link>{post_url}</link>
            <pubDate>{pub_date}</pubDate>
            <description><![CDATA[{post_excerpt}]]></description>
        </item>
'''
    
    rss += '''    </channel>
</rss>'''
    
    response = make_response(rss)
    response.headers['Content-Type'] = 'application/rss+xml'
    return response

if __name__ == '__main__':
    app.run(debug=True)

