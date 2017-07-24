#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import requests
import threading

from forecastio.models import Forecast
import pytz

from config import __config__

_weather_emoji_dic = {
    'clear-day': '☀️',
    'clear-night': '🌓',
    'rain': '🌧️',
    'snow': '🌨️',
    'sleet': '🌨️',
    'wind': '🌬️️',
    'fog': '🌫️',
    'cloudy': '☁️',
    'partly-cloudy-day': '⛅',
    'partly-cloudy-night': '⛅'
}

_all_excluded_datablocks = 'minutely,currently,hourly,daily,alerts,flags'.split(',')


def _get_emoji_by_icon(icon):
    if icon in _weather_emoji_dic:
        return _weather_emoji_dic[icon]
    else:
        return ''


class WeatherForecast(object):
    def __init__(self, lat, lng, tz):
        self.__FORECAST_URL = "%s/%s/" % (__config__.FORECAST_URL, __config__.FORECAST_KEY)

        self.lat = lat
        self.lng = lng
        self.local_tz = pytz.timezone(tz)

    def get_current_weather(self):
        forecast_currently = self._load_forecast(included_datablocks='currently').currently()
        return '''{emoji}\n 🌡️ {temp} ℃ (ощущается как {apparent_temp} ℃), 
        ☁ {cloud}%'''.format(
            emoji=_get_emoji_by_icon(forecast_currently.icon), temp=int(round(forecast_currently.temperature, 0)),
            apparent_temp=int(round(forecast_currently.apparentTemperature, 0)),
            cloud=int(round(forecast_currently.cloudCover, 2) * 100))

    def get_timezone_by_coords(self):
        return self._load_forecast(included_datablocks='').json['timezone']

    def today_smart_weather(self):
        now = datetime.now(self.local_tz).replace(minute=0, second=0, microsecond=0)
        yesterday = now - timedelta(days=1)
        # tomorrow = now + timedelta(days=1)

        # print('past weather:')
        yesterday_datablock = \
            self._load_forecast(time=yesterday, included_datablocks='hourly').hourly()

        yesterday_datapoints, yesterday_avr_weather = \
            self._get_avr_weather(
                yesterday_datablock.data,
                yesterday.replace(hour=max(7, yesterday.hour)),
                yesterday.replace(hour=23))

        # print('future weather:')
        today_datablock = \
            self._load_forecast(included_datablocks='hourly').hourly()

        today_datapoints, today_avr_weather = \
            self._get_avr_weather(
                today_datablock.data,
                now.replace(hour=max(7, now.hour)),
                now.replace(hour=23))

        return self._compare_avr_weathers(yesterday_avr_weather, today_avr_weather)

    def nearest_weather_change(self):
        now = datetime.now(self.local_tz).replace(minute=0, second=0, microsecond=0)
        yesterday = now - timedelta(days=1)

        # print('past weather:')
        yesterday_datablock = \
            self._load_forecast(time=yesterday, included_datablocks='daily').daily()
        yesterday_datapoint = yesterday_datablock.data[0]

        today_datablock = \
            self._load_forecast(included_datablocks='daily').daily()
        today_datapoints = today_datablock.data

        compare_text = ''
        prev_datapoint = yesterday_datapoint
        for next_datapoint in today_datapoints:
            compare_text += self._compare_daily_weathers(prev_datapoint, next_datapoint)
            prev_datapoint = next_datapoint

        return compare_text

    def _get_avr_weather(self, datapoints, from_datetime, to_datetime):
        filtered_datapoints = {}
        avr_weather = {"apparentTemperature": 0, "precipProbability": 0, "precipIntensity": 0}
        for datapoint in datapoints:
            datapoint_time_local = datapoint.time.replace(tzinfo=pytz.utc).astimezone(self.local_tz)
            if from_datetime <= datapoint_time_local <= to_datetime:
                filtered_datapoints[datapoint_time_local.hour] = datapoint
                avr_weather["apparentTemperature"] += datapoint.apparentTemperature
                avr_weather["precipProbability"] += datapoint.precipProbability
                avr_weather["precipIntensity"] += datapoint.precipIntensity

        for key in avr_weather.keys():
            avr_weather[key] = round(avr_weather[key] / len(filtered_datapoints), 2)

        return filtered_datapoints, avr_weather

    @staticmethod
    def _compare_avr_weathers(yesterday_avr_weather, today_avr_weather):
        message = ''

        if yesterday_avr_weather["precipProbability"] > 0.0 and today_avr_weather["precipProbability"] == 0.0:
            message = ('Осадки прекратятся ')
        elif yesterday_avr_weather["precipProbability"] == 0.0 and today_avr_weather["precipProbability"] > 0.0:
            if today_avr_weather["precipIntensity"] > __config__.precipintens_delta:
                message += ('Будут интенсивные осадки ')
            else:
                message += ('Будут осадки слабой интенсивности ')

        avr_temp_delta = round(today_avr_weather["apparentTemperature"] - yesterday_avr_weather["apparentTemperature"],
                               0)
        if avr_temp_delta > __config__.temp_delta:
            message += ('Потеплеет на {} градуса').format(avr_temp_delta)
        elif avr_temp_delta < -__config__.temp_delta:
            message += ('Похолодает на {} градуса').format(-avr_temp_delta)

        if not message:
            message = ('Существенного изменения погоды в ближайшие сутки не ожидается')

        return message

    def _compare_daily_weathers(self, prev_datapoint, next_datapoint):
        prev_weather = {"precipProbability": prev_datapoint.precipProbability,
                        "precipIntensity": prev_datapoint.precipIntensity,
                        "apparentTemperature": prev_datapoint.apparentTemperatureMax}

        next_weather = {"precipProbability": next_datapoint.precipProbability,
                          "precipIntensity": next_datapoint.precipIntensity,
                          "apparentTemperature": next_datapoint.apparentTemperatureMax}

        return '{}: {} (t:{}, p:{},{})\n'.format(
            next_datapoint.time.strftime('%d.%m.%Y'),
            self._compare_avr_weathers(prev_weather, next_weather),
            next_datapoint.apparentTemperatureMax,
            next_datapoint.precipProbability,
            next_datapoint.precipIntensity
        )

    def _FtoC(self, fahrenheit):
        return (fahrenheit - 32) * 5.0 / 9.0

    def _average_date_datapoint(self, forecast_by_days, datetime_date):
        for data_point in forecast_by_days.data:
            data_point_time = data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
            # if data_point_time.date == datetime_date.date:
            print("average by day - temp: {} - {}, precibProb: {}, precibIntens: {}".format(
                round(data_point.apparentTemperatureMin, 1),
                round(data_point.apparentTemperatureMax, 1),
                round(data_point.precipProbability, 1),
                round(data_point.precipIntensity, 1)))
            return data_point

    def _load_forecast(self, time=None, units="auto", included_datablocks=None,
                       callback=None):
        """
            This function builds the request url and loads some or all of the
            needed json depending on lazy is True
    
            inLat:  The latitude of the forecast
            inLong: The longitude of the forecast
            time:   A datetime.datetime object representing the desired time of
                   the forecast. If no timezone is present, the API assumes local
                   time at the provided latitude and longitude.
            units:  A string of the preferred units of measurement, "auto" id
                    default. also us,ca,uk,si is available
            lazy:   Defaults to false.  The function will only request the json
                    data as it is needed. Results in more requests, but
                    probably a faster response time (I haven't checked)
        """

        if time is None:
            request_params = '%s,%s?units=%s' % \
                             (self.lat, self.lng, units,)
        else:
            url_time = time.replace(microsecond=0).isoformat()  # API returns 400 for microseconds
            request_params = '%s,%s,%s?units=%s' % \
                             (self.lat, self.lng, url_time, units,)

        if included_datablocks is not None:
            excluded_datablocks = \
                [x for x in _all_excluded_datablocks if x not in included_datablocks.split(',')]
            request_params = "%s&exclude=%s" % \
                             (request_params, ','.join(excluded_datablocks))

        self.request_url = "%s%s" % (self.__FORECAST_URL, request_params)

        return self._load_forecast_manual(callback=callback)

    def _load_forecast_manual(self, callback=None):
        """
            This function is used by load_forecast OR by users to manually
            construct the URL for an API call.
        """

        if callback is None:
            return self._request_forecast()
        else:
            thread = threading.Thread(target=self.load_async,
                                      args=(self.request_url, callback))
            thread.start()

    def _request_forecast(self):
        forecastio_response = requests.get(self.request_url)
        forecastio_response.raise_for_status()

        return Forecast(forecastio_response.json(), forecastio_response, forecastio_response.headers)

    def load_async(self, callback):
        callback(self._request_forecast())
