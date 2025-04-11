def get_weather_emoji_and_description(weather_data):
    temperatura = weather_data["temperatura"]
    precipitazione = weather_data["precipitazione"]
    velocita_media = weather_data["velocità media"]
    velocita_raffica = weather_data["velocità raffica"]
    umidita = weather_data["umidità"]
    pressione = weather_data["pressione"]
    
    vento_moderato = velocita_media > 20 #inizio a considerare solo una velocità media di 20 km/h
    forte_vento = velocita_media > 30 #vento forte
    vento_tempesta = velocita_media > 50 #vento da tempesta
    raffica_forte = velocita_raffica > 50 #raffica di vento forte
    raffica_tempesta = velocita_raffica > 70 #raffica tempesta
    
    molto_caldo = temperatura > 30 
    caldo = temperatura > 25
    mite = 15 <= temperatura <= 25
    fresco = 10 <= temperatura < 15
    freddo = 0 <= temperatura < 10
    molto_freddo = temperatura < 0
    
    piovoso = precipitazione > 0.1 #mm
    pioggia_moderata = precipitazione > 2
    forte_pioggia = precipitazione > 5
    temporale = precipitazione > 10
    
    alta_umidita = umidita > 80

    bassa_pressione = pressione < 1000
    alta_pressione = pressione > 1025

    #URAGANO E TEMPESTA
    
    if (vento_tempesta or raffica_tempesta) and temporale:
        return ("⛈️🌪️", "Tempesta violenta")
    
    if (vento_tempesta or raffica_tempesta) and piovoso and molto_freddo:
        return ("❄️🌪️", "Bufera di neve")
    
    if (vento_tempesta or raffica_tempesta):
        if piovoso:
            return ("🌪️🌧️", "Pioggia e tempesta")
        else:
            return ("🌪️", "Vento tempestoso")
        
    #NEVE

    if piovoso and -1 <= temperatura <= 1:
        if pioggia_moderata:
            return ("🌨️🌨️", "Neve moderata")
        elif forte_vento or raffica_forte:
            return ("🌨️💨", "Neve e vento")
        elif piovoso:
            return ("🌨️", "Neve leggera")
    
    if piovoso and molto_freddo:
        return ("🌨️❄️", "Neve intensa")
    
    #PIOGGIA
    
    #temporale
    if temporale:
        if bassa_pressione:
            return ("⛈️⚡", "Forte temporale")
        return ("⛈️", "Temporale")
    
    #forte pioggia
    if forte_pioggia:
        if forte_vento or raffica_forte:
            return ("🌧️💨", "Forte pioggia e vento")
        return ("🌧️", "Forte pioggia")
    
    #pioggia moderata
    if pioggia_moderata:
        return ("🌧️", "Pioggia moderata")
    
    #pioggia leggera
    if piovoso:
        if forte_vento or raffica_forte:
            return ("🌦️💨", "Pioggerella e vento")
        return ("🌦️", "Pioggerella")
    
    #VENTO
    
    #vento forte con raffiche
    if forte_vento and raffica_forte:
        if molto_caldo:
            return ("☀️🌪️", "Caldo e ventoso")
        elif caldo:
            return ("🌤️🌪️", "Vento caldo")
        elif mite:
            return ("🌥️🌪️", "Mite e ventoso")
        elif freddo:
            return ("☁️🌪️", "Freddo ventoso")
        elif molto_freddo:
            return ("❄️🌪️", "Gelo ventoso")
        else:
            return ("🌪️", "Vento forte")
    
    #vento forte
    if forte_vento:
        if molto_caldo:
            return ("☀️💨", "Caldo e ventoso")
        elif caldo:
            return ("🌤️💨", "Caldo ventilato")
        elif mite:
            return ("🌥️💨", "Mite e ventoso")
        elif freddo:
            return ("☁️💨", "Vento freddo")
        elif molto_freddo:
            return ("❄️💨", "Vento gelido")
        else:
            return ("💨", "Ventoso")
    
    #vento moderato o raffiche senza vento costante
    if vento_moderato or raffica_forte:
        if molto_caldo:
            return ("☀️🍃", "Caldo con brezza")
        elif caldo:
            return ("🌤️🍃", "Brezza calda")
        elif freddo:
            return ("☁️🍃", "Brezza fresca")
        elif molto_freddo:
            return ("❄️🍃", "Brezza gelida")
        else:
            return ("🍃", "Vento leggero")
    
    #TEMPERATURE ESTREME
    
    #caldo estremo
    if temperatura > 35:
        if alta_umidita:
            return ("🔥💦", "Afa intensa")
        return ("🔥", "Caldo estremo")
    
    #molto caldo
    if molto_caldo:
        if alta_umidita:
            return ("☀️💦", "Afoso e umido")
        elif alta_pressione:
            return ("☀️☀️", "Sole caldo")
        return ("☀️", "Caldo")
    
    #freddo estremo
    if temperatura < -10:
        return ("❄️❄️", "Gelo intenso")
    
    #molto freddo
    if molto_freddo:
        return ("❄️", "Gelido")
    
    #ALTRE CONDIZIONI
    
    #alta umidità
    if alta_umidita:
        if temperatura > 20:
            return ("🌫️💦", "Umido e afoso")
        return ("🌫️", "Umidità alta")
    
    #alta pressione (generalmente bel tempo)
    if alta_pressione:
        if caldo:
            return ("☀️", "Soleggiato")
        elif mite:
            return ("🌤️", "Bel tempo")
        else:
            return ("☀️❄️", "Sole e freddo")
    
    #bassa pressione (possibile instabilità)
    if bassa_pressione:
        return ("🌥️", "Tempo variabile")
    
    if caldo:
        return ("☀️", "Soleggiato")
    
    if mite:
        return ("🌤️", "Tempo gradevole")
    
    if fresco:
        return ("🌥️", "Fresco")
    
    if freddo:
        return ("☁️", "Nuvoloso e fresco")

# weather_data = {
#     'pressione': 1013, 
#     'temperatura': 35, 
#     'umidità': 65, 
#     'precipitazione': 0, 
#     'velocità media': 30, 
#     'velocità raffica': 20
# }
# emoji, description = get_weather_emoji_and_description(weather_data)
# print(f"{emoji} - {description}")