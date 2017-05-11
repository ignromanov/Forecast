import forecastio
import forecast_messages
from datetime import datetime, timedelta
import pytz
import config


def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0


def fill_time_to_data_dic(forecast_by_hours, datetime_beg, datetime_end):
    dic = {}
    aver_dic = {"apparentTemperature": 0, "precipProbability": 0, "precipIntensity": 0}
    for data_point in forecast_by_hours.data:
        data_point_time = data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if datetime_beg <= data_point_time <= datetime_end:
            dic[data_point_time.hour] = data_point
            aver_dic["apparentTemperature"] += data_point.apparentTemperature
            aver_dic["precipProbability"] += data_point.precipProbability
            aver_dic["precipIntensity"] += data_point.precipIntensity

    for key in aver_dic.keys(): aver_dic[key] = round(aver_dic[key] / len(dic), 2)

    return dic, aver_dic


def average_date_datapoint(forecast_by_days, datetime_date):
    for data_point in forecast_by_days.data:
        data_point_time = data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        # if data_point_time.date == datetime_date.date:
        print("average by day - temp: {} - {}, precibProb: {}, precibIntens: {}".format(
            round(data_point.apparentTemperatureMin, 1),
            round(data_point.apparentTemperatureMax, 1),
            round(data_point.precipProbability, 1),
            round(data_point.precipIntensity, 1)))
        return data_point


def current_weather(lat, lng):
    return forecast_messages.current_weather(
        forecastio.load_forecast(config.FORECAST_KEY, lat, lng).currently())


def today_smart_weather(lat, lng, **kwargs):
    now = datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(minute=0, second=0, microsecond=0)
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    # print('past weather:')
    past_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng, time=yesterday)
    past_weather_dic, past_weather_aver_dic = fill_time_to_data_dic(
        past_forecastio.hourly(),
        yesterday.replace(hour=7),
        yesterday.replace(hour=23))

    # print('future weather:')
    future_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng)
    future_weather_dic, future_weather_aver_dic = fill_time_to_data_dic(
        future_forecastio.hourly(),
        now.replace(hour=7),
        now.replace(hour=23))

    return compare_avr_weathers(past_weather_aver_dic, future_weather_aver_dic)


def nearest_weather_change(lat, lng, **kwargs):
    now = datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(minute=0, second=0, microsecond=0)
    yesterday = now - timedelta(days=1)

    # print('past weather:')
    past_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng, time=yesterday)
    past_data_point = past_forecastio.daily().data[0]

    future_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng)
    compare_result = ''
    for next_data_point in future_forecastio.daily().data:
        compare_result += compare_daily_weathers(past_data_point, next_data_point)

    return compare_result


def compare_avr_weathers(past_weather, future_weather):
    result = 'Существенного изменения погоды в ближайшие сутки не ожидается'
    if past_weather["precipProbability"] > 0.0 and future_weather["precipProbability"] == 0.0:
        result = 'Осадки прекратятся'
    elif past_weather["precipProbability"] == 0.0 and future_weather["precipProbability"] > 0.0:
        if future_weather["precipIntensity"] > config.precipintens_delta:
            result = 'Будут интенсивные осадки'
        else:
            result = 'Будут осадки слабой интенсивности'

    avr_temp_delta = round(future_weather["apparentTemperature"] - past_weather["apparentTemperature"], 0)
    if avr_temp_delta > config.temp_delta:
        result = 'Потеплеет на {} градуса'.format(avr_temp_delta)
    elif avr_temp_delta < -config.temp_delta:
        result = 'Похолодает на {} градуса'.format(-avr_temp_delta)

    return result


def compare_daily_weathers(past_data_point, future_data_point):
    past_weather = {"precipProbability": past_data_point.precipProbability,
                    "precipIntensity": past_data_point.precipIntensity,
                    "apparentTemperature": past_data_point.apparentTemperatureMax}

    future_weather = {"precipProbability": future_data_point.precipProbability,
                      "precipIntensity": future_data_point.precipIntensity,
                      "apparentTemperature": future_data_point.apparentTemperatureMax}

    return 'Date: {} : {}\n'.format(
        future_data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow')),
        compare_avr_weathers(past_weather, future_weather))
