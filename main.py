from flask import Flask, render_template
import threading
import json
import request
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=request.main, daemon=True).start()
    app.run(host='0.0.0.0', port=3000)