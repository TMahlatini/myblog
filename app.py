from flask import Flask, render_template, make_response, request
import os
import markdown
from datetime import datetime
from functools import wraps

app = Flask(__name__)


POSTS_DIR = 'posts'
SITE_TITLE = "Terence Mahlatini"
SITE_DESCRIPTION = ""

@app.context_processor
def inject_now():
    """Make current date/time available to all templates"""
    return {'now': datetime.now()}

@app.context_processor
def inject_current_path():
    """Make current path available to all templates"""
    return {'current_path': request.path}

def get_posts():
    posts = []
    if os.path.exists(POSTS_DIR):
        for filename in sorted(os.listdir(POSTS_DIR), reverse=True):
            if filename.endswith('.md'):
                filepath = os.path.join(POSTS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter (simple version)
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        body = parts[2]
                        
                        # Extract metadata
                        title = filename.replace('.md', '').replace('-', ' ').title()
                        date = None
                        tags = []
                        
                        for line in frontmatter.split('\n'):
                            line = line.strip()
                            if line.startswith('title:'):
                                title = line.split(':', 1)[1].strip().strip('"\'')
                            elif line.startswith('date:'):
                                date_str = line.split(':', 1)[1].strip().strip('"\'')
                                try:
                                    date = datetime.strptime(date_str, '%Y-%m-%d')
                                except:
                                    pass
                            elif line.startswith('tags:'):
                                tags_str = line.split(':', 1)[1].strip()
                                tags = [t.strip().strip('"\'[]') for t in tags_str.split(',')]
                        
                        posts.append({
                            'slug': filename.replace('.md', ''),
                            'title': title,
                            'date': date,
                            'tags': tags,
                            'content': markdown.markdown(body),
                            'excerpt': body.split('\n')[0][:150] + '...' if len(body) > 150 else body
                        })
    
    
    posts.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    return posts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/now')
def now():
    return render_template('now.html')

@app.route('/blog')
def blog():
    posts = get_posts()
    return render_template('blog.html', posts=posts)

@app.route('/<slug>')
def post(slug):
    posts = get_posts()
    post = next((p for p in posts if p['slug'] == slug), None)
    
    if not post:
        # Try to load directly from file
        filepath = os.path.join(POSTS_DIR, f'{slug}.md')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]
                    
                    title = slug.replace('-', ' ').title()
                    date = None
                    tags = []
                    
                    for line in frontmatter.split('\n'):
                        line = line.strip()
                        if line.startswith('title:'):
                            title = line.split(':', 1)[1].strip().strip('"\'')
                        elif line.startswith('date:'):
                            date_str = line.split(':', 1)[1].strip().strip('"\'')
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                            except:
                                pass
                        elif line.startswith('tags:'):
                            tags_str = line.split(':', 1)[1].strip()
                            tags = [t.strip().strip('"\'[]') for t in tags_str.split(',')]
                    
                    post = {
                        'slug': slug,
                        'title': title,
                        'date': date,
                        'tags': tags,
                        'content': markdown.markdown(body)
                    }
        
        if not post:
            return "Post not found", 404
    
    return render_template('post.html', post=post)

@app.route('/feed.xml')
def feed():
    """Generate RSS feed"""
    posts = get_posts()[:10]  # Last 10 posts
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{SITE_TITLE}</title>
        <description>{SITE_DESCRIPTION}</description>
        <link>http://localhost:5000</link>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
'''
    
    for post in posts:
        if post['date']:
            pub_date = post['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
        else:
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        rss += f'''        <item>
            <title>{post['title']}</title>
            <link>http://localhost:5000/{post['slug']}</link>
            <pubDate>{pub_date}</pubDate>
            <description><![CDATA[{post['excerpt']}]]></description>
        </item>
'''
    
    rss += '''    </channel>
</rss>'''
    
    response = make_response(rss)
    response.headers['Content-Type'] = 'application/rss+xml'
    return response

if __name__ == '__main__':
    app.run(debug=True)

