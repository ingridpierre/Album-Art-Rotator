from flask import Flask, render_template, request, jsonify
import os
import socket
import logging
import json
from discogs_scraper import DiscogsCollectionScraper

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def find_free_port(start_port=5000, max_port=5100):
    """Find a free port to use by testing ports sequentially."""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError('No free ports found in range')

def load_album_data():
    """Load album metadata from JSON file."""
    try:
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], 'albums.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        app.logger.error(f"Error loading album data: {str(e)}")
    return []

@app.route('/')
def index():
    # Load album metadata
    albums = load_album_data()
    if not albums:
        # Fallback to just listing image files if no metadata
        albums = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and not filename.startswith('.'):
                albums.append({'filename': filename, 'title': filename, 'artist': ''})

    return render_template('index.html', albums=albums)

@app.route('/sync_albums', methods=['POST'])
def sync_albums():
    try:
        token = os.environ.get('DISCOGS_TOKEN')
        if not token:
            return jsonify({'success': False, 'error': 'Discogs token not configured'}), 400

        username = os.environ.get('DISCOGS_USERNAME', 'ingridvp')
        scraper = DiscogsCollectionScraper(username, token)
        albums = scraper.scrape_collection()

        return jsonify({
            'success': True,
            'message': f'Successfully synced {len(albums)} albums'
        })
    except Exception as e:
        app.logger.error(f"Error syncing albums: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(logging.DEBUG)

    try:
        # Find an available port
        port = find_free_port()
        app.logger.info(f"Starting Flask application on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        app.logger.error(f"Failed to start application: {str(e)}")
        raise