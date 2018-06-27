import contextlib
import datetime
import freezegun
import http.server
import json
from pathlib import Path
import requests
import sys
import time
import threading
import unittest.mock
import vcr

sys.path.append(str(Path(__file__.rsplit('/', 1)[0], '..', 'src', 'lib').resolve().absolute()))
import weather

class TimeServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        timestamp = time.time()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'timestamp': timestamp}).encode('utf-8'))

@contextlib.contextmanager
def memoize_time():
    # Takes advantage of VCR cassette stashing HTTP requests to make sure that we use the same time in our tests.
    # Streamlines the issue of capturing live data in recording but then having to update tests to use the same static
    # timestamp as the last recording.
    # Port needs to be fixed for VCR record/playback purposes, but the selection is arbitrary.
    port = 19718
    server_address = ('', port)
    time_server = http.server.HTTPServer(server_address, TimeServer)
    time_server_thread = threading.Thread(target=time_server.serve_forever)
    time_server_thread.start()

    # Check our time within cassette, if already recorded
    r = requests.get('http://127.0.0.1:{}'.format(port))
    with freezegun.freeze_time(datetime.datetime.utcfromtimestamp(r.json()['timestamp']).isoformat()):
        yield

    time_server.shutdown()
    time_server_thread.join()



@vcr.use_cassette
@memoize_time()
def test_cache_expiry():
    weather_client = weather.Client()

    # Our weather client should cache forecasts for a period, but not forever

