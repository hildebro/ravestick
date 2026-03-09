import json
import threading
import time

import numpy as np
from flask import Flask, render_template_string, Response

# This HTML uses a basic HTML5 Canvas to draw the bars and LEDs
WEB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ravestick Live Web</title>
    <style>
        body { background-color: #121212; color: white; display: flex; flex-direction: column; align-items: center; font-family: sans-serif; }
        canvas { background-color: #000; border: 1px solid #333; margin-top: 20px; box-shadow: 0 0 20px rgba(0,255,255,0.1); }
    </style>
</head>
<body>
    <h2>Ravestick Live Web Visualization</h2>
    <canvas id="viz" width="800" height="400"></canvas>

    <script>
        const canvas = document.getElementById('viz');
        const ctx = canvas.getContext('2d');
        
        // Connect to the Flask SSE stream
        const evtSource = new EventSource('/stream');
        
        evtSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 1. Draw the 64 background frequency bars
            ctx.fillStyle = 'rgba(80, 80, 80, 0.4)';
            const barWidth = canvas.width / data.bars.length;
            data.bars.forEach((val, i) => {
                // Scale the value (assuming a max amplitude around 6.0)
                const h = (val / 6.0) * canvas.height; 
                ctx.fillRect(i * barWidth, canvas.height - h, barWidth - 2, h);
            });
            
            // 2. Draw the 3 Vertical LED columns
            // X-positions for Bass, Mids, Highs
            const bandX = [canvas.width * 0.1, canvas.width * 0.5, canvas.width * 0.9]; 
            const ledSize = 15;
            const ledSpacing = 18;

            data.leds.forEach((bandColors, bandIdx) => {
                const x = bandX[bandIdx] - (ledSize / 2);
                
                bandColors.forEach((color, ledIdx) => {
                    ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
                    // Draw from bottom up
                    const y = canvas.height - (ledIdx * ledSpacing) - ledSize - 10;
                    ctx.fillRect(x, y, ledSize, ledSize);
                });
            });
        };
    </script>
</body>
</html>
"""


class WebDisplay:
    def __init__(self, port=5000):
        self.port = port
        self.active = True
        self.latest_data = {"bars": [], "leds": []}

        self.app = Flask(__name__)

        @self.app.route('/')
        def index():
            return render_template_string(WEB_TEMPLATE)

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
