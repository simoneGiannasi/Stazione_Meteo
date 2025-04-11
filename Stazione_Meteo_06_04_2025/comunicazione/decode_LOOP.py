def decode_loop_packet(data):
    """
    Decode a LOOP packet from a Davis Vantage weather station.
    
    Args:
        data: The data received from the station, including the ACK byte
        
    Returns:
        A dictionary containing the decoded weather data
    """
    # Skip the ACK (0x06) response byte
    if data[0] == 0x06:
        data = data[1:]
    
    # Ensure we have a complete packet (99 bytes)
    if len(data) < 99:
        raise ValueError(f"Incomplete LOOP packet: {len(data)} bytes, expected 99")
    
    # Check for 'LOO' at the start of the packet
    if data[0:3] != b'LOO':
        raise ValueError("Invalid LOOP packet: does not start with 'LOO'")
    
    # Create the result dictionary
    result = {}
    
    # Bar trend (Rev B) or 'P' (Rev A)
    bar_trend_byte = data[3]
    if bar_trend_byte == ord('P'):
        result['bar_trend'] = 'Rev A (no trend)'
    elif bar_trend_byte == 196:  # -60 as unsigned byte (Falling Rapidly)
        result['bar_trend'] = 'Falling Rapidly'
    elif bar_trend_byte == 236:  # -20 as unsigned byte (Falling Slowly)
        result['bar_trend'] = 'Falling Slowly'
    elif bar_trend_byte == 0:
        result['bar_trend'] = 'Steady'
    elif bar_trend_byte == 20:
        result['bar_trend'] = 'Rising Slowly'
    elif bar_trend_byte == 60:
        result['bar_trend'] = 'Rising Rapidly'
    else:
        result['bar_trend'] = f'Unknown ({bar_trend_byte})'
    
    # Packet type (0 for LOOP, 1 for LOOP2)
    result['packet_type'] = data[4]
    
    # Next record position
    result['next_record'] = data[5] + (data[6] << 8)
    
    # Barometer value (inches of Hg / 1000)
    result['barometer'] = (data[7] + (data[8] << 8)) / 1000.0
    
    # Inside temperature (°F / 10)
    inside_temp = data[9] + (data[10] << 8)
    if inside_temp != 32767:  # Not dashed
        result['inside_temp'] = inside_temp / 10.0
    
    # Inside humidity (%)
    if data[11] != 255:  # Not dashed
        result['inside_humidity'] = data[11]
    
    # Outside temperature (°F / 10)
    outside_temp = data[12] + (data[13] << 8)
    if outside_temp != 32767:  # Not dashed
        result['outside_temp'] = outside_temp / 10.0
    
    # Wind speed (mph)
    result['wind_speed'] = data[14]
    
    # 10-min average wind speed (mph)
    if data[15] != 255:  # Not dashed
        result['wind_speed_10min_avg'] = data[15]
    
    # Wind direction (0-360°)
    wind_dir = data[16] + (data[17] << 8)
    if wind_dir != 0:  # 0 means no data
        result['wind_direction'] = wind_dir
    
    # Extra temperatures (7 sensors)
    for i in range(7):
        if data[18 + i] != 255:  # Not dashed
            result[f'extra_temp_{i+1}'] = data[18 + i] - 90
    
    # Soil temperatures (4 sensors)
    for i in range(4):
        if data[25 + i] != 255:  # Not dashed
            result[f'soil_temp_{i+1}'] = data[25 + i] - 90
    
    # Leaf temperatures (4 sensors)
    for i in range(4):
        if data[29 + i] != 255:  # Not dashed
            result[f'leaf_temp_{i+1}'] = data[29 + i] - 90
    
    # Outside humidity (%)
    if data[33] != 255:  # Not dashed
        result['outside_humidity'] = data[33]
    
    # Extra humidities (7 sensors)
    for i in range(7):
        if data[34 + i] != 255:  # Not dashed
            result[f'extra_humidity_{i+1}'] = data[34 + i]
    
    # Rain rate (clicks per hour, 0.01in or 0.2mm per click)
    result['rain_rate'] = data[41] + (data[42] << 8)
    
    # UV index
    if data[43] != 255:  # Not dashed
        result['uv_index'] = data[43]
    
    # Solar radiation (W/m²)
    solar_rad = data[44] + (data[45] << 8)
    if solar_rad != 32767:  # Not dashed
        result['solar_radiation'] = solar_rad
    
    # Storm rain (0.01in or 0.2mm)
    result['storm_rain'] = (data[46] + (data[47] << 8)) / 100.0
    
    # Start date of current storm
    date_stamp = data[48] + (data[49] << 8)
    if date_stamp != 0:
        month = (date_stamp & 0xF000) >> 12
        day = (date_stamp & 0x0F80) >> 7
        year = 2000 + (date_stamp & 0x007F)
        result['storm_start_date'] = f"{year:04d}-{month:02d}-{day:02d}"
    
    # Day rain, month rain, year rain (0.01in or 0.2mm)
    result['day_rain'] = (data[50] + (data[51] << 8)) / 100.0
    result['month_rain'] = (data[52] + (data[53] << 8)) / 100.0
    result['year_rain'] = (data[54] + (data[55] << 8)) / 100.0
    
    # Day ET, month ET, year ET (1/1000 inch)
    result['day_et'] = (data[56] + (data[57] << 8)) / 1000.0
    result['month_et'] = (data[58] + (data[59] << 8)) / 100.0
    result['year_et'] = (data[60] + (data[61] << 8)) / 100.0
    
    # Soil moistures (4 sensors, centibar)
    for i in range(4):
        if data[62 + i] != 255:  # Not dashed
            result[f'soil_moisture_{i+1}'] = data[62 + i]
    
    # Leaf wetnesses (4 sensors, 0-15)
    for i in range(4):
        if data[66 + i] != 255:  # Not dashed
            result[f'leaf_wetness_{i+1}'] = data[66 + i]
    
    # Alarm bytes
    result['inside_alarms'] = data[70]
    result['rain_alarms'] = data[71]
    result['outside_alarms'] = data[72] + (data[73] << 8)
    
    # Extra temp/hum alarms (8 bytes)
    #result['extra_temp_hum_alarms'] = data[74:82]   # Il tipo è byte e quindi non può essere serializzato in JSON
    
    # Soil & leaf alarms (4 bytes)
    #result['soil_leaf_alarms'] = data[82:86] # Il tipo è byte e quindi non può essere serializzato in JSON
    
    # Transmitter battery status
    result['transmitter_battery'] = data[86]
    
    # Console battery voltage
    result['console_battery'] = ((data[87] * 300) / 512.0) / 100.0
    
    # Forecast icons
    result['forecast_icons'] = data[89]
    result['forecast_rule'] = data[90]
    
    # Sunrise time (hour*100 + min)
    sunrise = data[91] + (data[92] << 8)
    result['sunrise'] = f"{sunrise//100:02d}:{sunrise%100:02d}"
    
    # Sunset time (hour*100 + min)
    sunset = data[93] + (data[94] << 8)
    result['sunset'] = f"{sunset//100:02d}:{sunset%100:02d}"
    

    # CRC (last two bytes, not included in result)
    
    return result