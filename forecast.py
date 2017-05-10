import forecastio
import datetime
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
            # print("date: {}, temp: {}, precibProb: {}, precibIntens: {}".format(
            #     data_point_time.strftime('%Y-%m-%d %H:%M:%S %z %Z'),
            #     data_point.apparentTemperature,
            #     data_point.precipProbability,
            #     data_point.precipIntensity))
            aver_dic["apparentTemperature"] += data_point.apparentTemperature
            aver_dic["precipProbability"] += data_point.precipProbability
            aver_dic["precipIntensity"] += data_point.precipIntensity

    for key in aver_dic.keys(): aver_dic[key] = round(aver_dic[key] / len(dic), 2) 

    # print('average temp: {}, precibProb: {}, precibIntens: {}'.format(
    #     round(aver_dic["apparentTemperature"],2),
    #     round(aver_dic["precipProbability"],2),
    #     round(aver_dic["precipIntensity"],2)
    #     ))
    return dic, aver_dic


def average_date_datapoint(forecast_by_days, datetime_date):
    for data_point in forecast_by_days.data:
        data_point_time = data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        # if data_point_time.date == datetime_date.date:
        print("average by day - temp: {} - {}, precibProb: {}, precibIntens: {}".format(
            round(data_point.apparentTemperatureMin,1),
            round(data_point.apparentTemperatureMax,1),
            round(data_point.precipProbability,1),
            round(data_point.precipIntensity,1)))
        return data_point

def get_data_point_weather(dataPoint):
    return "current weather is temp: {}, precibProb: {}, precibIntens: {}".format(
        dataPoint.apparentTemperature,
        dataPoint.precipProbability,
        dataPoint.precipIntensity)


def get_current_weather(lat, lng):
    return get_data_point_weather(forecastio.load_forecast(config.FORECAST_KEY, lat, lng).currently())


def get_smart_weather(lat, lng):
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(minute=0, second=0, microsecond=0)
    yesterday = now - datetime.timedelta(days=1)
    tomorrow = now + datetime.timedelta(days=1)

    # print('past weather:')
    past_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng, time=now)
    past_weather_dic, past_weather_aver_dic = fill_time_to_data_dic(
        past_forecastio.hourly(),
        now.replace(hour=7),
        now.replace(hour=23))


    # print('future weather:')
    future_forecastio = forecastio.load_forecast(config.FORECAST_KEY, lat, lng)
    future_weather_dic, future_weather_aver_dic = fill_time_to_data_dic(
        future_forecastio.hourly(),
        tomorrow.replace(hour=7),
        tomorrow.replace(hour=23))


    # print('smart weather informer:')

    result = 'Никаких изменений погоды'
    if past_weather_aver_dic["precipProbability"] > 0.0 and future_weather_aver_dic["precipProbability"] == 0.0:
        result = 'Осадки прекратятся'
    elif past_weather_aver_dic["precipProbability"] == 0.0 and future_weather_aver_dic["precipProbability"] > 0.0:
        if future_weather_aver_dic["precipIntensity"] > config.precipintens_delta:
            result = 'Будут интенсивные осадки'
        else:
            result = 'Будут осадки слабой интенсивности'

    avr_temp_delta = round(future_weather_aver_dic["apparentTemperature"] - past_weather_aver_dic["apparentTemperature"], 0)
    if avr_temp_delta > config.temp_delta:
        result = 'Потеплеет на {} градуса'.format(avr_temp_delta)
    elif avr_temp_delta < -config.temp_delta:
        result = 'Похолодает на {} градуса'.format(-avr_temp_delta)

    return result





