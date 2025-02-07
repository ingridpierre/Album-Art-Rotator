from flask import Flask, render_template
import os
import socket
import logging
from app import app, db
from models import Album

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

@app.route('/')
def index():
    # Load albums from database
    albums = Album.query.all()
    return render_template('index.html', albums=[album.to_dict() for album in albums])

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