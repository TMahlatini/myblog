import os
import shutil
from app import app, get_posts

# Set base URL from environment variable or use default
BASE_URL = os.environ.get('BASE_URL', 'https://TMahlatini.github.io/myblog')
app.config['BASE_URL'] = BASE_URL

# Output directory
BUILD_DIR = 'build'

def build_static_site():
    """Build static site by rendering all routes."""
    # Create build directory
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    # Create test client with application context
    with app.app_context():
        client = app.test_client()
        
        # Build index page
        print("Building index page...")
        response = client.get('/')
        if response.status_code == 200:
            with open(os.path.join(BUILD_DIR, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
        
        # Build now page
        print("Building now page...")
        response = client.get('/now')
        if response.status_code == 200:
            with open(os.path.join(BUILD_DIR, 'now.html'), 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
        
        # Build blog page
        print("Building blog page...")
        response = client.get('/blog')
        if response.status_code == 200:
            with open(os.path.join(BUILD_DIR, 'blog.html'), 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
        
        # Build RSS feed
        print("Building RSS feed...")
        response = client.get('/feed.xml')
        if response.status_code == 200:
            with open(os.path.join(BUILD_DIR, 'feed.xml'), 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
        
        # Build individual post pages
        print("Building post pages...")
        posts = get_posts()
        for post in posts:
            slug = post['slug']
            response = client.get(f'/{slug}')
            if response.status_code == 200:
                # Create directory for post
                post_dir = os.path.join(BUILD_DIR, slug)
                os.makedirs(post_dir, exist_ok=True)
                with open(os.path.join(post_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(response.data.decode('utf-8'))
                print(f"  Built: /{slug}")
        
        # Build 404 page
        print("Building 404 page...")
        response = client.get('/404')
        if response.status_code == 200:
            with open(os.path.join(BUILD_DIR, '404.html'), 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
    
    # Copy static files
    print("Copying static files...")
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(BUILD_DIR, 'static'), dirs_exist_ok=True)
    
    # Create .nojekyll file for GitHub Pages
    print("Creating .nojekyll file...")
    with open(os.path.join(BUILD_DIR, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"\nStatic site built successfully in '{BUILD_DIR}' directory!")

if __name__ == '__main__':
    build_static_site()
