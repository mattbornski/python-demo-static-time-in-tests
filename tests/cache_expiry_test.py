from pathlib import Path
import sys
import vcr

from . import memoize

sys.path.append(str(Path(__file__.rsplit('/', 1)[0], '..', 'src', 'lib').resolve().absolute()))
import weather

def mock_client_with_cache():
    weather_client = weather.Client()
    weather_client.cache['94111'] = {'coord': {'lon': -122.42, 'lat': 37.78}, 'weather': [{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}], 'base': 'stations', 'main': {'temp': 294.85, 'pressure': 1013, 'humidity': 47, 'temp_min': 290.15, 'temp_max': 299.15}, 'visibility': 16093, 'wind': {'speed': 4.1, 'deg': 10, 'gust': 9.3}, 'clouds': {'all': 1}, 'dt': 1530135900, 'sys': {'type': 1, 'id': 438, 'message': 0.0045, 'country': 'US', 'sunrise': 1530103812, 'sunset': 1530156942}, 'id': 420008451, 'name': 'San Francisco', 'cod': 200}
    return weather_client

@vcr.use_cassette('cache_expiry_test')
@memoize.memoize_time()
def test_cache_expiry_with_memoization():
    weather_client = mock_client_with_cache()

    # Cache miss, go fetch.  The fetch has been recorded with VCR
    forecast = weather_client.get_forecast('10001')
    assert str(forecast['cod']) == '200'

    # Cache hit, and still within TTL
    forecast = weather_client.get_forecast('94111')
    assert str(forecast['cod']) == '200'



@vcr.use_cassette('cache_expiry_test')
def test_cache_expiry_without_memoization():
    weather_client = mock_client_with_cache()

    # Cache miss, go fetch.  The fetch has been recorded with VCR
    forecast = weather_client.get_forecast('10001')
    assert str(forecast['cod']) == '200'

    # Cache hit, but out of TTL because real time has advanced too far beyond time the fixture was recorded
    forecast = weather_client.get_forecast('94111')
    assert str(forecast['cod']) == '200'