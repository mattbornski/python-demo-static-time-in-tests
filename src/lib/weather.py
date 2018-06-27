import os
import requests
import time

FORECAST_TTL = 3600

class Client(object):
    def __init__(self, **kwargs):
        self.cache = {}

    def get_forecast(self, zipcode):
        now = time.time()
        forecast = self.cache.get(zipcode, None)
        if forecast is not None and now < (forecast.get('dt', 0) + FORECAST_TTL):
            return forecast

        url = 'http://api.openweathermap.org/data/2.5/weather?zip={zipcode},us&appid={app_id}'.format(**{
            'zipcode': zipcode,
            'app_id': os.environ.get('OWM_APP_ID', 'YOUR_OWN_OWM_APP_ID'),
        })
        forecast = requests.get(url).json()
        self.cache[zipcode] = forecast

        return forecast

