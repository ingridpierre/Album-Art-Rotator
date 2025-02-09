import os
from flask import Flask
from cursor_manager import CursorManager

app = Flask(__name__)

# Initialize cursor manager with 3 second hide delay
cursor_manager = CursorManager(hide_after_seconds=3)

@app.before_first_request
def start_cursor_manager():
    cursor_manager.start_monitoring()

@app.teardown_appcontext
def cleanup(exception=None):
    cursor_manager.stop_monitoring()