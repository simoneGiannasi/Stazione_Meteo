def convert_data(data):
    # Conversione bar_trend in italiano
    trend_translation = {
        "Falling Rapidly": "In rapida diminuzione",
        "Falling Slowly": "In lenta diminuzione",
        "Steady": "Stabile",
        "Rising Slowly": "In lento aumento",
        "Rising Rapidly": "In rapido aumento"
    }
    data['bar_trend'] = trend_translation.get(data['bar_trend'], data['bar_trend'])

    # Conversione barometro da pollici di mercurio a hPa
    data['barometer'] = round(data['barometer'] * 33.8639, 2)

    # Conversione temperatura da Fahrenheit a Celsius
    data['inside_temp'] = round((data['inside_temp'] - 32) * 5/9, 1)
    try:
        data['outside_temp'] = round((data['outside_temp'] - 32) * 5/9, 1)
        gradi_vento = data['wind_direction']
        if (gradi_vento <68 and gradi_vento>22):
            data["wind_direction"]='NE'
        elif (gradi_vento <338 and gradi_vento>292):
            data["wind_direction"]='NO'
        elif (gradi_vento <158 and gradi_vento>112):
            data["wind_direction"]='SE'
        elif (gradi_vento <248 and gradi_vento>202):
            data["wind_direction"]='SO'
        elif (gradi_vento <=112 and gradi_vento>=68):
            data["wind_direction"]='E'
        elif (gradi_vento <=202 and gradi_vento>=158):
            data["wind_direction"]='S'
        elif (gradi_vento <=292 and gradi_vento>=248):
            data["wind_direction"]='O'
        elif (gradi_vento <=22 or gradi_vento>=338):
            data["wind_direction"]='N'

        #print(f"Direzione vento: {data['wind_direction']}")
    except:
        data['outside_temp'] = 0
        data['wind_direction'] = '0'


   

    # Formula per il wind chill
    # T_wc = 13.12 + 0.6215 *temperature - 11.37 * (wind_speed ** 0.16) + 0.3965 * temperature * (wind_speed ** 0.16)

    return data