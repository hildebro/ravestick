import json
import threading
import time

import numpy as np
from flask import Flask, render_template, Response


class WebDisplay:
    def __init__(self, port=5000):
        self.port = port
        self.active = True
        self.latest_data = {"bars": [], "leds": []}

        self.app = Flask(__name__)

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/stream')
        def stream():
            def generate():
                while self.active:
                    # stream the latest data as JSON
                    yield f"data: {json.dumps(self.latest_data)}\n\n"
                    # cap at ~30 FPS so we don't crash the browser
                    time.sleep(0.033)

            return Response(generate(), mimetype='text/event-stream')

        # start the web server in a background thread so it doesn't block audio
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Web server started at http://localhost:{self.port}")

    def _run_server(self):
        # mute Flask's standard output for a cleaner console
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

    def update(self, frequency_bars, led_colors):
        """Updates the shared state. The web client pulls from this."""
        self.latest_data = {
            "bars": np.nan_to_num(frequency_bars).tolist(),
            "leds": np.nan_to_num(led_colors).tolist()
        }

    def is_active(self):
        return self.active
