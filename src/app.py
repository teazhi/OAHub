from flask import Flask
from auth import login
from gui import launch_gui
from threading import Thread
import sys

app = Flask(__name__)
app.secret_key = "super_secret_key"

app.add_url_rule('/login', view_func=login, methods=['POST'])

def run_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        launch_gui()
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)
