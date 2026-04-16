from flask import Flask
import threading
from main import run

app = Flask(__name__)

@app.route('/')
def home():
    return "SwingMaker Bot läuft!"

@app.route('/run')
def trigger():
    thread = threading.Thread(target=run)
    thread.start()
    return "Scan gestartet", 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)