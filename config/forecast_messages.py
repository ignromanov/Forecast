from config import config


def current_weather(dp):
    return '''{emoji}\n 🌡️ {temp} C (ощущается как {apparent_temp} C), 
    ☁ {cloud}%'''.format(
        emoji=get_emoji_by_icon(dp.icon), temp=int(round(dp.temperature, 0)),
        apparent_temp=int(round(dp.apparentTemperature, 0)), cloud=int(round(dp.cloudCover, 2) * 100))


def get_emoji_by_icon(icon):
    if icon in config.weather_emoji_dic:
        return config.weather_emoji_dic[icon]
    else:
        return ''
