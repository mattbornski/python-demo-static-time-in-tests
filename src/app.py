#!/usr/bin/env python3

import arrow
from pathlib import Path
import pytemperature
import sys
import time

sys.path.append(str(Path(__file__.rsplit('/', 1)[0], 'lib').resolve().absolute()))
import weather

if __name__ == '__main__':
    weather_client = weather.Client()
    while True:
        zipcode = input('Zipcode? ').strip()
        if len(zipcode) == 0:
            break

        forecast = weather_client.get_forecast(zipcode)
        # OWM API appears inconsistent with strings/integers in this field
        if str(forecast['cod']) != '200':
            print(forecast['message'])
            continue

        print('Weather for {zipcode} ({city}):'.format(zipcode=zipcode, city=forecast['name']))

        temp = pytemperature.k2f(forecast['main']['temp'])
        print('  {temp}° F'.format(temp=temp))

        for item in forecast['weather']:
            print('  {main}'.format(**item))

        now = time.time()
        for event in ['sunrise', 'sunset']:
            if now < forecast['sys'][event]:
                human_offset = arrow.Arrow.fromtimestamp(forecast['sys'][event]).humanize()
                print('  {event} {human_offset}'.format(event=event.capitalize(), human_offset=human_offset))
                break
  
        print('')
