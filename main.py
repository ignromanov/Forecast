import forecastio, datetime, pytz

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5.0 / 9.0

def fill_time_to_data_dic(forecast_by_hours, datetime_beg, datetime_end):
    dic = {}
    for data_point in forecast_by_hours.data:
        data_point_time = data_point.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if datetime_beg <= data_point_time <= datetime_end:
            dic[data_point_time.hour] = data_point
            print("date {}, temperature {}".format(
                data_point_time.strftime('%Y-%m-%d %H:%M:%S %z %Z'),
                data_point.apparentTemperature))
    return dic


api_key = "cf20028a34237493da18f8cbadcc966d"
lat = 55.751244
lng = 37.618423

now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(minute=0, second=0, microsecond=0)
yesterday = now - datetime.timedelta(days=1)
tomorrow = now + datetime.timedelta(days=1)

print('past weather:')
past_weather_dic = fill_time_to_data_dic(
    forecastio.load_forecast(api_key, lat, lng, time=now).hourly(),
    now.replace(hour=7),
    now.replace(hour=23))

print('forecast:')
future_weather_dic = fill_time_to_data_dic(
    forecastio.load_forecast(api_key, lat, lng).hourly(),
    tomorrow.replace(hour=7),
    tomorrow.replace(hour=23))

max_temp_delta = 4
max_precipintens_delta = 0.5
max_precipprob_delta = 0.5
temp_changed, precipprob_changed = False, False

temp_delta_dic, precipprob_delta_dic, precipintens_delta_dic = {}, {}, {}
for key in past_weather_dic.keys():
    temp_delta_dic[key] = future_weather_dic[key].apparentTemperature - past_weather_dic[key].apparentTemperature
    precipprob_delta_dic[key] = future_weather_dic[key].precipProbability - past_weather_dic[key].precipProbability
    precipintens_delta_dic[key] = future_weather_dic[key].precipIntensity - past_weather_dic[key].precipIntensity
    print('time: {}, temp dif: {}, precipProb dif: {}, precipIntens dif: {}'.format(
        key,
        round(temp_delta_dic[key],1),
        round(precipprob_delta_dic[key],1),
        round(precipintens_delta_dic[key],1)))
    if abs(temp_delta_dic[key]) > max_temp_delta and not temp_changed:
        print('There is temperature change at {} from {} to {}'.format(
            key,
            past_weather_dic[key].apparentTemperature,
            future_weather_dic[key].apparentTemperature
        ))
        temp_changed = True






