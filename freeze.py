from flask_frozen import Freezer
from app import app, get_posts
import os

# Set base URL from environment variable or use default
# For GitHub Pages: if repo is username.github.io, use https://username.github.io
# If repo is a project, use https://username.github.io/repo-name
BASE_URL = os.environ.get('BASE_URL', 'https://TMahlatini.github.io')
app.config['BASE_URL'] = BASE_URL

freezer = Freezer(app)

@freezer.register_generator
def post():
    """Generate URLs for all blog posts."""
    posts = get_posts()
    for post in posts:
        yield {'slug': post['slug']}

if __name__ == '__main__':
    freezer.freeze()

