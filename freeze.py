import os
from werkzeug.routing import Map
if not hasattr(Map, 'charset'):
    Map.charset = 'utf-8'

from flask_frozen import Freezer
from app import app, get_posts

# Set base URL from environment variable or use default
# For GitHub Pages: if repo is username.github.io, use https://username.github.io
# If repo is a project, use https://username.github.io/repo-name
BASE_URL = os.environ.get('BASE_URL', 'https://TMahlatini.github.io')
app.config['BASE_URL'] = BASE_URL

# Additional compatibility: ensure url_map has charset attribute
if not hasattr(app.url_map, 'charset'):
    app.url_map.charset = 'utf-8'

freezer = Freezer(app)

@freezer.register_generator
def post():
    """Generate URLs for all blog posts."""
    posts = get_posts()
    for post in posts:
        yield {'slug': post['slug']}

if __name__ == '__main__':
    freezer.freeze()

