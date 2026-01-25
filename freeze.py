from flask_frozen import Freezer
from app import app, get_posts
import os
import sys

# Set base URL from environment variable or use default
BASE_URL = os.environ.get('BASE_URL', 'https://www.terencemahlatini.com')
app.config['FREEZER_BASE_URL'] = BASE_URL

# Frozen-Flask configuration
app.config['FREEZER_DESTINATION'] = 'build'
app.config['FREEZER_REMOVE_EXTRA_FILES'] = True
app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True

freezer = Freezer(app)

@freezer.register_generator
def post():
    for post in get_posts():
        yield {'slug': post['slug']}

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        # Serve the built site locally
        print("Serving static site from 'build' directory...")
        freezer.run(debug=True )
    else:
        # Build the site
        print("Freezing the site...")
        freezer.freeze()
        
        # Create .nojekyll file for GitHub Pages
        nojekyll_path = os.path.join(app.config.get('FREEZER_DESTINATION', 'build'), '.nojekyll')
        with open(nojekyll_path, 'w') as f:
            f.write('')
        print(f"\nStatic site built successfully in '{app.config.get('FREEZER_DESTINATION', 'build')}' directory!")
